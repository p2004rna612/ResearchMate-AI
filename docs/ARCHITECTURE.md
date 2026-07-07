# ResearchMate AI Architecture

```
                  User Uploads PDFs
                          │
                          ▼
                  PDF Text Extraction
                          │
                          ▼
                    Text Chunking
                          │
                          ▼
               Sentence Embeddings
                          │
                          ▼
                 FAISS Vector Store
                          ▲
                          │
                  User Question
                          │
                          ▼
              Semantic Similarity Search
                          │
                          ▼
                  Gemini 2.5 Flash
                          │
                          ▼
          Answer + Source Citations
```

## Components

- PDF Loader
- Recursive Text Splitter
- Sentence Transformer Embeddings
- FAISS Vector Database
- Retriever
- Gemini LLM
- Streamlit UI