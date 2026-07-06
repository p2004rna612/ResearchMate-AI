from utils.pdf_loader import load_pdf
from utils.text_splitter import split_pages

pages = load_pdf("data/documents/bert.pdf")

chunks = split_pages(pages)

print("=" * 60)
print(f"Total Pages : {len(pages)}")
print(f"Total Chunks: {len(chunks)}")
print("=" * 60)

print("\nFirst Chunk:\n")

print(chunks[0])