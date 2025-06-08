# ingest.py

import os
import json
import uuid
import re
from docx import Document

# Load TOC map
with open("data/toc_map.json", "r", encoding="utf-8") as f:
    toc_map = json.load(f)

def clean_text(text):
    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove footnote-style numbers, e.g., '16', '17' that appear mid-paragraph or following line breaks
    text = re.sub(r"\n{1,2}\d{1,3}\b", "", text)  # footnotes like \n\n16 or \n17
    text = re.sub(r"\s\d{1,3}\b", "", text)  # footnotes like "training 17" when misformatted

    return text.strip()

def extract_text_from_docx(path):
    doc = Document(path)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    return "\n".join(full_text)

def split_into_chunks(text, max_chunk_size=1000):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def get_section_for_text(text, toc_entries):
    for section in toc_entries:
        # Match section if it appears at the start of the chunk
        pattern = rf"\b{re.escape(section)}\b"
        if re.search(pattern, text):
            return section
    return "Uncategorised"

def process_file(filepath):
    filename = os.path.basename(filepath)
    document_title = filename
    toc_entries = toc_map.get(document_title, [])

    # Extract and clean text
    if filepath.endswith(".docx"):
        raw_text = extract_text_from_docx(filepath)
    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
    else:
        print(f"Skipping unsupported file format: {filepath}")
        return []

    raw_text = clean_text(raw_text)
    chunks = split_into_chunks(raw_text)

    processed = []
    for chunk in chunks:
        entry = {
            "id": str(uuid.uuid4()),
            "document": document_title,
            "section": get_section_for_text(chunk, toc_entries),
            "content": chunk
        }
        processed.append(entry)

    return processed

def main():
    source_dir = "docs"
    all_chunks = []

    for filename in os.listdir(source_dir):
        if filename.endswith(".docx") or filename.endswith(".txt"):
            print(f"Processing: {filename}")
            chunks = process_file(os.path.join(source_dir, filename))
            all_chunks.extend(chunks)

    output_path = "data/chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"Written {len(all_chunks)} chunks to {output_path}")

if __name__ == "__main__":
    main()
