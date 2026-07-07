import os
import tempfile
import streamlit as st

from utils.document_loader import load_document
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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_response" not in st.session_state:
    st.session_state.current_response = None

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("📚 ResearchMate AI")

    st.markdown("---")

    st.markdown("### Chat History")

    if st.session_state.chat_history:

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_response = None
            st.rerun()

        for index, item in enumerate(
            reversed(st.session_state.chat_history),
            start=1
        ):

            with st.expander(f"Q{index}: {item['question']}"):

                if item["found"]:
                    st.markdown(item["answer"])
                else:
                    st.warning(item["answer"])

                history_download = (
                    f"Question:\n{item['question']}\n\n"
                    f"Answer:\n{item['answer']}"
                )

                if item["citations"]:
                    history_download += "\n\nSources:\n"
                    history_download += "\n".join(
                        f"- {citation}" for citation in item["citations"]
                    )

                st.download_button(
                    label="Download",
                    data=history_download,
                    file_name=f"researchmate_answer_{index}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"sidebar_download_{index}_{item['question']}"
                )

    else:

        st.info("No questions yet.")

    st.markdown("---")

    st.markdown("### 📖 How to Use")

    st.write("""
1. Upload documents.

2. Click **Process Documents**.

3. Ask any question from the uploaded documents.

4. View the AI-generated answer.

5. Check the cited sources.
""")

# ==========================================================
# HEADER
# ==========================================================

st.title("📚 ResearchMate AI")

st.caption(
    "AI-powered Document Assistant using Retrieval-Augmented Generation (RAG)"
)

st.divider()

# ==========================================================
# DOCUMENT UPLOAD
# ==========================================================

st.subheader("📂 Upload Documents")

uploaded_files = st.file_uploader(
    "Select one or more documents",
    type=["pdf", "txt", "md", "markdown", "docx"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(
        f"✅ {len(uploaded_files)} document(s) selected."
    )

    with st.expander("Uploaded Files"):

        for document in uploaded_files:

            st.write("📄", document.name)

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
        st.warning("⚠️ Please upload at least one document.")
        st.stop()

    try:
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("📄 Reading uploaded documents...")
        progress_bar.progress(10)

        with st.spinner("📄 Reading uploaded documents..."):

            all_pages = []

            for uploaded_file in uploaded_files:

                extension = os.path.splitext(uploaded_file.name)[1]

                # Save uploaded document temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=extension
                ) as tmp_file:

                    tmp_file.write(uploaded_file.getbuffer())

                    temp_path = tmp_file.name

                # Extract text
                pages = load_document(
                    temp_path,
                    document_name=uploaded_file.name
                )

                all_pages.extend(pages)

                # Remove temporary file
                os.remove(temp_path)

            if not all_pages:
                raise ValueError(
                    "No readable text was found in the uploaded documents. "
                    "Please upload text-based files instead of scanned images."
                )

        status_text.text("🧩 Splitting documents into chunks...")
        progress_bar.progress(35)

        with st.spinner("🧩 Splitting documents into chunks..."):

            chunks = split_pages(all_pages)

            if not chunks:
                raise ValueError(
                    "The uploaded documents were read, but no valid text chunks were created."
                )

        status_text.text("🧠 Generating embeddings...")
        progress_bar.progress(60)

        with st.spinner("🧠 Generating embeddings..."):

            chunks = generate_embeddings(chunks)

        status_text.text("📚 Building FAISS vector database...")
        progress_bar.progress(85)

        with st.spinner("📚 Building FAISS vector database..."):

            dimension = len(chunks[0]["embedding"])

            vector_store = VectorStore(dimension)

            vector_store.add_chunks(chunks)

        # Save in Session State
        st.session_state.vector_store = vector_store
        st.session_state.documents_processed = True
        st.session_state.chunks = chunks
        st.session_state.chat_history = []
        st.session_state.current_response = None
        progress_bar.progress(100)
        status_text.text("✅ Processing completed successfully!")
        st.balloons()
        st.success("✅ Documents processed successfully!")
        

        # ==================================================
        # Processing Statistics
        # ==================================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Documents",
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

    st.subheader("❓ Ask a Document Question")

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

            answer_not_found = "do not contain enough information" in answer.lower()

            history_item = {
                "question": question.strip(),
                "answer": answer,
                "citations": citations,
                "found": not answer_not_found,
                "retrieved_chunks": retrieved_chunks,
            }

            st.session_state.chat_history.append(history_item)
            st.session_state.current_response = history_item

            # Show a warning if the answer is not found
            if answer_not_found:
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

            download_text = f"Question:\n{question.strip()}\n\nAnswer:\n{answer}"

            if citations:
                download_text += "\n\nSources:\n"
                download_text += "\n".join(f"- {citation}" for citation in citations)

            st.download_button(
                label="Download Answer",
                data=download_text,
                file_name="researchmate_answer.txt",
                mime="text/plain",
                use_container_width=True
            )

            if not answer_not_found:

                st.divider()

                with st.expander("🔎 Retrieved Chunks (Debug View)", expanded=True):

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

                        if "score" in chunk:
                            st.caption(
                                f"Relevance score: {chunk['score']:.2f}"
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
