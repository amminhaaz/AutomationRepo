import pdfplumber
import pandas as pd
import re


# Path to your local PDF file
pdf_path = "/Users/mz/PycharmProjects/PythonProject/Split-2024-Main-Match-Results-and-Data-Final.pdf"  # Update this path

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                data.append(text)
    return "\n".join(data)

# Process extracted text
def process_match_data(text):
    lines = text.split("\n")
    structured_data = []
    current_hospital = ""
    current_location = ""

    for line in lines:
        line = line.strip()

        # Identify hospital and location
        hospital_match = re.match(r"^(.*?)\s*-\s*([A-Z]{2})$", line)
        if hospital_match:
            current_hospital, current_location = hospital_match.groups()
            continue

        # Extract program details (Program, Code, Quota, Matched)
        parts = line.split()
        if len(parts) >= 4:
            try:
                quota = int(parts[-2])
                matched = int(parts[-1])
                unfilled = quota - matched
                code = parts[-3]  # Extract program code
                program = " ".join(parts[:-3])  # Extract program name

                structured_data.append([current_hospital, current_location, program, code, quota, matched, unfilled])
            except ValueError:
                continue  # Skip lines that don't match expected format

    return structured_data

# Extract text from PDF
full_text = extract_text_from_pdf(pdf_path)

# Process and structure the match data
match_data = process_match_data(full_text)

# Convert to DataFrame
df = pd.DataFrame(match_data, columns=["Hospital", "Location", "Program", "Code", "Quota", "Matched", "Unfilled"])

# Save to Excel
excel_path = "Match_2024_Complete_Data.xlsx"  # Update path as needed
df.to_excel(excel_path, index=False)

print(f"Extraction complete! Data saved to {excel_path}")
