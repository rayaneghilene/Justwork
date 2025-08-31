import os
import fitz  # PyMuPDF
import ollama


# -------- PDF Extraction --------
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

# -------- LLM Processing --------
def enrich_job_description(text, model="mistral"):
    """Send the job description text to the LLM and get enriched output."""
    prompt = f"""
You are an expert HR analyst. Based on the job description below, fill in all missing details.

Return the result strictly in the following structured format:

job_title
seniority
experience_years_min
experience_years_max
location (with type and timezone_requirement if relevant)
employment_type
department
company: name, industry, product_type, customer_base, market_focus, stage
team: size, structure, collaboration, culture
responsibilities: [array of tasks]
requirements:
  hard_skills: [{{category, skill, importance (1–5)}}]
  soft_skills: [{{skill, importance (1–5)}}]
compensation: {{currency, salary_min, salary_max, equity, insurance, learning_budget, remote, flexible_hours}}
application_process: [array of steps in snake_case]
hidden_expectations: [array of implicit truths about the role]

Normalize hard skills into meaningful categories. Use importance ranking 1–5.

Original job description:
{text}
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# -------- Main Pipeline --------
def process_pdfs(folder, model="mistral"):
    """Process all PDFs in the folder and save enriched job descriptions."""

    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder, filename)
            print(f"Processing {pdf_path}...")

            # Extract text
            raw_text = extract_text_from_pdf(pdf_path)

            # Enrich with LLM
            enriched_text = enrich_job_description(raw_text, model=model)

            # Save output
            output_filename = os.path.splitext(filename)[0] + "_enriched.txt"
            output_path = os.path.join(folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(enriched_text)

            print(f"Saved enriched description to {folder}")

# -------- Run Script --------
if __name__ == "__main__":
    path = os.getcwd() 
    process_pdfs(path, model="mistral")