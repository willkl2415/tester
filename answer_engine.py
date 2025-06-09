# answer_engine.py
import json
import tiktoken
from preprocess_pipeline import clean_text
from rewrite_query import rewrite_with_phrase_map as rewrite_query

# Load chunks
with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

# Load phrase map
with open("data/phrase_map.json", "r", encoding="utf-8") as f:
    phrase_map = json.load(f)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def num_tokens_from_string(string: str) -> int:
    return len(encoding.encode(string))

def get_answer(question, chunks_subset):
    if not question:
        return []

    # Handle input as string only
    if isinstance(question, list):
        question = question[0]
    question = question.strip()

    rewritten_phrases = rewrite_query(question, phrase_map)
    results = []

    for chunk in chunks_subset:
        chunk_text = clean_text(chunk["content"])
        for phrase in rewritten_phrases:
            if phrase.lower() in chunk_text.lower():
                results.append(chunk)
                break

    return results
