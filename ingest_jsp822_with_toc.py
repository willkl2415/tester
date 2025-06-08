import os
import re
import uuid
import json
from docx import Document
from pathlib import Path

# File paths
docx_path = Path("docs/JSP 822 V7.0 Vol 2 V3.0 Defence Individual Training.docx")
toc_map_path = Path("data/toc_map.json")
output_path = Path("data/chunks.json")

# Load Table of Contents mapping
with open(toc_map_path, "r", encoding="utf-8") as f:
    toc_map = json.load(f)

toc_sections = toc_map.get(docx_path.name, [])
toc_patterns = [(section, re.compile(rf"^{re.escape(section)}\b", re.IGNORECASE)) for section in toc_sections]

def match_to_toc_section(text):
    for section_title, pattern in toc_patterns:
        if pattern.match(text.strip()):
            return section_title
    return None

def extract_chunks(docx_path):
    doc = Document(docx_path)
    chunks = []
    buffer = []
    current_section = "Uncategorised"

    def flush_buffer():
        nonlocal buffer, current_section
        while buffer:
            chunk_paras = buffer[:3]
            buffer[:3] = []
            chunks.append({
                "id": str(uuid.uuid4()),
                "document": docx_path.name,
                "section": current_section,
                "content": " ".join(chunk_paras).strip()
            })

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        match = match_to_toc_section(text)
        if match:
            flush_buffer()
            current_section = match
        buffer.append(text)

    flush_buffer()
    return chunks

# Process and save
chunks = extract_chunks(docx_path)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

