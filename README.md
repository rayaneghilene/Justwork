# Justwork
This project is dedicated to eliminating unjust discrimination in the job market and ensuring that every individual is judged by their skills, not by bias. We design tools, frameworks, and practices that help employers make fair decisions, increase transparency in hiring, and create equal opportunities for all.

By addressing hidden barriers and promoting inclusive policies, the project supports both job seekers and organizations. It empowers candidates from diverse backgrounds to access opportunities with dignity, while helping employers build stronger, fairer, and more innovative teams.

The vision is a global job market where talent is recognized without prejudice, and workplaces reflect the richness of human diversity.


## Installation

Clone the repo using the following command:
```ruby
git clone https://github.com/rayaneghilene/Justwork.git
cd Justwork
```

We recommend creating a virtual environment (optional):
```bash
python3 -m venv myenv
source myenv/bin/activate 
```

To install the requirements run the following command: 
```
pip install -r requirements.txt
```

## Testing
Add your documents in the data folder (not the most efficient but works for now) and run the following 

```python 
python -m backend.main  
```


### Project structure
```
backend/
│── __init__.py          # Makes everything importable from backend
│── config.json          # Config file for API key, paths, models
│── data_loader.py
│── keyword_extractor.py
│── llm_chain.py
│── main.py
│── data/
```

The config.json file should be as follows, You should add your unique mistral Api Key. Read more at https://docs.mistral.ai/api/

```json
{
  "api_key": "YOUR_MISTRAL_API_KEY",
  "data_folder": "data",
  "embedding_model": "all-MiniLM-L12-V2",
  "keyword_model": "numind/NuExtract-tiny"
}
```


## Example Candidate Assesment:

```text
Candidate Assessment:
 Based on the information provided, this candidate has a strong skillset in machine learning, with expertise in various algorithms, modeling techniques, and tools. Their current position as a Senior Data Scientist and their experience with companies like EX.CORP demonstrate their ability to apply these skills in a professional setting.

Strengths:
- Proficient in a wide range of machine learning techniques, including regression, recommender systems, and time series analysis.
- Strong background in Python and SQL, which are commonly used in data science and machine learning roles.
- Experience working with various databases and data storage systems, such as Google BigQuery, MySQL, ClickHouse, and PostgreSQL.
- Familiarity with cloud platforms, like Google Cloud Platform, and tools for ETL pipelines, version control, and CI/CD.

Weaknesses:
- While the candidate has a diverse skillset, it's not clear if they have deep expertise in any specific area. This might be an opportunity for further growth and development.
- There's no mention of experience with Retrieval-Augmented Generation (RAG) or ML System Design related to personalization and recommender systems mentioned in the context, which could be a potential gap if those are crucial for the role.

Job suitability:
Given the candidate's strong background in machine learning, data science, and various tools and techniques, they appear to be well-suited for roles involving data analysis, modeling, and machine learning engineering. However, without more information about the specific requirements of the job, it's difficult to make a definitive assessment of their suitability. As a Senior Data Scientist with experience in various industries, this candidate could bring valuable insights and expertise to a team focused on investment opportunities or other data-driven projects.
```



## Contributing
We welcome contributions from the community to enhance work. 
If you have ideas for features, improvements, or bug fixes, please submit a pull request or open an issue on GitHub.


## Support
For any questions, issues, or feedback, please reach out to rayane.ghilene@ensea.fr
