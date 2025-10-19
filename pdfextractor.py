import pdfplumber
import csv

# Path to your PDF file
pdf_path = "/Users/mz/PycharmProjects/PythonProject/Split-2024-Main-Match-Results-and-Data-Final.pdf"
output_csv = "/Users/mz/PycharmProjects/PythonProject/residency_data.csv"

# Open the PDF
with pdfplumber.open(pdf_path) as pdf:
    data = []
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            data.append(text)

# Write the extracted data to a CSV file
with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Program", "Specialty", "Code", "Quota", "Matched", "Unfilled"])  # Header row
    for line in data:
        # Process each line and split into columns (customize this based on the PDF structure)
        parts = line.split()  # Adjust delimiter logic here
        writer.writerow(parts)

print(f"Data extracted and saved to {output_csv}")