# ResearchMate AI

ResearchMate AI is an AI-powered document question-answering assistant built with Retrieval-Augmented Generation (RAG). It allows users to upload documents, ask natural language questions, and receive grounded answers with source citations.

The system is document-agnostic: it does not depend on any fixed PDF or hardcoded dataset. Any supported uploaded document is processed dynamically into chunks, embedded, stored in FAISS, and used for retrieval-based answering.

## Features

- Upload multiple documents
- Supports PDF, TXT, Markdown, and DOCX files
- Extracts and chunks document text automatically
- Generates semantic embeddings using Sentence Transformers
- Stores and searches embeddings using FAISS
- Uses Google Gemini 2.5 Flash for answer generation
- Answers only from uploaded document context
- Filters weak retrieval matches using a relevance threshold
- Shows source citations with page numbers
- Adds research links using DOI, arXiv, or Google Scholar fallback
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
Text Chunking
        |
        v
Sentence Transformer Embeddings
        |
        v
FAISS Vector Store
        |
        v
User Question
        |
        v
Semantic Retrieval + Relevance Filtering
        |
        v
Gemini 2.5 Flash
        |
        v
Answer + Citations + Research Links
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
3. Ask a question related to the uploaded documents.
4. View the generated answer.
5. Check citations, page numbers, and research links.
6. Inspect retrieved chunks and relevance scores if needed.
7. Download the answer using the download button.
8. Use the sidebar chat history to revisit previous answers.

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
- Advanced metadata extraction from research papers

## Author

Poorna Pragna

Final Year B.E. - Computer Science & Engineering (AI & ML)

Sahyadri College of Engineering & Management
