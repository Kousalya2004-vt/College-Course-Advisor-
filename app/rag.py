import streamlit as st
from google import genai
from pypdf import PdfReader

client = genai.Client(
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

Answer the question ONLY using the uploaded curriculum.

Question:
{question}

Curriculum:
{context}

Rules:
1. Give a clear and simple answer.
2. Do not invent information.
3. Use exact course names from the curriculum.
4. Give credits when asked.
5. Give prerequisites when asked.
6. Mention the relevant page number.
7. If the information is not available, say:
"I could not find this information in the uploaded curriculum."
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    sources = []

    for page in pages:

        source = "Page " + str(page["page"])

        if source not in sources:
            sources.append(source)

    return response.text, sources
