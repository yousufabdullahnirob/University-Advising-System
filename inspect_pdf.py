import pdfplumber

def inspect_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        print("--- TEXT ---")
        print(text[:500])
        print("--- TABLES ---")
        tables = page.extract_tables()
        for table in tables:
            for row in table[:5]:
                print(row)

if __name__ == "__main__":
    inspect_pdf('faculty_list.pdf')
