import pdfplumber

pdf_path = "/Users/mz/PycharmProjects/PythonProject/Main_Match_Program_Results_2021-2025.pdf"
with pdfplumber.open(pdf_path) as pdf:
    for i in range(5, 10):  # pages 6-10 (0-based)
        text = pdf.pages[i].extract_text()
        print(f"--- Page {i+1} ---\n{text}\n")
