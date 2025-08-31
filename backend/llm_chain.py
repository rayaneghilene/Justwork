import time
import logging
from langchain.chains import RetrievalQA
from langchain_mistralai.chat_models import ChatMistralAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_chain(vector_store, api_key: str):
    logger.info("Building LLM chain with Mistral AI...")
    start_time = time.time()
    chain = RetrievalQA.from_chain_type(
        llm=ChatMistralAI(mistral_api_key=api_key),
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        input_key="question"
    )
    logger.info(f"Chain built in {time.time() - start_time:.2f} seconds")
    return chain

def assess_candidate(chain, keywords: str):
    """Pass extracted keywords to the chain to generate an assessment."""
    logger.info("Starting candidate assessment with Mistral AI...")
    start_time = time.time()
    
    prompt = f"Here are extracted keywords from a candidate's resume:\n{keywords}\n\nPlease provide a professional assessment of the candidate's strengths, weaknesses, and job suitability."
    
    result = chain.run(prompt)
    logger.info(f"Assessment completed in {time.time() - start_time:.2f} seconds")
    
    return result