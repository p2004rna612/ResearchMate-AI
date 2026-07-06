from pathlib import Path
from utils.pdf_loader import load_pdf

pdf_folder = Path("data/documents")

pdf_files = list(pdf_folder.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found!")
    exit()

for pdf in pdf_files:
    print("=" * 60)
    print(f"Loading: {pdf.name}")

    pages = load_pdf(pdf)

    print(f"Pages extracted: {len(pages)}")

    if pages:
        print("\nFirst Page:")
        print("-" * 60)
        print(pages[0]["text"][:500])   # Print first 500 characters
        print("\n")