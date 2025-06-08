# rewrite_query.py
import json
import os
from rapidfuzz import fuzz

# Load phrase mapping
PHRASE_MAP_PATH = os.path.join("data", "phrase_map.json")

if os.path.exists(PHRASE_MAP_PATH):
    with open(PHRASE_MAP_PATH, "r", encoding="utf-8") as f:
        phrase_map = json.load(f)
else:
    phrase_map = {}

def rewrite_with_phrase_map(query):
    threshold = 80  # minimum similarity %
    rewritten_query = query

    for key in phrase_map:
        score = fuzz.partial_ratio(query.lower(), key.lower())
        if score >= threshold:
            rewritten_query = phrase_map[key]
            break

    return rewritten_query.lower()
