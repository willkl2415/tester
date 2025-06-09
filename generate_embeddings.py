import os
import json
import openai
from tqdm import tqdm

openai.api_key = os.getenv("OPENAI_API_KEY")

def embed(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text,
    )
    return response["data"][0]["embedding"]

def load_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chunks(chunks, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

def main():
    input_path = "data/chunks.json"
    output_path = "data/chunks_with_vectors.json"
    chunks = load_chunks(input_path)
    print(f"Embedding {len(chunks)} chunks...")

    for chunk in tqdm(chunks):
        content = chunk.get("content", "")
        try:
            chunk["vector"] = embed(content[:500])
        except Exception as e:
            print(f"⚠️ Embedding failed for chunk: {e}")
            chunk["vector"] = []

    save_chunks(chunks, output_path)
    print(f"✅ Embeddings saved to {output_path}")

if __name__ == "__main__":
    main()
