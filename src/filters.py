def filter_chunks(chunks, selected_documents, selected_sections, include_subsections):
    filtered = []

    for chunk in chunks:
        doc_match = not selected_documents or chunk["document"] in selected_documents

        if not selected_sections:
            sec_match = True
        elif include_subsections:
            sec_match = any(
                chunk.get("section", "").startswith(sel_sec)
                for sel_sec in selected_sections
            )
        else:
            sec_match = chunk.get("section") in selected_sections

        if doc_match and sec_match:
            filtered.append(chunk)

    return filtered

