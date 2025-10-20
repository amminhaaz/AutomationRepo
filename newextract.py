import pdfplumber
import pandas as pd
import re

pdf_path = "/Users/mz/PycharmProjects/PythonProject/Main_Match_Program_Results_2021-2025.pdf"
excel_path = "Main_Match_Program_Results_2021-2025.xlsx"

YEARS = [2025, 2024, 2023, 2022, 2021]
columns = ["State", "City", "Hospital", "Program", "Code"]
for year in YEARS:
    columns += [f"{year} Quota", f"{year} Filled"]

def extract_program_data():
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        state = city = hospital = None
        for page in pdf.pages[5:]:
            lines = page.extract_text().split("\n")
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Detect state (all caps, not a header)
                if re.match(r"^[A-Z .&'-]+$", line) and len(line) > 2 and not line.startswith("Program Results"):
                    state = line.title()
                    i += 1
                    continue
                # Detect hospital/location (ends with -ST, -CA, etc.)
                if re.match(r"^[A-Za-z0-9 .&'\-/]+-[A-Z]{2}$", line):
                    hospital = line
                    # Next line is often city, but not always
                    if i+1 < len(lines):
                        next_line = lines[i+1].strip()
                        # If next line is not a header or program, treat as city
                        if re.match(r"^[A-Za-z .&'\-/]+Program$", next_line):
                            city = next_line.replace(" Program","").strip()
                            i += 2
                        elif not next_line.startswith("Code") and not re.match(r"^([A-Za-z0-9 /&'\-()]+)\s+([0-9A-Z]{9,10})\s+(.+)$", next_line):
                            city = next_line
                            i += 2
                        else:
                            city = None
                            i += 1
                    else:
                        city = None
                        i += 1
                    # Skip header lines
                    while i < len(lines) and not lines[i].startswith("Code"):
                        i += 1
                    i += 1
                    continue
                # If line is a city (not hospital, not program, not header)
                if city is None and not line.startswith("Code") and not re.match(r"^([A-Za-z0-9 /&'\-()]+)\s+([0-9A-Z]{9,10})\s+(.+)$", line) and not re.match(r"^[A-Z .&'-]+$", line):
                    city = line
                    i += 1
                    continue
                # Parse program line
                prog_match = re.match(r"^([A-Za-z0-9 /&'\-()]+)\s+([0-9A-Z]{9,10})\s+(.+)$", line)
                if prog_match:
                    program, code, rest = prog_match.groups()
                    values = re.findall(r"(\d+|--)\s+(\d+|--)", rest)
                    while len(values) < len(YEARS):
                        values.append(("--","--"))
                    row = [state, city, hospital, program, code]
                    for quota, filled in values[:len(YEARS)]:
                        row.append(quota if quota != "--" else None)
                        row.append(filled if filled != "--" else None)
                    rows.append(row)
                i += 1
    return rows

data = extract_program_data()
df = pd.DataFrame(data, columns=columns)
df.to_excel(excel_path, index=False)
print(f"Extraction complete! Data saved to {excel_path}")