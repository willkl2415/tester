# preprocess_pipeline.py
import re
import docx
import uuid
from bs4 import BeautifulSoup
from docx.table import _Cell
from docx.text.paragraph import Paragraph
from typing import Union

def get_text_from_paragraph(paragraph):
    return paragraph.text.strip()

def get_text_from_cell(cell):
    return "\n".join(get_text_from_paragraph(p) for p in cell.paragraphs)

def iter_block_items(parent):
    if isinstance(parent, docx.document.Document):
        parent_elm = parent._element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("Unsupported parent type")

    for child in parent_elm.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield _Cell(child, parent)

def extract_text_and_sections(doc_path):
    doc = docx.Document(doc_path)
    paragraphs = []
    current_section = "Uncategorised"

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue

            # Match patterns like "3.1 Introduction", "4 Training Gap Analysis", etc.
            match = re.match(r"^(\d+(\.\d+)?)[\s\-–—]+(.+)", text)
            if match:
                section_number = match.group(1)
                section_title = match.group(3).strip()
                current_section = f"{section_number} {section_title}"

            paragraphs.append({"section": current_section, "text": text})
        elif isinstance(block, _Cell):
            paragraphs.append({"section": current_section, "text": get_text_from_cell(block)})

    return paragraphs

def chunk_paragraphs(paragraphs, max_words=300):
    chunks = []
    current_chunk = ""
    current_section = ""
    for para in paragraphs:
        if not para["text"]:
            continue

        section = para["section"]
        text = para["text"]
        if len(current_chunk.split()) + len(text.split()) <= max_words:
            current_chunk += " " + text
        else:
            chunks.append({
                "id": str(uuid.uuid4()),
                "section": current_section or section,
                "content": current_chunk.strip()
            })
            current_chunk = text
            current_section = section

    if current_chunk.strip():
        chunks.append({
            "id": str(uuid.uuid4()),
            "section": current_section,
            "content": current_chunk.strip()
        })

    return chunks

def clean_text(text):
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text
