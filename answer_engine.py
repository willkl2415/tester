import json
import os
import openai
from rapidfuzz import fuzz
from rewrite_query import rewrite_with_phrase_map
from utils import classify_intent

# Load chunks once
def load_chunks():
    with open("data/chunks.json", "r", encoding="utf-8") as f:
        return json.load(f)

chunks = load_chunks()

# OpenAI legacy API key auth
openai.api_key = os.getenv("OPENAI_API_KEY")

# Embedding helper
def embed(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text,
    )
    return response["data"][0]["embedding"]

# Cosine similarity
def cosine_similarity(v1, v2):
    import numpy as np
    v1, v2 = np.array(v1), np.array(v2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

# Semantic + phrase + co-occurrence engine
def get_semantic_answer(query, chunks):
    print("🔍 Semantic Engine Triggered")

    variations = rewrite_with_phrase_map(query)
    best_variant = variations[0]
    intent = classify_intent(best_variant)
    query_vector = embed(best_variant)

    results = []
    for chunk in chunks:
        content = chunk.get("content", "")
        base_score = max(fuzz.partial_ratio(v.lower(), content.lower()) for v in variations) / 100.0

        emb_score = 0
        try:
            chunk_vector = embed(content[:500])
            emb_score = cosine_similarity(query_vector, chunk_vector)
        except Exception:
            pass  # Safely ignore embedding failures

        total_score = round((0.5 * base_score) + (0.4 * emb_score), 4)
        if total_score > 0.3:  # Filter noise
            results.append({
                "score": total_score,
                "reason": f"Intent: {intent}, match via semantic + token",
                "content": content,
                "section": chunk.get("section", "Uncategorised"),
                "document": chunk.get("document", "Unknown")
            })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:10]

# Fallback classic phrase/variant match
def get_answer(query, chunks):
    print("🔁 Classic Match Engine Triggered")

    variations = rewrite_with_phrase_map(query)
    results = []
    for chunk in chunks:
        content = chunk.get("content", "")
        for variant in variations:
            if variant in content.lower():
                results.append({
                    "score": 1.0,
                    "reason": f"Matched variant: {variant}",
                    "content": content,
                    "section": chunk.get("section", "Uncategorised"),
                    "document": chunk.get("document", "Unknown")
                })
                break

    return sorted(results, key=lambda x: x["score"], reverse=True)[:10]
