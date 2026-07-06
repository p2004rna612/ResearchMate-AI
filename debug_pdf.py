import pdfplumber

pdf_path = "data/documents/sample.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print("Total pages:", len(pdf.pages))

    first_page = pdf.pages[0]

    text = first_page.extract_text()

    print(text)