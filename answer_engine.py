# answer_engine.py
import json
import tiktoken
from preprocess_pipeline import clean_text
from rewrite_query import rewrite_with_phrase_map

# Load chunks
with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def num_tokens_from_string(string: str) -> int:
    return len(encoding.encode(string))

def get_answer(question, chunks_subset):
    if not question:
        return []

    question = question.strip().lower()

    # Try to rewrite the question using the phrase map
    try:
        rewritten = rewrite_with_phrase_map(question)
    except Exception as e:
        rewritten = question  # fail gracefully

    results = []

    for chunk in chunks_subset:
        chunk_text = clean_text(chunk["content"])
        if rewritten in chunk_text.lower() or question in chunk_text.lower():
            results.append(chunk)

    return results
