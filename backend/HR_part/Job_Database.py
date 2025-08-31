import re
import json
import requests
import pandas as pd
import sqlite3

class JobDatabase:
    def __init__(self, api_key: str, db_path: str = "demo.db"):
        self.api_key = api_key
        self.db_path = db_path
        self.job = None   

        # ensure table exists
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            seniority TEXT,
            experience_years_min INTEGER,
            experience_years_max INTEGER,
            location TEXT,
            employment_type TEXT,
            department TEXT,
            company TEXT,
            team TEXT,
            responsibilities TEXT,
            requirements TEXT,
            compensation TEXT,
            application_process TEXT,
            hidden_expectations TEXT
        )
        """)
        conn.commit()
        cur.close()
        conn.close()

    def generate_json(self, job_description: str, instructions: str):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": job_description}
            ]
        }

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        response = resp.json()

        raw = response["choices"][0]["message"]["content"]

        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in response")

        json_str = match.group(0)

        try:
            data = json.loads(json_str)
            self.job = data
            print("JSON valid and loaded:", data)
            return data
        except json.JSONDecodeError as e:
            print("Invalid JSON:", e)
            return None

    def populate_db(self):
        if not self.job:
            raise ValueError("No job data available. Run generate_json() first.")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("PRAGMA table_info(jobs);")
        columns = [row[1] for row in cur.fetchall() if row[1] != "id"]

        flat = {}
        for k, v in self.job.items():
            if isinstance(v, (dict, list)):
                flat[k] = json.dumps(v)
            else:
                flat[k] = v

        valid_keys = [k for k in flat.keys() if k in columns]

        if valid_keys:
            placeholders = ", ".join("?" for _ in valid_keys)
            col_names = ", ".join(valid_keys)
            values = [flat[k] for k in valid_keys]

            sql = f"INSERT INTO jobs ({col_names}) VALUES ({placeholders})"
            cur.execute(sql, values)
            conn.commit()

        df = pd.read_sql("SELECT * FROM jobs", conn)
        print(df.to_string())

        cur.close()
        conn.close()
