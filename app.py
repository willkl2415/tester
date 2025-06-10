from flask import Flask, render_template, request
from answer_engine import get_answer
from filters import filter_chunks
from utils import load_chunks

app = Flask(__name__)

chunks = load_chunks("data/chunks.json")

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    results = []
    filtered_chunks = chunks
    selected_documents = []
    selected_sections = []
    include_subsections = False

    if request.method == "POST":
        user_input = request.form["question"]
        selected_documents = request.form.getlist("documents")
        selected_sections = request.form.getlist("sections")
        include_subsections = request.form.get("includeSubsections") == "on"
        filtered_chunks = filter_chunks(chunks, selected_documents, selected_sections, include_subsections)
        answer, results = get_answer(user_input, filtered_chunks)

    documents = sorted(set(chunk["document"] for chunk in chunks))
    sections = sorted(set(chunk.get("section", "Uncategorised") for chunk in chunks))

    return render_template("index.html",
                           answer=answer,
                           results=results,
                           documents=documents,
                           sections=sections,
                           selected_documents=selected_documents,
                           selected_sections=selected_sections,
                           include_subsections=include_subsections)
