import json
import os

# Load phrase map
phrase_map_path = os.path.join("data", "phrase_map.json")
if os.path.exists(phrase_map_path):
    with open(phrase_map_path, "r", encoding="utf-8") as f:
        phrase_map = json.load(f)
else:
    phrase_map = {}

def rewrite_query(original_query):
    """
    Accepts a raw query string, splits it into words, and replaces
    known phrases or typos using the phrase_map dictionary.
    Returns a list of possible rewritten queries including the original.
    """
    if not isinstance(original_query, str):
        return [original_query]

    words = original_query.strip().lower().split()
    rewritten_words = []

    for word in words:
        if word in phrase_map:
            replacement = phrase_map[word]
            rewritten_words.append(replacement)
        else:
            rewritten_words.append(word)

    rewritten_query = " ".join(rewritten_words)

    # Always include original query too
    if rewritten_query != original_query:
        return [rewritten_query, original_query]
    else:
        return [original_query]
