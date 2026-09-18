import os
import re
import numpy as np
import google.generativeai as genai
from pypdf import PdfReader

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

PDF_FILE = "curriculum.pdf"

reader = PdfReader(PDF_FILE)

documents = []

for page_number, page in enumerate(reader.pages):
    text = page.extract_text()

    if text:
        chunks = re.split(r"\n\s*\n", text)

        for chunk in chunks:
            chunk = chunk.strip()

            if len(chunk) > 50:
                semester = re.search(
                    r"(?:semester|sem)\s*[-:]?\s*(\d+)",
                    chunk,
                    re.IGNORECASE
                )

                documents.append({
                    "text": chunk,
                    "page": page_number + 1,
                    "semester": semester.group(1) if semester else "Unknown"
                })


def get_embedding(text):
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return np.array(result["embedding"])


embeddings = [get_embedding(doc["text"]) for doc in documents]


def retrieve(question, top_k=5):
    query_embedding = genai.embed_content(
        model="models/gemini-embedding-001",
        content=question,
        task_type="retrieval_query"
    )

    query_embedding = np.array(query_embedding["embedding"])

    scores = []

    for i, embedding in enumerate(embeddings):
        score = np.dot(query_embedding, embedding) / (
            np.linalg.norm(query_embedding) *
            np.linalg.norm(embedding)
        )

        scores.append((score, i))

    scores.sort(reverse=True)

    selected = []

    for score, index in scores[:top_k]:
        selected.append(documents[index])

    return selected


def ask_question(question):
    results = retrieve(question)

    context = ""

    for doc in results:
        context += (
            f"\n[Page {doc['page']} | "
            f"Semester: {doc['semester']}]\n"
            f"{doc['text']}\n"
        )

    prompt = f"""
You are a College Course Advisor.

Answer the user's question ONLY using the curriculum information below.

If the answer is not available in the curriculum, say:
"I could not find this information in the curriculum."

Give a clear and simple answer.

Always mention the relevant page number in the answer.

Curriculum information:
{context}

User question:
{question}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    sources = []

    for doc in results:
        source = f"Page {doc['page']} — Semester: {doc['semester']}"
        if source not in sources:
            sources.append(source)

    return response.text, sources
