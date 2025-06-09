import os
import json
import numpy as np
from rapidfuzz import fuzz
from rewrite_query import rewrite_with_phrase_map
from utils import classify_intent

# Load chunks with precomputed vectors
def load_chunks_with_vectors():
    with open("data/chunks_with_vectors.json", "r", encoding="utf-8") as f:
        return json.load(f)

chunks = load_chunks_with_vectors()

# Load OpenAI key (only needed for query embedding)
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text,
    )
    return response["data"][0]["embedding"]

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    if len(v1) != len(v2) or not np.any(v1) or not np.any(v2):
        return 0
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

# Combined semantic + fuzzy engine using precomputed vectors
def get_semantic_answer(query, chunks):
    print("\n🔍 [Precomputed Semantic Engine Triggered]")

    variations = rewrite_with_phrase_map(query)
    best_variant = variations[0]
    print(f"→ Variants: {variations}")
    intent = classify_intent(best_variant)
    print(f"→ Intent: {intent}")

    try:
        query_vector = embed(best_variant)
    except Exception as e:
        print(f"⚠️ Embedding failed: {e}")
        return get_answer(query, chunks)

    results = []
    for chunk in chunks:
        content = chunk.get("content", "")
        base_score = max(fuzz.partial_ratio(v.lower(), content.lower()) for v in variations) / 100.0
        emb_score = 0

        if "vector" in chunk and chunk["vector"]:
            try:
                chunk_vector = chunk["vector"]
                emb_score = cosine_similarity(query_vector, chunk_vector)
            except Exception:
                emb_score = 0

        total_score = round((0.5 * base_score) + (0.4 * emb_score), 4)

        if total_score > 0:
            results.append({
                "score": total_score,
                "reason": f"Intent: {intent}, fuzzy + precomputed vector match",
                "content": content,
                "section": chunk.get("section", "Uncategorised"),
                "document": chunk.get("document", "Unknown")
            })

    if not results:
        print("⚠️ No semantic results — fallback to classic")
        return get_answer(query, chunks)

    return sorted(results, key=lambda x: x["score"], reverse=True)

# Fallback classic engine
def get_answer(query, chunks):
    print("\n🔁 [Classic Match Triggered]")
    variations = rewrite_with_phrase_map(query)
    print(f"→ Variants: {variations}")

    results = []
    for chunk in chunks:
        content = chunk.get("content", "")
        for v in variations:
            if v in content.lower():
                results.append({
                    "score": 1.0,
                    "reason": f"Matched variant: {v}",
                    "content": content,
                    "section": chunk.get("section", "Uncategorised"),
                    "document": chunk.get("document", "Unknown")
                })
                break

    return sorted(results, key=lambda x: x["score"], reverse=True)
