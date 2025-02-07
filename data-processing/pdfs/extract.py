##Extraction of data##

import PyPDF2
import pandas as pd
import json
import os
from tabulate import tabulate


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyPDF2"""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {str(e)}")
        return None
    return text.strip()


# -------------------------- file 1 --------------------------
def process_sample1(text):
    """Process sample-1.pdf"""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    return {
        "document_type": "product_brochure",
        "company": lines[0] if len(lines) > 0 else "",
        "address": lines[1] if len(lines) > 1 else "",
        "city": lines[2].split(",")[0].strip() if len(lines) > 2 else "",
        "state": lines[2].split(",")[1].strip().split()[0] if len(lines) > 2 else "",
        "zip": lines[2].split(",")[1].strip().split()[1] if len(lines) > 2 else "",
        "phone": lines[3] if len(lines) > 3 else "",
        "date": lines[5] if len(lines) > 5 else "",
        "product_overview": " ".join(lines[7:12]),
        "details": " ".join(lines[12:])
    }


# -------------------------- FILE 2 --------------------------
def process_sample2(text):
    """Process sample-2.pdf"""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    return {
        "document_type": "letter",
        "sender_name": lines[0] if len(lines) > 0 else "",
        "sender_address": lines[1] if len(lines) > 1 else "",
        "sender_city": lines[2].split(",")[0].strip() if len(lines) > 2 else "",
        "sender_state": lines[2].split(",")[1].strip().split()[0] if len(lines) > 2 else "",
        "sender_zip": lines[2].split(",")[1].strip().split()[1] if len(lines) > 2 else "",
        "sender_phone": lines[3].replace("(", "").replace(")", "").replace("-", "") if len(lines) > 3 else "",
        "sender_email": lines[4] if len(lines) > 4 else "",
        "date": lines[5] if len(lines) > 5 else "",
        "recipient_name": lines[6] if len(lines) > 6 else "",
        "recipient_role": lines[7].split(",")[0].strip() if len(lines) > 7 else "",
        "recipient_company": lines[7].split(",")[1].strip() if len(lines) > 7 else "",
        "recipient_address": lines[8] if len(lines) > 8 else "",
        "letter_body": " ".join(lines[9:])
    }


# -------------------------- file 3 --------------------------
def process_sample3(text):
    """Process sample3.pdf"""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Extract personal information
    personal_info = {
        "name": lines[1].replace("I'm ", "") if len(lines) > 1 else "",
        "address": lines[2] if len(lines) > 2 else "",
        "city": lines[3].split(",")[0].strip() if len(lines) > 3 else "",
        "state": lines[3].split(",")[1].strip()[:2] if len(lines) > 3 else "",
        "zip": lines[3].split(",")[1].strip()[2:] if len(lines) > 3 else "",
        "phone": lines[4].replace("(", "").replace(")", "").replace("-", "") if len(lines) > 4 else "",
        "email": lines[5] if len(lines) > 5 else "",

    }

    # Extract sections
    sections = {
        "skills": " ".join(lines[7:9]),
        "experience":  " ".join(lines[12:35]),
        "education": "".join(lines[36:41]),
        "awards": "".join(lines[41:])
    }

    current_section = None
    experience_entry = {}

    for line in lines[6:]:
        if line.lower() in [k.lower() for k in sections.keys()]:
            current_section = line.lower()
            if current_section == "experience":
                experience_entry = {}
        else:
            if current_section == "experience":
                if line.count("-") > 0 and len(line) > 10:
                    if experience_entry:
                        sections["experience"].append(experience_entry)
                    parts = line.split("-")
                    experience_entry = {
                        "dates": parts[0].strip(),
                        "company": parts[1].split(",")[0].strip(),
                        "location": parts[1].split(",")[1].split("-")[0].strip(),
                        "title": parts[-1].strip(),
                        "details": []
                    }
                elif experience_entry:
                    if line.startswith("-"):
                        experience_entry["details"].append(line[1:].strip())
                    else:
                        experience_entry["details"].append(line)
            elif current_section:
                sections[current_section].append(line)

    if experience_entry:
        sections["experience"].append(experience_entry)

    return {
        "document_type": "resume",
        **personal_info,
        "skills": " ".join(sections["skills"]),
        "experience": sections["experience"],
        "education": " ".join(sections["education"]),
        "awards": " ".join(sections["awards"])
    }


# -------------------------- MAIN PROCESSOR --------------------------
def process_pdf(pdf_path):
    """Process PDF file and save outputs"""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    filename = os.path.basename(pdf_path).lower()
    processor_map = {
        "sample-1.pdf": process_sample1,
        "sample-2.pdf": process_sample2,
        "sample-3.pdf": process_sample3
    }

    if filename not in processor_map:
        print(f"Skipping unknown document: {filename}")
        return None

    try:
        data = processor_map[filename](text)

        # Create output directory
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON
        json_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)

        # Create and save DataFrame
        flat_data = flatten_data(data) if filename == "sample3.pdf" else data
        df = pd.DataFrame([flat_data])
        #csv_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.csv")
        #df.to_csv(csv_path, index=False)

        # Print formatted table
        print(f"\nProcessed {filename}:")
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
        print(f"Outputs saved to:\n- {json_path}")

        return data

    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None


def flatten_data(data):
    """Flatten nested structures for CSV output"""
    flat = {k: v for k, v in data.items() if not isinstance(v, (list, dict))}

    # Handle experience
    for i, exp in enumerate(data.get("experience", []), 1):
        flat[f"exp_{i}_dates"] = exp.get("dates", "")
        flat[f"exp_{i}_company"] = exp.get("company", "")
        flat[f"exp_{i}_title"] = exp.get("title", "")
        flat[f"exp_{i}_details"] = "\n".join(exp.get("details", []))

    # Handle other list fields
    for field in ["skills", "education", "awards"]:
        flat[field] = data.get(field, "").replace("\n", "; ")

    return flat


if __name__ == "__main__":
    input_dir = "D://pythontest//data-driven-software-engineer-evaluation//data-processing//pdfs"
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            process_pdf(pdf_path)