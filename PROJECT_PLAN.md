# ResearchMate AI – Project Plan

## 1. Project Overview

### Project Title
ResearchMate AI – Research Agent with Citations

### Objective
Develop an AI-powered Research Agent that accepts user questions and source documents, retrieves relevant information using Retrieval-Augmented Generation (RAG), and generates accurate answers with citations.

---

## 2. Problem Statement

Researchers often spend significant time searching through multiple documents to find relevant information. This project aims to simplify that process by allowing users to upload documents and ask natural language questions. The agent retrieves relevant sections and generates concise, cited answers.

---

## 3. Project Goals

- Accept multiple PDF documents
- Extract document text
- Build semantic search using embeddings
- Retrieve relevant passages
- Generate answers using Gemini
- Display citations
- Avoid hallucinations by answering only from uploaded documents

---

## 4. Functional Requirements

### Input

- PDF documents
- User question

### Output

- AI-generated answer
- Source citations
- "Answer not found" message when appropriate

---

## 5. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| UI | Streamlit |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | Sentence Transformers |
| Vector Database | FAISS |
| PDF Parsing | pdfplumber |
| Environment | python-dotenv |
| Version Control | Git & GitHub |

---

## 6. System Architecture

User

↓

Upload PDF

↓

PDF Loader

↓

Text Splitter

↓

Embedding Generator

↓

FAISS Vector Store

↓

Retriever

↓

Gemini LLM

↓

Answer Generator

↓

Citation Engine

↓

Streamlit UI

---

## 7. Folder Structure

ResearchMate-AI/

app.py

README.md

requirements.txt

PROJECT_PLAN.md

utils/

data/

vector_store/

screenshots/

sample_output/

---

## 8. Workflow

1. Upload PDFs
2. Extract text
3. Split into chunks
4. Generate embeddings
5. Store vectors in FAISS
6. User asks a question
7. Retrieve relevant chunks
8. Generate answer using Gemini
9. Display citations

---

## 9. Modules

### PDF Loader

Responsible for extracting text from uploaded PDFs.

### Text Splitter

Splits extracted text into manageable chunks.

### Embedding Generator

Converts text chunks into vector embeddings.

### Vector Store

Stores embeddings using FAISS.

### Retriever

Finds the most relevant chunks for a question.

### LLM Module

Sends retrieved context to Gemini.

### Citation Module

Displays source document and page references.

### Streamlit UI

Provides user interaction.

---

## 10. Deliverables

- Public GitHub Repository
- Working Streamlit Application
- README
- Sample PDFs
- Sample Questions
- Sample Outputs
- Tradeoff Notes

---

## 11. Limitations

- Optimized for text-based PDFs
- No OCR support in the initial version
- Chunk-level citations
- English documents only

---

## 12. Future Enhancements

- OCR for scanned PDFs
- DOCX support
- Persistent vector database
- Chat history
- User authentication
- Multi-user support

---

## 13. Development Phases

Phase 1 – Project Setup

Phase 2 – PDF Processing

Phase 3 – Text Chunking

Phase 4 – Embedding Generation

Phase 5 – FAISS Integration

Phase 6 – Gemini Integration

Phase 7 – Citation Engine

Phase 8 – UI Improvements

Phase 9 – Testing

Phase 10 – Documentation

Phase 11 – GitHub Submission

## Design Decisions

- Streamlit was chosen over React to reduce development time and focus on AI functionality.
- FAISS was selected for fast local vector similarity search.
- Sentence Transformers were chosen for high-quality semantic embeddings.
- Gemini Flash was selected for its speed and free API access.
- Modular architecture improves maintainability and makes the code easier to explain.