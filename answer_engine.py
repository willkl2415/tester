import json
import os
import re
from openai import OpenAI
from rapidfuzz import fuzz
from rewrite_query import apply_phrase_map
from utils import classify_intent

client = OpenAI()

def load_chunks():
    with open("data/chunks.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_phrase_map():
    with open("data/phrase_map.json", "r", encoding="utf-8") as f:
        return json.load(f)

def embed(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
    )
    return response.data[0].embedding

def cosine_similarity(v1, v2):
    import numpy as np
    v1, v2 = np.array(v1), np.array(v2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

def semantic_match(query, chunks, use_embedding=True, co_terms=None):
    phrase_map = load_phrase_map()
    query_rewritten = apply_phrase_map(query, phrase_map)
    intent = classify_intent(query_rewritten)

    if use_embedding:
        query_vector = embed(query_rewritten)

    scored = []
    for chunk in chunks:
        content = chunk.get("content", "")
        base_score = fuzz.partial_ratio(query_rewritten.lower(), content.lower()) / 100.0
        co_score = 0
        if co_terms:
            co_score = sum(1 for term in co_terms if term.lower() in content.lower()) * 0.05
        emb_score = 0
        if use_embedding:
            chunk_vector = embed(content[:500])  # avoid token overrun
            emb_score = cosine_similarity(query_vector, chunk_vector)

        total_score = round(0.5 * base_score + 0.4 * emb_score + co_score, 4)
        scored.append({
            "score": total_score,
            "reason": f"Intent: {intent}, phrase match + embedding + co-occurrence",
            "content": content,
            "section": chunk.get("section", "Uncategorised"),
            "document": chunk.get("document", "Unknown")
        })

    return sorted(scored, key=lambda x: x["score"], reverse=True)[:10]
