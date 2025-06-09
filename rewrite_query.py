import json
import os

PHRASE_MAP_PATH = os.path.join("data", "phrase_map.json")
if os.path.exists(PHRASE_MAP_PATH):
    with open(PHRASE_MAP_PATH, "r") as file:
        PHRASE_MAP = json.load(file)
else:
    PHRASE_MAP = {}

def rewrite_with_phrase_map(user_input, phrase_map=PHRASE_MAP):
    """
    Returns a list of rewritten query variations including corrections.
    """
    rewritten = set()
    cleaned_input = user_input.strip().lower()
    rewritten.add(cleaned_input)

    for correct_term, variants in phrase_map.items():
        for variant in variants:
            variant_lower = variant.lower()
            if variant_lower in cleaned_input and correct_term.lower() not in cleaned_input:
                updated = cleaned_input.replace(variant_lower, correct_term.lower())
                rewritten.add(updated)

    return list(rewritten)
