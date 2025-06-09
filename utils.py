# utils.py

def normalise_input(text):
    text = text.lower().replace('-', ' ').replace('–', ' ')
    return ' '.join(text.split())

def expand_phrases(query, phrase_map):
    expansions = [query]
    for key, values in phrase_map.items():
        if query == key or query in values:
            expansions.extend([key] + values)
    return list(set(expansions))

def classify_intent(query):
    q = query.lower()
    if q.startswith("how "): return "how"
    if q.startswith("why "): return "why"
    if q.startswith("what "): return "what"
    if q.startswith("where "): return "where"
    if q.startswith("when "): return "when"
    return "general"
