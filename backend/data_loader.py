import json
from glob import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_FOLDER_PATH = "data"

def load_resumes():
    pdf_files = glob(f"{DATA_FOLDER_PATH}/*.pdf")
    loaders = [PyPDFLoader(file_path) for file_path in pdf_files]

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L12-V2")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)

    docs = []
    for loader in loaders:
        docs.extend(text_splitter.split_documents(loader.load()))

    vector_store = FAISS.from_documents(docs, embedding=embeddings)

    # save docs metadata
    docs_data = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    with open("vector_store.json", "w") as f:
        json.dump(docs_data, f, indent=2)

    return vector_store