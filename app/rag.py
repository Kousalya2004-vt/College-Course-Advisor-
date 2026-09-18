import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)


def ask_question(pdf, question):

    reader = PdfReader(pdf)

    pages = []

    for page_number, page in enumerate(reader.pages):

        text = page.extract_text()

        if text:
            pages.append({
                "page": page_number + 1,
                "text": text
            })

    context = ""

    for page in pages:

        context += (
            "\n--- Page "
            + str(page["page"])
            + " ---\n"
            + page["text"]
        )

    if len(context) > 50000:
        context = context[:50000]

    prompt = f"""
You are a College Course Advisor.

Answer the user's question using ONLY the uploaded curriculum.

User Question:
{question}

Curriculum:
{context}

Instructions:

1. Give a clear and simple answer.
2. Do not invent information.
3. Use the exact course names and credits from the curriculum.
4. If the question asks about a semester, give the subjects for that semester.
5. If the question asks about prerequisites, identify the prerequisite courses.
6. If the question asks about credits, give the correct credits.
7. Mention the relevant page number.
8. If the information is not available, say:
"I could not find this information in the uploaded curriculum."
"""

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    sources = []

    for page in pages:

        source = "Page " + str(page["page"])

        if source not in sources:
            sources.append(source)

    return response.text, sources
