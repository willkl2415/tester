# answer_engine.py
import json
import tiktoken
from rapidfuzz import fuzz
from preprocess_pipeline import clean_text
from utils import normalise_input, expand_phrases

with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

with open("data/phrase_map.json", "r", encoding="utf-8") as f:
    phrase_map = json.load(f)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def num_tokens_from_string(string: str) -> int:
    return len(encoding.encode(string))

def get_answer(question, chunks_subset):
    if not question:
        return []

    normalised = normalise_input(question)
    expanded_phrases = expand_phrases(normalised, phrase_map)

    results = []
    for chunk in chunks_subset:
        chunk_text = clean_text(chunk["content"])
        for phrase in expanded_phrases:
            if fuzz.partial_ratio(phrase, chunk_text.lower()) >= 85:
                results.append(chunk)
                break

    return results