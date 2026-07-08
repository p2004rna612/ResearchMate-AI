import os
import tempfile
import queue
import threading
import streamlit as st

import config
from utils.citation_utils import format_citation
from utils.document_loader import load_document
from utils.metadata_extractor import extract_document_metadata
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

if "document_metadata" not in st.session_state:
    st.session_state.document_metadata = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_response" not in st.session_state:
    st.session_state.current_response = None


def render_metadata_panel(metadata_items):
    if not metadata_items:
        return

    st.subheader("Paper Information")

    for metadata in metadata_items:
        with st.container(border=True):
            title = metadata.get("title", "Not found")
            document = metadata.get("document", "Uploaded document")

            st.markdown(f"#### {title}")
            st.caption(document)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Authors**")
                st.write(metadata.get("authors", "Not found"))
                st.markdown("**Year**")
                st.write(metadata.get("year", "Not found"))

            with col2:
                st.markdown("**DOI**")
                doi = metadata.get("doi", "Not found")
                if doi != "Not found":
                    st.markdown(f"[{doi}](https://doi.org/{doi})")
                else:
                    st.write(doi)

                st.markdown("**Conference / Journal**")
                st.write(metadata.get("venue", "Not found"))

            with col3:
                st.markdown("**Keywords**")
                st.write(metadata.get("keywords", "Not found"))

            st.markdown("**Abstract**")
            st.write(metadata.get("abstract", "Not found"))


def generate_follow_up_questions():
    return [
        "Explain this in simple terms.",
        "Compare this with another method.",
        "What are the limitations?",
        "Give practical applications.",
    ]


RESEARCH_TASKS = {
    "Answer a question": {
        "placeholder": "Example: What is BERT?",
        "button": "Ask ResearchMate AI",
        "default_request": "",
        "uses_broad_context": False,
        "instruction": (
            "Answer the user's question directly. Use concise academic language "
            "and include only information supported by the document context."
        ),
    },
    "Explain a difficult concept": {
        "placeholder": "Example: Explain self-attention in simple terms.",
        "button": "Explain Concept",
        "default_request": "",
        "uses_broad_context": False,
        "instruction": (
            "Explain the concept clearly in simple terms, then add the technical "
            "meaning and why it matters in the paper."
        ),
    },
    "Summarize papers": {
        "placeholder": "Optional: focus the summary on methods, findings, or contributions.",
        "button": "Summarize Papers",
        "default_request": "Summarize the uploaded paper or papers.",
        "uses_broad_context": True,
        "instruction": (
            "Summarize the uploaded paper or papers with sections for purpose, "
            "methodology, key contributions, findings, and conclusion."
        ),
    },
    "Compare papers": {
        "placeholder": "Optional: compare by method, dataset, results, or limitations.",
        "button": "Compare Papers",
        "default_request": "Compare the uploaded papers.",
        "uses_broad_context": True,
        "max_chunks": 6,
        "per_document": 2,
        "max_context_chars": 650,
        "max_output_tokens": 380,
        "instruction": (
            "Create a concise comparison. Use short sections for problem, method, "
            "strengths, limitations, and key difference. Keep it under 8 bullets."
        ),
    },
    "Generate literature review": {
        "placeholder": "Optional: describe the topic or angle for the literature review.",
        "button": "Generate Literature Review",
        "default_request": "Generate a literature review from the uploaded papers.",
        "uses_broad_context": True,
        "instruction": (
            "Write a concise literature review that synthesizes the uploaded papers, "
            "groups related ideas, highlights trends, and explains how the papers connect."
        ),
    },
    "Identify research gaps": {
        "placeholder": "Optional: focus on methods, datasets, evaluation, or applications.",
        "button": "Identify Research Gaps",
        "default_request": "Identify research gaps from the uploaded papers.",
        "uses_broad_context": True,
        "instruction": (
            "Identify research gaps, unresolved limitations, missing evaluations, "
            "and possible future research directions supported by the document context."
        ),
    },
}


def select_broad_context_chunks(
    chunks,
    max_chunks=None,
    per_document=None
):
    max_chunks = max_chunks or getattr(config, "BROAD_CONTEXT_MAX_CHUNKS", 10)
    per_document = per_document or getattr(
        config,
        "BROAD_CONTEXT_CHUNKS_PER_DOCUMENT",
        3
    )

    selected = []
    counts_by_document = {}

    for chunk in chunks:
        document = chunk.get("document", "document")
        current_count = counts_by_document.get(document, 0)

        if current_count >= per_document:
            continue

        selected.append(chunk)
        counts_by_document[document] = current_count + 1

        if len(selected) >= max_chunks:
            break

    return selected


def trim_chunks_for_task(chunks, max_context_chars=None):
    if not max_context_chars:
        return chunks

    trimmed_chunks = []

    for chunk in chunks:
        trimmed_chunk = dict(chunk)
        text = (trimmed_chunk.get("text") or "").strip()

        if len(text) > max_context_chars:
            text = text[:max_context_chars].rsplit(" ", 1)[0].strip()

        trimmed_chunk["text"] = text
        trimmed_chunks.append(trimmed_chunk)

    return trimmed_chunks


def generate_research_response(
    request_text,
    retrieved_chunks,
    selected_task,
    task_config,
    stream_callback=None
):
    fast_chunks = trim_chunks_for_task(
        retrieved_chunks,
        max_context_chars=task_config.get("max_context_chars")
    )

    try:
        return generate_answer(
            request_text,
            fast_chunks,
            task_label=selected_task,
            task_instruction=task_config["instruction"],
            max_output_tokens=task_config.get("max_output_tokens"),
            max_context_chars=task_config.get("max_context_chars"),
            stream_callback=stream_callback,
        )
    except TypeError as exc:
        if "unexpected keyword argument" not in str(exc):
            raise

        return generate_answer(
            request_text,
            fast_chunks,
            task_label=selected_task,
            task_instruction=task_config["instruction"],
        )


def generate_local_fallback_response(request_text, retrieved_chunks, selected_task):
    if not retrieved_chunks:
        return (
            "The uploaded documents do not contain enough information to answer this request.",
            []
        )

    citations = sorted({format_citation(chunk) for chunk in retrieved_chunks})

    if selected_task == "Compare papers":
        grouped_chunks = {}

        for chunk in retrieved_chunks:
            grouped_chunks.setdefault(chunk["document"], []).append(chunk)

        lines = [
            "Gemini is taking too long, so here is a quick comparison from the retrieved document text.",
            "",
        ]

        for document, chunks in grouped_chunks.items():
            excerpt = chunks[0]["text"].strip()
            excerpt = excerpt[:450].rsplit(" ", 1)[0].strip()
            lines.append(f"**{document}**")
            lines.append(f"- Main retrieved idea: {excerpt}")
            lines.append("")

        lines.append("Use the retrieved chunks below for more detail, or ask a narrower comparison question.")

        return "\n".join(lines), citations

    lines = [
        "Gemini is taking too long, so here is a quick document-based response from the most relevant retrieved passages.",
        "",
    ]

    for index, chunk in enumerate(retrieved_chunks[:3], start=1):
        excerpt = chunk["text"].strip()
        excerpt = excerpt[:600].rsplit(" ", 1)[0].strip()
        lines.append(
            f"{index}. From **{chunk['document']}**, page {chunk['page']}: {excerpt}"
        )

    lines.append("")
    lines.append("Try asking a shorter or more specific question for a faster Gemini answer.")

    return "\n".join(lines), citations


def generate_research_response_with_timeout(
    request_text,
    retrieved_chunks,
    selected_task,
    task_config
):
    timeout_seconds = getattr(config, "GEMINI_REQUEST_TIMEOUT_SECONDS", 12)
    result_queue = queue.Queue(maxsize=1)

    def run_gemini_request():
        try:
            result_queue.put(
                (
                    "ok",
                    generate_research_response(
                        request_text,
                        retrieved_chunks,
                        selected_task,
                        task_config,
                        None
                    ),
                )
            )
        except Exception as exc:
            result_queue.put(("error", exc))

    worker = threading.Thread(target=run_gemini_request, daemon=True)
    worker.start()

    try:
        status, payload = result_queue.get(timeout=timeout_seconds)
    except queue.Empty:
        return generate_local_fallback_response(
            request_text,
            trim_chunks_for_task(
                retrieved_chunks,
                max_context_chars=task_config.get("max_context_chars")
            ),
            selected_task
        )

    if status == "error":
        return generate_local_fallback_response(
            request_text,
            trim_chunks_for_task(
                retrieved_chunks,
                max_context_chars=task_config.get("max_context_chars")
            ),
            selected_task
        )

    answer, citations = payload

    if answer.startswith("An error occurred while generating the answer."):
        return generate_local_fallback_response(
            request_text,
            trim_chunks_for_task(
                retrieved_chunks,
                max_context_chars=task_config.get("max_context_chars")
            ),
            selected_task
        )

    return answer, citations


def render_follow_up_questions(questions):
    if not questions:
        return

    st.divider()
    st.subheader("Suggested Follow-up Questions")

    with st.container(border=True):
        for follow_up in questions:
            st.markdown(f"- {follow_up}")

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

            task_label = item.get("task", "Answer a question")

            with st.expander(f"{task_label} {index}: {item['question']}"):

                if item["found"]:
                    st.markdown(item["answer"])
                    render_follow_up_questions(
                        item.get("follow_up_questions", [])
                    )
                else:
                    st.warning(item["answer"])

                history_download = (
                    f"Task:\n{task_label}\n\n"
                    f"Request:\n{item['question']}\n\n"
                    f"Response:\n{item['answer']}"
                )

                if item["citations"]:
                    history_download += "\n\nSources:\n"
                    history_download += "\n".join(
                        f"- {citation}" for citation in item["citations"]
                    )

                if item.get("follow_up_questions"):
                    history_download += "\n\nSuggested Follow-up Questions:\n"
                    history_download += "\n".join(
                        f"- {follow_up}"
                        for follow_up in item["follow_up_questions"]
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
            document_metadata = []

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

                if pages:
                    document_metadata.append(
                        extract_document_metadata(
                            pages,
                            uploaded_file.name
                        )
                    )

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
        st.session_state.document_metadata = document_metadata
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

        render_metadata_panel(st.session_state.document_metadata)

    except Exception as e:

        st.error("❌ Error while processing documents.")

        st.exception(e)

st.divider()

# ==========================================================
# RESEARCH ASSISTANCE
# ==========================================================

if st.session_state.documents_processed:

    st.success("Documents processed successfully. You can now use research assistance.")

    st.subheader("Research Assistance")

    render_metadata_panel(st.session_state.document_metadata)

    selected_task = st.selectbox(
        "Choose a research task",
        options=list(RESEARCH_TASKS.keys())
    )

    task_config = RESEARCH_TASKS[selected_task]

    question = st.text_area(
        "Enter your request",
        placeholder=task_config["placeholder"],
        height=100
    )

    request_text = question.strip() or task_config["default_request"]

    ask_button = st.button(
        task_config["button"],
        use_container_width=True
    )

    if ask_button:

        if not request_text:
            st.warning("Please enter a research request.")
            st.stop()

        try:

            with st.spinner("Preparing relevant document context..."):

                if task_config["uses_broad_context"]:
                    retrieved_chunks = select_broad_context_chunks(
                        st.session_state.chunks,
                        max_chunks=task_config.get("max_chunks"),
                        per_document=task_config.get("per_document")
                    )
                else:
                    retrieved_chunks = retrieve(
                        request_text,
                        st.session_state.vector_store
                    )

            st.divider()
            st.subheader("ResearchMate Response")
            response_placeholder = st.empty()
            response_placeholder.info(
                "Trying Gemini. If it is slow, ResearchMate will show a quick document-based response."
            )

            with st.spinner("Generating response..."):

                answer, citations = generate_research_response_with_timeout(
                    request_text,
                    retrieved_chunks,
                    selected_task,
                    task_config
                )

            answer_not_found = "do not contain enough information" in answer.lower()
            follow_up_questions = (
                []
                if answer_not_found
                else generate_follow_up_questions()
            )

            history_item = {
                "task": selected_task,
                "question": request_text,
                "answer": answer,
                "citations": citations,
                "found": not answer_not_found,
                "retrieved_chunks": retrieved_chunks,
                "follow_up_questions": follow_up_questions,
            }

            st.session_state.chat_history.append(history_item)
            st.session_state.current_response = history_item

            if answer_not_found:
                response_placeholder.empty()
                st.warning(answer)
            else:
                response_placeholder.markdown(answer)

                st.divider()

                st.subheader("Sources")

                if citations:

                    for citation in citations:
                        st.markdown(f"- {citation}")

                else:

                    st.info("No citations available.")

                render_follow_up_questions(follow_up_questions)

            download_text = (
                f"Task:\n{selected_task}\n\n"
                f"Request:\n{request_text}\n\n"
                f"Response:\n{answer}"
            )

            if citations:
                download_text += "\n\nSources:\n"
                download_text += "\n".join(f"- {citation}" for citation in citations)

            if follow_up_questions:
                download_text += "\n\nSuggested Follow-up Questions:\n"
                download_text += "\n".join(
                    f"- {follow_up}"
                    for follow_up in follow_up_questions
                )

            st.download_button(
                label="Download Response",
                data=download_text,
                file_name="researchmate_response.txt",
                mime="text/plain",
                use_container_width=True
            )

            if not answer_not_found:

                st.divider()

                with st.expander("Retrieved Chunks (Debug View)", expanded=True):

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

            st.error("Failed to generate research assistance.")

            st.exception(e)

else:

    st.info(
        "Upload and process documents before using research assistance."
    )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "ResearchMate AI • Built using Streamlit, FAISS, Sentence Transformers and Gemini 2.5 Flash"
)



