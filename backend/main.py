import json
from pathlib import Path
from backend import load_resumes, predict_keywords, build_chain, assess_candidate

# Load configuration
with open(Path(__file__).parent / "config.json", "r") as f:
    config = json.load(f)

API_KEY = config["api_key"]
schema = """{
    "Skills": [],
    "Job Titles": [],
    "Education": [],
    "Projects": [],
    "Experience Years": []
}"""

def main():
    # Step 1: Load resumes
    vector_store = load_resumes()

    # Step 2: Extract keywords
    with open("vector_store.json", "r") as f:
        docs = json.load(f)
    resume_text = " ".join([doc["page_content"] for doc in docs])

    keywords = predict_keywords(resume_text, schema)
    print("\nExtracted Keywords:\n", keywords)

    # Step 3: Build chain
    chain = build_chain(vector_store, API_KEY)

    # Step 4: Assessment
    assessment = assess_candidate(chain, keywords)
    print("\nCandidate Assessment:\n", assessment)

if __name__ == "__main__":
    main()