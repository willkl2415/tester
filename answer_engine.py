# answer_engine.py

import json
import os
import re
import numpy as np
import tiktoken
from sklearn.metrics.pairwise import cosine_similarity
import openai
from utils import normalise_input

# Load OpenAI key
openai = OpenAI()

# Load vectorised chunks
with open("data/chunks_with_vectors.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Load phrase map
with open("data/phrase_map.json", "r", encoding="utf-8") as f:
    phrase_map = json.load(f)

# Priority weightings
PRIORITY_WEIGHTS = {
    "JSP 822": 5.0,
    "DTSM": 4.0,
    "JSP": 3.0,
    "DEF": 2.0,
    "OTHER": 1.0,
}

def get_doc_priority(doc_name):
    doc_name = doc_name.upper()
    if "JSP 822" in doc_name:
        return PRIORITY_WEIGHTS["JSP 822"]
    elif doc_name.startswith("DTSM"):
        return PRIORITY_WEIGHTS["DTSM"]
    elif "JSP" in doc_name:
        return PRIORITY_WEIGHTS["JSP"]
    elif any(x in doc_name for x in ["MATG", "HUMAN FACTORS", "SKILL FADE", "HF", "DEF STANDARDS", "MARITIME"]):
        return PRIORITY_WEIGHTS["DEF"]
    return PRIORITY_WEIGHTS["OTHER"]

def embed_query(query):
    response = openai.embeddings.create(
        input=[query],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def semantic_search(query, chunks, top_n=10):
    query_vec = np.array(embed_query(query)).reshape(1, -1)

    results = []
    for chunk in chunks:
        chunk_vec = np.array(chunk["vector"]).reshape(1, -1)
        score = cosine_similarity(query_vec, chunk_vec)[0][0]
        priority = get_doc_priority(chunk["document"])
        weighted_score = score * priority
        chunk["score"] = round(score, 3)
        chunk["priority"] = priority
        chunk["weighted_score"] = round(weighted_score, 3)
        results.append(chunk)

    sorted_results = sorted(results, key=lambda x: x["weighted_score"], reverse=True)
    return sorted_results[:top_n]

def classic_search(query, chunks):
    query = normalise_input(query)
    matches = []

    for chunk in chunks:
        content = normalise_input(chunk["content"])
        if query in content:
            chunk["score"] = None
            matches.append(chunk)

    return matches

def get_answer(user_input, chunks):
    from rewrite_query import rewrite_with_phrase_map

    variants = rewrite_with_phrase_map(user_input)
    normalised_variants = [normalise_input(v) for v in variants]
    base_query = normalise_input(user_input)

    # Detect if it's a classic keyword match
    if any(len(v.split()) == 1 for v in normalised_variants):
        print(f"🔁 Using Classic Engine for query: {user_input}")
        print(f"🔁 [Classic Match Triggered]")
        print(f"→ Variants: {normalised_variants}")
        return classic_search(base_query, chunks)

    print(f"🧠 Using Semantic Engine for query: {user_input}")
    print(f"🔍 [Semantic Engine Triggered]")
    print(f"→ Variants: {normalised_variants}")
    intent = detect_question_type(base_query)
    print(f"→ Intent: {intent}")

    return semantic_search(base_query, chunks, top_n=25)

def detect_question_type(text):
    q = text.strip().lower()
    if q.startswith("what"): return "what"
    if q.startswith("how"): return "how"
    if q.startswith("why"): return "why"
    if q.startswith("when"): return "when"
    if q.startswith("who"): return "who"
    if q.startswith("where"): return "where"
    return "general"

def get_semantic_answer(user_input, chunks):
    return semantic_search(user_input, chunks, top_n=25)
