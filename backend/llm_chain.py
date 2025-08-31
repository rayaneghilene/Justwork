from langchain.chains import RetrievalQA
from langchain_mistralai.chat_models import ChatMistralAI

def build_chain(vector_store, api_key: str):
    return RetrievalQA.from_chain_type(
        llm=ChatMistralAI(mistral_api_key=api_key),
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        input_key="question"
    )

def assess_candidate(chain, keywords: str):
    """Pass extracted keywords to the chain to generate an assessment."""
    prompt = f"Here are extracted keywords from a candidate's resume:\n{keywords}\n\nPlease provide a professional assessment of the candidate’s strengths, weaknesses, and job suitability."
    return chain.run(prompt)