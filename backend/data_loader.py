import json
import time
import logging
from glob import glob
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config for data folder path
config_path = Path(__file__).parent / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

DATA_FOLDER_PATH = config.get("data_folder", "data")
logger.info(f"Data folder configured: {DATA_FOLDER_PATH}")

def load_resumes():
    """Load and process PDF resumes into a vector store with detailed logging"""
    logger.info("="*50)
    logger.info("STARTING RESUME LOADING PROCESS")
    logger.info("="*50)
    start_time = time.time()
    
    # Step 1: Find PDF files
    logger.info("Step 1: Scanning for PDF files...")
    scan_start = time.time()
    pdf_files = glob(f"{DATA_FOLDER_PATH}/*.pdf")
    logger.info(f"✓ Found {len(pdf_files)} PDF files in {time.time() - scan_start:.2f}s")
    
    if not pdf_files:
        logger.warning("⚠️  No PDF files found!")
        return None
    
    for i, file_path in enumerate(pdf_files, 1):
        logger.info(f"  [{i}] {Path(file_path).name}")
    
    # Step 2: Initialize components
    logger.info("Step 2: Initializing processing components...")
    init_start = time.time()
    
    loaders = [PyPDFLoader(file_path) for file_path in pdf_files]
    logger.info(f"✓ Created {len(loaders)} PDF loaders")
    
    logger.info("✓ Loading embedding model (all-MiniLM-L12-V2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L12-V2")
    logger.info("✓ Embedding model loaded")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,        # Increased from 100 to 1000 for better context
        chunk_overlap=100,      # Added overlap to maintain context
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]  # Better splitting
    )
    logger.info("✓ Text splitter initialized (chunk_size=1000, overlap=100)")
    logger.info(f"✓ All components initialized in {time.time() - init_start:.2f}s")

    # Step 3: Process documents
    logger.info("Step 3: Processing PDF documents...")
    process_start = time.time()
    docs = []
    
    for i, loader in enumerate(loaders, 1):
        file_start = time.time()
        file_name = Path(pdf_files[i-1]).name
        logger.info(f"  Processing file [{i}/{len(loaders)}]: {file_name}")
        
        try:
            raw_docs = loader.load()
            logger.info(f"    ✓ Loaded {len(raw_docs)} pages")
            
            split_docs = text_splitter.split_documents(raw_docs)
            docs.extend(split_docs)
            logger.info(f"    ✓ Split into {len(split_docs)} chunks")
            logger.info(f"    ✓ File processed in {time.time() - file_start:.2f}s")
            
        except Exception as e:
            logger.error(f"    ❌ Failed to process {file_name}: {str(e)}")
            continue
    
    total_chunks = len(docs)
    logger.info(f"✓ Total document processing completed: {total_chunks} chunks in {time.time() - process_start:.2f}s")

    # Step 4: Create vector store
    logger.info("Step 4: Creating FAISS vector store...")
    vector_start = time.time()
    
    try:
        vector_store = FAISS.from_documents(docs, embedding=embeddings)
        logger.info(f"✓ Vector store created with {total_chunks} documents in {time.time() - vector_start:.2f}s")
    except Exception as e:
        logger.error(f"❌ Failed to create vector store: {str(e)}")
        raise

    # Step 5: Save metadata
    logger.info("Step 5: Saving document metadata...")
    save_start = time.time()
    
    try:
        docs_data = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        with open("vector_store.json", "w") as f:
            json.dump(docs_data, f, indent=2)
        
        file_size = Path("vector_store.json").stat().st_size / 1024  # KB
        logger.info(f"✓ Metadata saved to vector_store.json ({file_size:.1f} KB) in {time.time() - save_start:.2f}s")
    except Exception as e:
        logger.error(f"❌ Failed to save metadata: {str(e)}")
        raise

    # Summary
    total_time = time.time() - start_time
    logger.info("="*50)
    logger.info("RESUME LOADING COMPLETED SUCCESSFULLY")
    logger.info(f"📊 Summary:")
    logger.info(f"   • Files processed: {len(pdf_files)}")
    logger.info(f"   • Total chunks: {total_chunks}")
    logger.info(f"   • Total time: {total_time:.2f}s")
    logger.info(f"   • Average per file: {total_time/len(pdf_files):.2f}s")
    logger.info("="*50)

    return vector_store