import re
import numpy as np
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_embedding(text):
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return np.array(result["embedding"])


def ask_question(pdf, question):

    reader = PdfReader(pdf)
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

    embeddings = []

    for doc in documents:
        embeddings.append(get_embedding(doc["text"]))

    query = genai.embed_content(
        model="models/gemini-embedding-001",
        content=question,
        task_type="retrieval_query"
    )

    query_embedding = np.array(query["embedding"])

    scores = []

    for i in range(len(embeddings)):
        score = np.dot(query_embedding, embeddings[i]) / (
            np.linalg.norm(query_embedding) *
            np.linalg.norm(embeddings[i])
        )

        scores.append((score, i))

    scores.sort(reverse=True)

    results = []

    for score, index in scores[:5]:
        results.append(documents[index])

    context = ""

    for doc in results:
        context += (
            f"\nPage: {doc['page']}\n"
            f"Semester: {doc['semester']}\n"
            f"{doc['text']}\n"
        )

    prompt = f"""
You are a College Course Advisor.

Answer the question only using the curriculum information below.

Question:
{question}

Curriculum:
{context}

Give a clear and simple answer.

If the information is not present, say:
"I could not find this information in the uploaded curriculum."

Mention the relevant page number.
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    sources = []

    for doc in results:
        source = f"Page {doc['page']} | Semester: {doc['semester']}"

        if source not in sources:
            sources.append(source)

    return response.text, sources
