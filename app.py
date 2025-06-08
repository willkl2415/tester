# app.py
import os
import json
from flask import Flask, render_template, request, redirect, url_for
from answer_engine import get_answer

app = Flask(__name__)

# Load chunks.json and prepare filter lists
with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

documents = sorted(set(chunk["document"] for chunk in chunks_data))

@app.route("/", methods=["GET", "POST"])
def index():
    question = request.form.get("question", "")
    selected_doc = request.form.get("document", "")
    refine_query = request.form.get("refine_query", "")
    answer = []

    if request.form.get("clear") == "1":
        return redirect(url_for("index"))

    filtered_chunks = chunks_data
    if selected_doc and selected_doc != "All Documents":
        filtered_chunks = [chunk for chunk in filtered_chunks if chunk["document"] == selected_doc]

    if refine_query:
        filtered_chunks = [chunk for chunk in filtered_chunks if refine_query.lower() in chunk["content"].lower()]

    if question:
        answer = get_answer(question, filtered_chunks)
    elif refine_query:
        answer = filtered_chunks

    return render_template(
        "index.html",
        answer=answer,
        question=question,
        documents=["All Documents"] + documents,
        selected_doc=selected_doc,
        refine_query=refine_query
    )

if __name__ == "__main__":
    app.run(debug=True)
