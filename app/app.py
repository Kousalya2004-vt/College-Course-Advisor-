import streamlit as st
from rag import ask_question

st.set_page_config(page_title="College Course Advisor", page_icon="🎓")

st.title("🎓 College Course Advisor")
st.write("Ask questions about your college curriculum.")

question = st.text_input(
    "Enter your question:",
    placeholder="What subjects are available in the third semester?"
)

if st.button("Ask"):
    if question:
        with st.spinner("Finding answer..."):
            answer, sources = ask_question(question)

        st.subheader("Answer")
        st.write(answer)

        if sources:
            st.subheader("Sources")
            for source in sources:
                st.write(source)
    else:
        st.warning("Please enter a question.")
