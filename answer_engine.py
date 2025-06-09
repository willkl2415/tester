# answer_engine.py
import json
import tiktoken
from preprocess_pipeline import clean_text
from rewrite_query import rewrite_query

# Load chunks
with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def num_tokens_from_string(string: str) -> int:
    return len(encoding.encode(string))

def get_answer(question, chunks_subset):
    if not question:
        return []

    rewritten_queries = rewrite_query(question)

    # Ensure the rewritten_queries is a list
    if isinstance(rewritten_queries, str):
        rewritten_queries = [rewritten_queries]

    results = []
    for chunk in chunks_subset:
        chunk_text = clean_text(chunk["content"]).lower()

        for rewritten in rewritten_queries:
            if rewritten.lower() in chunk_text:
                results.append(chunk)
                break  # Avoid duplicate entries from multiple matches

    return results
