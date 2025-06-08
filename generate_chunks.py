import os
import re
import json
import uuid
import docx
from docx.table import _Cell
from docx.text.paragraph import Paragraph
from bs4 import BeautifulSoup

# Load existing chunks if available
chunks_file = "data/chunks.json"
if os.path.exists(chunks_file):
    with open(chunks_file, "r", encoding="utf-8") as f:
        existing_chunks = json.load(f)
else:
    existing_chunks = []

existing_ids = {chunk["id"] for chunk in existing_chunks}
existing_files = {chunk["document"] for chunk in existing_chunks}

def clean_text(text):
    return BeautifulSoup(text, "html.parser").get_text().replace("\n", " ").strip()

def iter_block_items(parent):
    parent_elm = parent._element.body if isinstance(parent, docx.document.Document) else parent._tc
    for child in parent_elm.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield docx.table.Table(child, parent)

def extract_text(doc_path):
    doc = docx.Document(doc_path)
    text_blocks = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            txt = block.text.strip()
        elif isinstance(block, _Cell):
            txt = "\n".join(p.text.strip() for p in block.paragraphs)
        elif hasattr(block, "rows"):
            txt = "\n".join(cell.text.strip() for row in block.rows for cell in row.cells)
        else:
            txt = ""
        if txt:
            text_blocks.append(txt)
    return text_blocks

def split_chunks(blocks, chunk_size=3):
    return [" ".join(blocks[i:i+chunk_size]) for i in range(0, len(blocks), chunk_size)]

docs_folder = "docs"
new_chunks = []

for filename in os.listdir(docs_folder):
    if filename.endswith(".docx") and filename not in existing_files:
        path = os.path.join(docs_folder, filename)
        try:
            blocks = extract_text(path)
            chunks = split_chunks(blocks)
            for idx, chunk in enumerate(chunks):
                chunk_entry = {
                    "id": str(uuid.uuid4()),
                    "document": filename,
                    "section": f"{idx + 1}",
                    "content": clean_text(chunk)
                }
                new_chunks.append(chunk_entry)
            print(f"Processed: {filename}")
        except Exception as e:
            print(f"Failed: {filename} — {e}")

# Combine and save
combined_chunks = existing_chunks + new_chunks
os.makedirs("data", exist_ok=True)
with open(chunks_file, "w", encoding="utf-8") as f:
    json.dump(combined_chunks, f, ensure_ascii=False, indent=2)

print(f"Added {len(new_chunks)} new chunks. Total is now {len(combined_chunks)}.")
