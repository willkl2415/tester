import json
import os
from openai import OpenAI
from rapidfuzz import fuzz
from rewrite_query import rewrite_with_phrase_map
from utils import classify_intent

client = OpenAI()

def load_chunks():
    with open("data/chunks.json", "r", encoding="utf-8") as f:
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

def get_semantic_answer(query, chunks, use_embedding=True, co_terms=None):
    variations = rewrite_with_phrase_map(query)
    best_variant = variations[0]  # you can expand this logic to rank variants
    intent = classify_intent(best_variant)

    if use_embedding:
        query_vector = embed(best_variant)

    scored = []
    for chunk in chunks:
        content = chunk.get("content", "")
        base_score = max(fuzz.partial_ratio(v.lower(), content.lower()) for v in variations) / 100.0
        co_score = 0
        if co_terms:
            co_score = sum(1 for term in co_terms if term.lower() in content.lower()) * 0.05
        emb_score = 0
        if use_embedding:
            chunk_vector = embed(content[:500])
            emb_score = cosine_similarity(query_vector, chunk_vector)

        total_score = round(0.5 * base_score + 0.4 * emb_score + co_score, 4)
        scored.append({
            "score": total_score,
            "reason": f"Intent: {intent}, variant match + embedding + co-occurrence",
            "content": content,
            "section": chunk.get("section", "Uncategorised"),
            "document": chunk.get("document", "Unknown")
        })

    return sorted(scored, key=lambda x: x["score"], reverse=True)[:10]

def get_answer(query, chunks):
    variations = rewrite_with_phrase_map(query)
    results = []
    for chunk in chunks:
        for v in variations:
            if v in chunk["content"].lower():
                results.append({
                    "score": 1.0,
                    "reason": f"Matched variant: {v}",
                    "content": chunk["content"],
                    "section": chunk.get("section", "Uncategorised"),
                    "document": chunk.get("document", "Unknown")
                })
                break
    return sorted(results, key=lambda x: x["score"], reverse=True)[:10]
