# ResearchMate AI

ResearchMate AI is an AI-powered research assistant built with Retrieval-Augmented Generation (RAG). It allows users to upload documents, ask natural language questions, summarize papers, compare research, generate literature reviews, identify research gaps, and receive grounded responses with source citations.

The system is document-agnostic: it does not depend on any fixed PDF or hardcoded dataset. Any supported uploaded document is processed dynamically into chunks, embedded, stored in FAISS, and used for retrieval-based answering.

## Features

- Upload multiple documents
- Supports PDF, TXT, Markdown, and DOCX files
- Automatically extracts title, authors, year, DOI, venue, keywords, and abstract
- Shows extracted paper metadata in a clean information panel
- Extracts and chunks document text automatically
- Uses a faster PDF text extraction path with fallback support
- Generates semantic embeddings using Sentence Transformers
- Stores and searches embeddings using FAISS
- Uses Google Gemini 2.5 Flash for answer generation
- Answers only from uploaded document context
- Explains difficult concepts from uploaded papers
- Summarizes individual or multiple papers
- Compares papers across methods, findings, strengths, and limitations
- Generates literature-review style syntheses
- Identifies research gaps and future directions
- Filters weak retrieval matches using a relevance threshold
- Shows source citations with page numbers
- Adds research links using DOI, arXiv, or Google Scholar fallback
- Suggests follow-up questions after each answer
- Shows retrieved chunks and relevance scores for transparency
- Maintains chat history in the sidebar
- Allows users to download generated answers

## System Architecture

```text
Uploaded Documents
        |
        v
Document Loader
(PDF / TXT / Markdown / DOCX)
        |
        v
Text Extraction
        |
        v
Metadata Extraction + Information Panel
        |
        v
Text Chunking
        |
        v
Sentence Transformer Embeddings
        |
        v
FAISS Vector Store
        |
        v
Research Request
        |
        v
Task Mode + Context Selection
        |
        v
Gemini 2.5 Flash
        |
        v
Research Assistance Response + Citations + Research Links
```

## Project Structure

```text
ResearchMate-AI/

app.py
config.py
requirements.txt
README.md
.env.example

utils/
  citation_utils.py
  document_loader.py
  metadata_extractor.py
  pdf_loader.py
  text_splitter.py
  embeddings.py
  vector_store.py
  retriever.py
  prompts.py
  llm.py

data/
  documents/

docs/
sample_output/
screenshots/
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ResearchMate-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux or macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### 5. Run the application

```bash
streamlit run app.py
```

## Supported File Types

- PDF
- TXT
- Markdown (`.md`, `.markdown`)
- DOCX

Note: scanned image-based PDFs may not work unless OCR is added. The current implementation works best with text-based documents.

## How To Use

1. Upload one or more supported documents.
2. Click **Process Documents**.
3. Review the extracted paper information panel.
4. Choose a research task.
5. Enter a question, topic, or optional focus.
6. View the generated research assistance response.
7. Check citations, page numbers, and research links.
8. Use the suggested follow-up questions to continue exploring the topic.
9. Inspect retrieved chunks and relevance scores if needed.
10. Download the response using the download button.
11. Use the sidebar chat history to revisit previous responses.

## Research Assistance Modes

ResearchMate AI supports these task modes:

- Answer a question
- Explain a difficult concept
- Summarize papers
- Compare papers
- Generate literature review
- Identify research gaps

Broad tasks such as summaries, comparisons, literature reviews, and research-gap analysis use a wider selection of uploaded document chunks so the response can synthesize across papers.

## Paper Metadata Extraction

After processing, ResearchMate AI displays a paper information panel for each uploaded document.

Extracted fields:

- Title
- Authors
- Year
- DOI
- Conference / Journal
- Keywords
- Abstract

The extractor uses document text heuristics and DOI pattern matching, so it works without an additional LLM or network call. If a field cannot be detected confidently, the panel shows `Not found`.

## Citation And Research Link Support

ResearchMate AI creates citations from the uploaded documents and enriches them with external research links when possible.

Link priority:

1. DOI link if a DOI is found in the document text
2. arXiv link if an arXiv identifier is found
3. Google Scholar search link as a fallback

Example citation:

```text
bert.pdf (Page 3) - DOI
```

or:

```text
transformer.pdf (Page 2) - arXiv
```

or:

```text
paper.pdf (Page 1) - Google Scholar
```

## Sample Questions

- What is BERT?
- Explain self-attention.
- What is Retrieval-Augmented Generation?
- Compare BERT and Transformers.
- Which paper introduced BERT?
- What are the main contributions of this document?

## Out-Of-Scope Question Handling

If the uploaded documents do not contain enough information, the app responds with:

```text
The uploaded documents do not contain enough information to answer this question.
```

For unrelated questions, the app hides citations and retrieved chunks to avoid misleading the user.

## Technologies Used

- Python
- Streamlit
- Google Gemini 2.5 Flash
- Sentence Transformers
- FAISS
- pdfplumber
- python-docx
- LangChain Text Splitter
- NumPy

## Key Design Decisions

### Why RAG?

RAG grounds answers in uploaded documents and reduces hallucination by forcing the model to answer from retrieved context.

### Why FAISS?

FAISS provides efficient vector similarity search over document chunks.

### Why Sentence Transformers?

Sentence Transformers provide strong semantic embeddings with reasonable speed and resource usage.

The embedding model is loaded lazily and reused after the first embedding or retrieval call. This avoids repeated Hugging Face metadata requests during Streamlit reruns.

### Why faster processing settings?

ResearchMate AI uses larger chunks, lower chunk overlap, batched embedding generation, and capped Gemini context to reduce processing and response time. PDF text extraction uses `pypdfium2` first because it is much faster for text-based PDFs, with `pdfplumber` kept as a fallback.

### Why relevance filtering?

Semantic search always returns nearest chunks, even for unrelated questions. A minimum relevance threshold helps reject weak matches before answer generation.

### Why DOI/arXiv/Google Scholar links?

DOI and arXiv are stable research identifiers. Google Scholar is used only as a fallback search link when no stable identifier is detected.

## Future Improvements

- OCR support for scanned PDFs
- PDF text highlighting for cited passages
- Persistent chat history database
- User authentication
- FastAPI backend
- Cloud deployment
- LLM-assisted metadata validation for difficult paper layouts

## Author

Poorna Pragna

Final Year B.E. - Computer Science & Engineering (AI & ML)

Sahyadri College of Engineering & Management
