# answer_engine.py
import json
from preprocess_pipeline import clean_text
from rewrite_query import rewrite_with_phrase_map

# Load chunks
with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

def get_answer(question, chunks_subset):
    if not question:
        return []

    question_original = question.strip().lower()
    question_rewritten = rewrite_with_phrase_map(question_original)

    results = []

    for chunk in chunks_subset:
        chunk_text = clean_text(chunk["content"]).lower()
        if (
            question_original in chunk_text
            or question_rewritten in chunk_text
        ):
            results.append(chunk)

    return results
