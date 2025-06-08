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