import json
from rapidfuzz import fuzz
from rewrite_query import rewrite_user_query

def get_answer(user_input, chunks, top_n=25):
    rewritten_query = rewrite_user_query(user_input)
    matches = []

    for chunk in chunks:
        score = fuzz.token_set_ratio(rewritten_query.lower(), chunk["text"].lower())
        if score > 50:
            matches.append({**chunk, "score": score})

    sorted_matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:top_n]

    if sorted_matches:
        answer = sorted_matches[0]["text"]
    else:
        answer = "No relevant information found. Try rephrasing your question."

    return answer, sorted_matches
