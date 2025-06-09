import json
import os

# Load phrase_map.json once when the app starts
PHRASE_MAP_PATH = os.path.join("data", "phrase_map.json")
if os.path.exists(PHRASE_MAP_PATH):
    with open(PHRASE_MAP_PATH, "r") as file:
        PHRASE_MAP = json.load(file)
else:
    PHRASE_MAP = {}

def rewrite_with_phrase_map(user_input, phrase_map=PHRASE_MAP):
    """
    Rewrites a user query using known typo/abbreviation/variant mappings.

    Returns a list of rewritten phrases that can be used for better matching.
    """
    rewritten = []
    cleaned_input = user_input.strip().lower()

    # Always include the original query
    rewritten.append(cleaned_input)

    # Check phrase map for possible rewrites
    for key, variants in phrase_map.items():
        for variant in variants:
            if variant.lower() in cleaned_input and key.lower() not in cleaned_input:
                rewritten.append(cleaned_input.replace(variant.lower(), key.lower()))

    # Remove duplicates
    rewritten = list(set(rewritten))

    return rewritten
