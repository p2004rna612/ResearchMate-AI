from utils.pdf_loader import load_pdf
from utils.text_splitter import split_pages
from utils.embeddings import generate_embeddings

pages = load_pdf("data/documents/bert.pdf")

chunks = split_pages(pages)

chunks = generate_embeddings(chunks)

print("=" * 60)

print("Chunks:", len(chunks))

print("Embedding Dimension:", len(chunks[0]["embedding"]))

print("=" * 60)

print(chunks[0]["embedding"][:10])