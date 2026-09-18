import streamlit as st
from rag import ask_question

st.set_page_config(
    page_title="College Course Advisor",
    page_icon="🎓"
)

st.title("🎓 College Course Advisor")

st.write(
    "Upload your official curriculum PDF and ask questions about courses."
)

pdf = st.file_uploader(
    "Upload Curriculum PDF",
    type=["pdf"]
)

question = st.text_input(
    "Ask your question",
    placeholder="What subjects are available in the third semester?"
)

if st.button("Ask"):

    if pdf is None:
        st.warning("Please upload a curriculum PDF.")

    elif question.strip() == "":
        st.warning("Please enter a question.")

    else:

        with st.spinner("Finding answer..."):

            try:
                answer, sources = ask_question(pdf, question)

                st.subheader("Answer")
                st.write(answer)

                st.subheader("Sources")

                for source in sources:
                    st.write("📄 " + source)

            except Exception as e:
                st.error("Error: " + str(e))
