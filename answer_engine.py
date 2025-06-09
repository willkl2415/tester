import json
import tiktoken
from preprocess_pipeline import clean_text
from rewrite_query import rewrite_with_phrase_map
from rapidfuzz import fuzz

with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def num_tokens_from_string(string: str) -> int:
    return len(encoding.encode(string))

def get_answer(question, chunks_subset):
    if not question:
        return []

    variations = rewrite_with_phrase_map(question)
    matches = []

    for chunk in chunks_subset:
        chunk_text = clean_text(chunk["content"]).lower()
        for phrase in variations:
            phrase = phrase.lower().strip()
            if phrase in chunk_text or fuzz.partial_ratio(phrase, chunk_text) > 80:
                matches.append(chunk)
                break

    return matches
