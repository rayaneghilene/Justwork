from Job_Database import JobDatabase

def exec_JobDatabase():
    # load job description
    with open("job_description.txt", "r", encoding="utf-8") as f:
        job_description = f.read()

    # load instructions
    with open("instructions.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    # your OpenRouter API key
    API_KEY = "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"

    # create instance of HiringDb
    db = JobDatabase(api_key=API_KEY)

    # generate JSON and insert into DB
    job_json = db.generate_json(job_description, instructions)
    if job_json:
        db.populate_db()


