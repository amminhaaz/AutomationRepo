import pdfplumber
import pandas as pd
import re

pdf_path = "/Users/mz/PycharmProjects/PythonProject/Main_Match_Program_Results_2021-2025.pdf"
excel_path = "Main_Match_Program_Results_2021-2025.xlsx"

YEARS = [2025, 2024, 2023, 2022, 2021]
columns = ["State", "City", "Hospital", "Program", "Code"]
for year in YEARS:
    columns += [f"{year} Quota", f"{year} Filled"]

US_STATES = set([
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
])

def clean_city(line):
    line = re.sub(r"Program.*", "", line)
    line = re.sub(r"\b(?:2025|2024|2023|2022|2021)\b", "", line)
    return line.strip()

def is_state(line):
    return line.title() in US_STATES

def is_program(line):
    return re.match(r"^(.+?)\s+([0-9A-Z]{9,10})\s+(.+)$", line)

def is_header(line):
    return line.startswith("Code") or re.match(r"^\d{4}(?: \d{4})*", line)

def is_footer(line):
    return "Reproduction prohibited" in line or re.match(r"Page \d+ of \d+", line)

def extract_program_data():
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        state = city = hospital = None
        for page in pdf.pages[5:]:
            lines = page.extract_text().split("\n")
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if is_footer(line):
                    i += 1
                    continue
                # Detect state
                if is_state(line):
                    state = line.title()
                    city = None
                    hospital = None
                    i += 1
                    continue
                # Skip headers
                if is_header(line):
                    i += 1
                    continue
                # Detect hospital header (not state, not header, not program, next line is city)
                if (not is_program(line) and not is_state(line) and not is_header(line)
                    and i+1 < len(lines) and re.match(r"^[A-Za-z .&'\-/]+Program.*$", lines[i+1].strip())):
                    hospital = line
                    city = clean_city(lines[i+1].strip())
                    i += 2
                    continue
                # Detect city (not state, not header, not program, next line is program)
                if (not is_program(line) and not is_state(line) and not is_header(line)
                    and i+1 < len(lines) and is_program(lines[i+1].strip())):
                    city = clean_city(line)
                    # Find previous hospital
                    j = i-1
                    while j >= 0:
                        prev = lines[j].strip()
                        if not is_state(prev) and not is_header(prev) and not is_program(prev) and not is_footer(prev):
                            hospital = prev
                            break
                        j -= 1
                    i += 1
                    continue
                # Parse program line
                if is_program(line):
                    prog_match = re.match(r"^(.+?)\s+([0-9A-Z]{9,10})\s+(.+)$", line)
                    if prog_match:
                        program, code, rest = prog_match.groups()
                        # Handle multi-line program names (if next line is not a code but not a header/footer)
                        if (i+1 < len(lines) and not is_header(lines[i+1].strip()) and not is_program(lines[i+1].strip()) and not is_state(lines[i+1].strip()) and not is_footer(lines[i+1].strip())):
                            program += " " + lines[i+1].strip()
                            i += 1
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