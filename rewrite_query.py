import json
import os
from rapidfuzz import fuzz

# Load phrase map
with open("data/phrase_map.json", "r", encoding="utf-8") as f:
    phrase_map = json.load(f)

def rewrite_with_phrase_map(original_query):
    if not isinstance(original_query, str):
        return original_query  # fallback to original if not string

    query_lower = original_query.lower()

    best_match = None
    best_score = 0

    for alt, canonical in phrase_map.items():
        score = fuzz.partial_ratio(query_lower, alt.lower())
        if score > best_score:
            best_score = score
            best_match = canonical

    if best_score >= 80:
        return best_match
    else:
        return original_query
