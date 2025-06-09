import json
import os
import openai
from rapidfuzz import fuzz
from rewrite_query import rewrite_with_phrase_map
from utils import classify_intent

# Load all chunks
def load_chunks():
    with open("data/chunks.json", "r", encoding="utf-8") as f:
        return json.load(f)

chunks = load_chunks()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Embed with OpenAI
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

# Semantic Match Engine (Enhanced)
def get_semantic_answer(query, chunks):
    print("\n🔍 [Semantic Engine Triggered]")
    variations = rewrite_with_phrase_map(query)
    best_variant = variations[0]
    print(f"Query Variations: {variations}")
    intent = classify_intent(best_variant)
    print(f"Detected Intent: {intent}")
    query_vector = embed(best_variant)

    results = []
    for chunk in chunks:
        content = chunk.get("content", "")
        base_score = max(fuzz.partial_ratio(v.lower(), content.lower()) for v in variations) / 100.0

        try:
            chunk_vector = embed(content[:500])
            emb_score = cosine_similarity(query_vector, chunk_vector)
        except Exception:
            emb_score = 0

        total_score = round((0.5 * base_score) + (0.4 * emb_score), 4)
        if total_score > 0:
            print(f"→ Score: {total_score:.4f} | Match: {content[:80]}...")
            results.append({
                "score": total_score,
                "reason": f"Intent: {intent}, semantic + phrase match",
                "content": content,
                "section": chunk.get("section", "Uncategorised"),
                "document": chunk.get("document", "Unknown")
            })

    return sorted(results, key=lambda x: x["score"], reverse=True)

# Classic Match Engine (Phrase only)
def get_answer(query, chunks):
    print("\n🔁 [Classic Match Engine Triggered]")
    variations = rewrite_with_phrase_map(query)
    print(f"Query Variations: {variations}")

    results = []
    for chunk in chunks:
        content = chunk.get("content", "")
        for v in variations:
            if v in content.lower():
                print(f"→ Matched: {v} in: {content[:80]}...")
                results.append({
                    "score": 1.0,
                    "reason": f"Matched variant: {v}",
                    "content": content,
                    "section": chunk.get("section", "Uncategorised"),
                    "document": chunk.get("document", "Unknown")
                })
                break

    return results
