import os
import tempfile
import streamlit as st

from utils.pdf_loader import load_pdf
from utils.text_splitter import split_pages
from utils.embeddings import generate_embeddings
from utils.vector_store import VectorStore
from utils.retriever import retrieve
from utils.llm import generate_answer

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False

if "chunks" not in st.session_state:
    st.session_state.chunks = []

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("📚 ResearchMate AI")

    st.markdown("---")

    st.markdown("### 🚀 Features")

    st.success("✅ Multi PDF Upload")

    st.success("✅ Semantic Search")

    st.success("✅ Gemini 2.5 Flash")

    st.success("✅ FAISS Vector Database")

    st.success("✅ Source Citations")

    st.markdown("---")

    st.markdown("### 📖 How to Use")

    st.write("""
1. Upload research papers.

2. Click **Process Documents**.

3. Ask any research question.

4. View the AI-generated answer.

5. Check the cited sources.
""")

# ==========================================================
# HEADER
# ==========================================================

st.title("📚 ResearchMate AI")

st.caption(
    "AI-powered Research Assistant using Retrieval-Augmented Generation (RAG)"
)

st.divider()

# ==========================================================
# PDF UPLOAD
# ==========================================================

st.subheader("📂 Upload Research Papers")

uploaded_files = st.file_uploader(
    "Select one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(
        f"✅ {len(uploaded_files)} PDF(s) selected."
    )

    with st.expander("Uploaded Files"):

        for pdf in uploaded_files:

            st.write("📄", pdf.name)

st.divider()

# ==========================================================
# PROCESS DOCUMENTS
# ==========================================================

st.subheader("⚙️ Process Documents")

process_button = st.button(
    "🚀 Process Documents",
    use_container_width=True
)

if process_button:

    if not uploaded_files:
        st.warning("⚠️ Please upload at least one PDF.")
        st.stop()

    try:

        with st.spinner("📄 Reading uploaded documents..."):

            all_pages = []

            for uploaded_file in uploaded_files:

                # Save uploaded PDF temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp_file:

                    tmp_file.write(uploaded_file.getbuffer())

                    temp_path = tmp_file.name

                # Extract pages
                pages = load_pdf(
                    temp_path,
                    document_name=uploaded_file.name
                )

                all_pages.extend(pages)

                # Remove temporary file
                os.remove(temp_path)

        with st.spinner("🧩 Splitting documents into chunks..."):

            chunks = split_pages(all_pages)

        with st.spinner("🧠 Generating embeddings..."):

            chunks = generate_embeddings(chunks)

        with st.spinner("📚 Building FAISS vector database..."):

            dimension = len(chunks[0]["embedding"])

            vector_store = VectorStore(dimension)

            vector_store.add_chunks(chunks)

        # Save in Session State
        st.session_state.vector_store = vector_store
        st.session_state.documents_processed = True
        st.session_state.chunks = chunks
        st.balloons()
        st.success("✅ Documents processed successfully!")
        

        # ==================================================
        # Processing Statistics
        # ==================================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "PDFs",
                len(uploaded_files)
            )

        with col2:
            st.metric(
                "Pages",
                len(all_pages)
            )

        with col3:
            st.metric(
                "Chunks",
                len(chunks)
            )

    except Exception as e:

        st.error("❌ Error while processing documents.")

        st.exception(e)

st.divider()

# ==========================================================
# ASK QUESTIONS
# ==========================================================

if st.session_state.documents_processed:

    st.success("✅ Documents processed successfully. You can now ask questions.")

    st.subheader("❓ Ask a Research Question")

    question = st.text_input(
        "Enter your question",
        placeholder="Example: What is BERT?"
    )

    ask_button = st.button(
        "🤖 Ask ResearchMate AI",
        use_container_width=True
    )

    if ask_button:

        if question.strip() == "":
            st.warning("⚠️ Please enter a question.")
            st.stop()

        try:

            with st.spinner("🔍 Searching relevant document chunks..."):

                retrieved_chunks = retrieve(
                    question,
                    st.session_state.vector_store
                )

            with st.spinner("🤖 Gemini is generating an answer..."):

                answer, citations = generate_answer(
                question,
                retrieved_chunks
            )

                st.divider()

                st.subheader("💬 AI Answer")

# Show a warning if the answer is not found
            if "do not contain enough information" in answer.lower():
                st.warning(answer)
            else:
                st.markdown(answer)

                st.divider()

                st.subheader("📚 Sources")

            if citations:

                for citation in citations:
                    st.markdown(f"- {citation}")

            else:

                st.info("No citations available.")

            st.divider()

            with st.expander("🔎 Retrieved Chunks (Debug View)"):

                for i, chunk in enumerate(retrieved_chunks, start=1):

                    st.markdown(
                        f"### Result {i}"
                    )

                    st.markdown(
                        f"**Document:** {chunk['document']}"
                    )

                    st.markdown(
                        f"**Page:** {chunk['page']}"
                    )

                    st.write(chunk["text"])

                    st.markdown("---")

        except Exception as e:

            st.error("❌ Failed to generate answer.")

            st.exception(e)

else:

    st.info(
        "📄 Upload and process documents before asking questions."
    )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "ResearchMate AI • Built using Streamlit, FAISS, Sentence Transformers and Gemini 2.5 Flash"
)