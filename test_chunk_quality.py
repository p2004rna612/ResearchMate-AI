from pathlib import Path

from utils.pdf_loader import load_pdf
from utils.text_splitter import split_pages

pdf_folder = Path("data/documents")
pdf_files = list(pdf_folder.glob("*.pdf"))

all_chunks = []

for pdf in pdf_files:
    pages = load_pdf(pdf)
    chunks = split_pages(pages)
    all_chunks.extend(chunks)

print("=" * 60)
print(f"Total PDFs    : {len(pdf_files)}")
print(f"Total Chunks  : {len(all_chunks)}")
print("=" * 60)

print("\nSample Chunk\n")

sample = all_chunks[0]

for key, value in sample.items():

    if key == "text":
        print(f"{key}:")
        print(value[:300])
    else:
        print(f"{key}: {value}")