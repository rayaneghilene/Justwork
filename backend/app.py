import json
import os
import shutil
import time
import logging
from pathlib import Path
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

from backend.models import (
    KeywordExtractionRequest,
    KeywordExtractionResponse,
    AssessmentRequest,
    AssessmentResponse,
    ResumeUploadResponse,
    CandidateAnalysisRequest,
    CandidateAnalysisResponse,
    HealthResponse
)
from backend.data_loader import load_resumes
from backend.keyword_extractor import predict_keywords, get_cache_stats, clear_cache
from backend.llm_chain import build_chain, assess_candidate

# Load configuration
logger.info("="*60)
logger.info("INITIALIZING JUSTWORK RESUME ANALYSIS API")
logger.info("="*60)

config_path = Path(__file__).parent / "config.json"
logger.info(f"Loading configuration from: {config_path}")

try:
    with open(config_path, "r") as f:
        config = json.load(f)
    logger.info("✓ Configuration loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load configuration: {str(e)}")
    # If config file fails to load, create default config
    config = {
        "api_key": "",
        "data_folder": "data",
        "embedding_model": "all-MiniLM-L12-V2",
        "keyword_model": "numind/NuExtract-tiny"
    }

# Use environment variables with config as fallback
API_KEY = os.getenv("API_KEY") or config["api_key"]
DATA_FOLDER = os.getenv("DATA_FOLDER") or config.get("data_folder", "data")

logger.info(f"✓ API key configured: {'*' * (len(API_KEY) - 4) + API_KEY[-4:] if API_KEY else 'NOT SET'}")
logger.info(f"✓ Data folder: {DATA_FOLDER}")

# Ensure data folder exists
data_path = Path(DATA_FOLDER)
data_path.mkdir(exist_ok=True)
logger.info(f"✓ Data folder ensured: {data_path.absolute()}")

# Default schema for keyword extraction
DEFAULT_SCHEMA = """{
    "Skills": [],
    "Job Titles": [],
    "Education": [],
    "Projects": [],
    "Experience Years": []
}"""

app = FastAPI(
    title="JustWork Resume Analysis API",
    description="API for analyzing resumes using AI-powered keyword extraction and candidate assessment",
    version="1.0.0"
)
logger.info("✓ FastAPI application created")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("✓ CORS middleware configured")

# Global variables to store the vector store and chain
vector_store = None
chain = None

logger.info("✓ Global variables initialized")
logger.info("="*60)

@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info("🚀 FASTAPI APPLICATION STARTING UP")
    logger.info("="*60)
    logger.info("✓ JustWork Resume Analysis API is ready to serve requests")
    logger.info("✓ Available endpoints:")
    logger.info("   • GET    /                       - Health check")
    logger.info("   • GET    /status                 - System status")
    logger.info("   • GET    /cache-stats            - Cache statistics")
    logger.info("   • DELETE /cache                  - Clear keyword cache")
    logger.info("   • POST   /upload-resumes         - Upload PDF files")
    logger.info("   • POST   /extract-keywords       - Extract keywords (cached)")
    logger.info("   • POST   /assess-candidate       - Assess candidate")
    logger.info("   • POST   /analyze-resumes        - Full analysis")
    logger.info("   • POST   /test-performance       - Performance test")
    logger.info("   • POST   /debug-extraction       - Debug extraction issues")
    logger.info("   • POST   /regenerate-vector-store- Regenerate with better chunking")
    logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("🛑 FASTAPI APPLICATION SHUTTING DOWN")
    logger.info("✓ JustWork Resume Analysis API stopped gracefully")
    logger.info("="*60)

def get_vector_store():
    """Dependency to get or create vector store"""
    logger.info("🔗 Vector store dependency called")
    global vector_store
    if vector_store is None:
        logger.info("📦 Vector store not loaded, creating new one...")
        # Check if we have resumes to load
        data_path = Path(DATA_FOLDER)
        if not data_path.exists() or not any(data_path.glob("*.pdf")):
            logger.warning("⚠️  No PDF files found for vector store creation")
            raise HTTPException(
                status_code=400, 
                detail="No PDF resumes found. Please upload resumes first."
            )
        vector_store = load_resumes()
        logger.info("✓ Vector store created and cached")
    else:
        logger.info("✓ Using cached vector store")
    return vector_store

def get_chain():
    """Dependency to get or create LLM chain"""
    logger.info("🔗 LLM chain dependency called")
    global chain
    if chain is None:
        logger.info("🧠 Chain not initialized, creating new one...")
        vs = get_vector_store()
        chain = build_chain(vs, API_KEY)
        logger.info("✓ LLM chain created and cached")
    else:
        logger.info("✓ Using cached LLM chain")
    return chain

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    logger.info("🏥 Health check endpoint called")
    start_time = time.time()
    
    response = HealthResponse(status="healthy", message="JustWork Resume Analysis API is running")
    
    logger.info(f"✓ Health check completed in {time.time() - start_time:.3f}s")
    return response

@app.post("/upload-resumes", response_model=ResumeUploadResponse)
async def upload_resumes(files: List[UploadFile] = File(...)):
    """Upload PDF resume files to the data folder"""
    logger.info("📤 UPLOAD RESUMES ENDPOINT CALLED")
    logger.info("="*50)
    start_time = time.time()
    global vector_store, chain
    
    # Log request details
    logger.info(f"📁 Files received: {len(files)}")
    for i, file in enumerate(files, 1):
        logger.info(f"  [{i}] {file.filename} ({file.content_type})")
    
    # Create data folder if it doesn't exist
    data_path = Path(DATA_FOLDER)
    data_path.mkdir(exist_ok=True)
    logger.info(f"✓ Data folder ready: {data_path}")
    
    # Clear existing files
    existing_files = list(data_path.glob("*.pdf"))
    if existing_files:
        logger.info(f"🗑️  Clearing {len(existing_files)} existing PDF files...")
        for existing_file in existing_files:
            existing_file.unlink()
            logger.info(f"   Deleted: {existing_file.name}")
    
    files_processed = 0
    
    # Validate and save files
    logger.info("📋 Validating and saving files...")
    for i, file in enumerate(files, 1):
        file_start = time.time()
        logger.info(f"  Processing file [{i}/{len(files)}]: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            error_msg = f"File {file.filename} is not a PDF. Only PDF files are supported."
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save the uploaded file
        file_path = data_path / file.filename
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = file_path.stat().st_size / 1024  # KB
            logger.info(f"    ✓ Saved {file.filename} ({file_size:.1f} KB) in {time.time() - file_start:.2f}s")
            files_processed += 1
            
        except Exception as e:
            logger.error(f"    ❌ Failed to save {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save file {file.filename}")
    
    logger.info(f"✓ All files saved successfully: {files_processed} files")
    
    # Reset global variables to force reloading
    logger.info("🔄 Resetting global variables...")
    vector_store = None
    chain = None
    
    # Create vector store with new files
    logger.info("🔮 Creating vector store from uploaded files...")
    vector_creation_start = time.time()
    
    try:
        vector_store = load_resumes()
        vector_store_created = True
        logger.info(f"✓ Vector store created successfully in {time.time() - vector_creation_start:.2f}s")
        
    except Exception as e:
        error_msg = f"Failed to create vector store: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    # Final summary
    total_time = time.time() - start_time
    logger.info("="*50)
    logger.info("UPLOAD PROCESS COMPLETED SUCCESSFULLY")
    logger.info(f"📊 Summary:")
    logger.info(f"   • Files uploaded: {files_processed}")
    logger.info(f"   • Vector store created: {vector_store_created}")
    logger.info(f"   • Total time: {total_time:.2f}s")
    logger.info("="*50)
    
    return ResumeUploadResponse(
        message=f"Successfully uploaded and processed {files_processed} resume(s)",
        files_processed=files_processed,
        vector_store_created=vector_store_created
    )

@app.post("/extract-keywords", response_model=KeywordExtractionResponse)
async def extract_keywords(request: KeywordExtractionRequest):
    """Extract structured keywords from text using AI"""
    logger.info("🔍 EXTRACT KEYWORDS ENDPOINT CALLED")
    logger.info("="*50)
    start_time = time.time()
    
    # Log request details
    text_length = len(request.text)
    schema_preview = request.schema[:100] + "..." if len(request.schema) > 100 else request.schema
    examples_count = len(request.examples) if request.examples else 0
    
    logger.info(f"📝 Request details:")
    logger.info(f"   • Text length: {text_length} characters")
    logger.info(f"   • Schema preview: {schema_preview}")
    logger.info(f"   • Examples provided: {examples_count}")
    
    try:
        logger.info("🤖 Calling NuExtract model for keyword extraction...")
        extraction_start = time.time()
        
        keywords = predict_keywords(
            text=request.text,
            schema=request.schema,
            examples=request.examples
        )
        
        extraction_time = time.time() - extraction_start
        keywords_length = len(keywords)
        
        logger.info(f"✓ Keywords extracted successfully:")
        logger.info(f"   • Extraction time: {extraction_time:.2f}s")
        logger.info(f"   • Result length: {keywords_length} characters")
        logger.info(f"   • Total endpoint time: {time.time() - start_time:.2f}s")
        
        return KeywordExtractionResponse(keywords=keywords)
        
    except Exception as e:
        error_msg = f"Failed to extract keywords: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"   • Failed after {time.time() - start_time:.2f}s")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/assess-candidate", response_model=AssessmentResponse)
async def assess_candidate_endpoint(
    request: AssessmentRequest,
    chain_dep = Depends(get_chain)
):
    """Generate candidate assessment based on extracted keywords"""
    logger.info("👤 ASSESS CANDIDATE ENDPOINT CALLED")
    logger.info("="*50)
    start_time = time.time()
    
    # Log request details
    keywords_length = len(request.keywords)
    keywords_preview = request.keywords[:200] + "..." if len(request.keywords) > 200 else request.keywords
    
    logger.info(f"📝 Request details:")
    logger.info(f"   • Keywords length: {keywords_length} characters")
    logger.info(f"   • Keywords preview: {keywords_preview}")
    
    try:
        logger.info("🧠 Calling Mistral AI for candidate assessment...")
        assessment_start = time.time()
        
        assessment = assess_candidate(chain_dep, request.keywords)
        
        assessment_time = time.time() - assessment_start
        assessment_length = len(assessment)
        
        logger.info(f"✓ Assessment completed successfully:")
        logger.info(f"   • Assessment time: {assessment_time:.2f}s")
        logger.info(f"   • Result length: {assessment_length} characters")
        logger.info(f"   • Total endpoint time: {time.time() - start_time:.2f}s")
        
        return AssessmentResponse(assessment=assessment)
        
    except Exception as e:
        error_msg = f"Failed to assess candidate: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"   • Failed after {time.time() - start_time:.2f}s")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/analyze-resumes", response_model=CandidateAnalysisResponse)
async def analyze_resumes(
    request: CandidateAnalysisRequest = None,
    chain_dep = Depends(get_chain)
):
    """Complete analysis: extract keywords from uploaded resumes and provide assessment"""
    logger.info("🔄 FULL RESUME ANALYSIS ENDPOINT CALLED")
    logger.info("="*60)
    
    try:
        start_time = time.time()
        logger.info("Starting resume analysis...")
        
        # Load resume text from vector store
        if not os.path.exists("vector_store.json"):
            raise HTTPException(
                status_code=400,
                detail="No resumes processed. Please upload resumes first."
            )
        
        load_start = time.time()
        with open("vector_store.json", "r") as f:
            docs = json.load(f)
        
        resume_text = " ".join([doc["page_content"] for doc in docs])
        logger.info(f"Loaded resume text in {time.time() - load_start:.2f} seconds")
        
        # Extract keywords
        keyword_start = time.time()
        logger.info("Starting keyword extraction...")
        keywords = predict_keywords(resume_text, DEFAULT_SCHEMA)
        logger.info(f"Keyword extraction completed in {time.time() - keyword_start:.2f} seconds")
        
        # Generate assessment
        assessment_start = time.time()
        logger.info("Starting candidate assessment...")
        assessment = assess_candidate(chain_dep, keywords)
        logger.info(f"Assessment completed in {time.time() - assessment_start:.2f} seconds")
        
        total_time = time.time() - start_time
        logger.info(f"Total analysis completed in {total_time:.2f} seconds")
        
        return CandidateAnalysisResponse(
            keywords=keywords,
            assessment=assessment
        )
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze resumes: {str(e)}"
        )

@app.get("/status")
async def get_status():
    """Get current system status"""
    logger.info("📊 STATUS ENDPOINT CALLED")
    start_time = time.time()
    
    # Check system components
    data_path = Path(DATA_FOLDER)
    pdf_files = list(data_path.glob("*.pdf")) if data_path.exists() else []
    
    status_info = {
        "vector_store_loaded": vector_store is not None,
        "chain_initialized": chain is not None,
        "data_folder_exists": data_path.exists(),
        "pdf_files_count": len(pdf_files),
        "pdf_files": [f.name for f in pdf_files],
        "vector_store_file_exists": os.path.exists("vector_store.json")
    }
    
    logger.info(f"✓ Status check completed:")
    logger.info(f"   • Vector store loaded: {status_info['vector_store_loaded']}")
    logger.info(f"   • Chain initialized: {status_info['chain_initialized']}")
    logger.info(f"   • PDF files: {status_info['pdf_files_count']}")
    logger.info(f"   • Response time: {time.time() - start_time:.3f}s")
    
    return status_info

@app.get("/cache-stats")
async def get_cache_statistics():
    """Get keyword extraction cache statistics"""
    logger.info("📊 CACHE STATISTICS ENDPOINT CALLED")
    start_time = time.time()
    
    try:
        stats = get_cache_stats()
        
        # Add some additional system info
        try:
            import torch
            device_info = str(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
            torch_version = torch.__version__
        except ImportError:
            device_info = "unknown"
            torch_version = "not installed"
        
        extended_stats = {
            **stats,
            "timestamp": time.time(),
            "system_info": {
                "device_type": device_info.split(":")[0],
                "torch_version": torch_version
            }
        }
        
        logger.info(f"✓ Cache stats retrieved:")
        logger.info(f"   • Cache entries: {stats['cache_size']}")
        logger.info(f"   • Response time: {time.time() - start_time:.3f}s")
        
        return extended_stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")

@app.delete("/cache")
async def clear_keyword_cache():
    """Clear the keyword extraction cache"""
    logger.info("🧹 CLEAR CACHE ENDPOINT CALLED")
    start_time = time.time()
    
    try:
        # Get stats before clearing
        stats_before = get_cache_stats()
        cache_size_before = stats_before['cache_size']
        
        # Clear the cache
        clear_cache()
        
        # Verify clearing
        stats_after = get_cache_stats()
        cache_size_after = stats_after['cache_size']
        
        result = {
            "message": f"Cache cleared successfully",
            "entries_removed": cache_size_before,
            "entries_remaining": cache_size_after,
            "clearing_time": time.time() - start_time
        }
        
        logger.info(f"✓ Cache cleared:")
        logger.info(f"   • Entries removed: {cache_size_before}")
        logger.info(f"   • Time taken: {result['clearing_time']:.3f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@app.post("/test-performance")
async def test_keyword_extraction_performance():
    """Test keyword extraction performance with sample data"""
    logger.info("🚀 PERFORMANCE TEST ENDPOINT CALLED")
    start_time = time.time()
    
    # Sample test data
    test_text = """
    John Doe is a Senior Software Engineer with 5 years of experience in Python, JavaScript, and React.
    He has a Bachelor's degree in Computer Science from MIT and has worked on several machine learning projects.
    His skills include: Python, Django, FastAPI, React, Node.js, PostgreSQL, Docker, Kubernetes, AWS.
    Previous roles: Software Engineer at Google (2020-2022), Full Stack Developer at Facebook (2018-2020).
    """
    
    test_schema = DEFAULT_SCHEMA
    
    try:
        # First call (should be slower - no cache)
        logger.info("🔥 First call (cache miss expected)...")
        first_start = time.time()
        result1 = predict_keywords(test_text, test_schema)
        first_time = time.time() - first_start
        
        # Second call (should be faster - cache hit)
        logger.info("⚡ Second call (cache hit expected)...")
        second_start = time.time()
        result2 = predict_keywords(test_text, test_schema)
        second_time = time.time() - second_start
        
        # Verify results are identical
        results_identical = result1 == result2
        
        # Get cache stats
        cache_stats = get_cache_stats()
        
        performance_report = {
            "test_completed": True,
            "total_test_time": time.time() - start_time,
            "first_call": {
                "time_seconds": first_time,
                "cache_status": "miss",
                "result_length": len(result1)
            },
            "second_call": {
                "time_seconds": second_time, 
                "cache_status": "hit",
                "result_length": len(result2)
            },
            "performance_improvement": {
                "speedup_factor": round(first_time / second_time, 2) if second_time > 0 else "infinite",
                "time_saved_seconds": first_time - second_time,
                "time_saved_percent": round(((first_time - second_time) / first_time) * 100, 1) if first_time > 0 else 0
            },
            "cache_stats": cache_stats,
            "results_identical": results_identical,
            "sample_result_preview": result1[:200] + "..." if len(result1) > 200 else result1
        }
        
        logger.info(f"🎉 Performance test completed:")
        logger.info(f"   • First call: {first_time:.2f}s")
        logger.info(f"   • Second call: {second_time:.2f}s")
        logger.info(f"   • Speedup: {performance_report['performance_improvement']['speedup_factor']}x")
        logger.info(f"   • Time saved: {performance_report['performance_improvement']['time_saved_percent']}%")
        
        return performance_report
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance test failed: {str(e)}")

@app.post("/debug-extraction")
async def debug_keyword_extraction():
    """Debug keyword extraction with actual resume data"""
    logger.info("🐛 DEBUG EXTRACTION ENDPOINT CALLED")
    start_time = time.time()
    
    try:
        # Step 1: Load actual resume data
        if not os.path.exists("vector_store.json"):
            raise HTTPException(
                status_code=400,
                detail="No resumes found. Please upload resumes first."
            )
        
        with open("vector_store.json", "r") as f:
            docs = json.load(f)
        
        # Get some sample chunks for debugging
        sample_chunks = [doc["page_content"] for doc in docs[:10]]  # First 10 chunks
        full_text = " ".join([doc["page_content"] for doc in docs])
        
        logger.info(f"📊 Resume data loaded:")
        logger.info(f"   • Total documents: {len(docs)}")
        logger.info(f"   • Full text length: {len(full_text)} characters")
        logger.info(f"   • Sample chunks: {len(sample_chunks)}")
        
        # Step 2: Test with small sample first
        sample_text = " ".join(sample_chunks[:5])  # Use first 5 chunks
        logger.info(f"🔍 Testing with sample text ({len(sample_text)} chars):")
        logger.info(f"Sample: {sample_text[:200]}...")
        
        # Clear cache to see fresh extraction
        clear_cache()
        
        # Step 3: Extract keywords from sample
        extraction_start = time.time()
        keywords = predict_keywords(sample_text, DEFAULT_SCHEMA)
        extraction_time = time.time() - extraction_start
        
        # Step 4: Parse the result
        try:
            parsed_keywords = json.loads(keywords)
            keywords_valid = True
        except json.JSONDecodeError as e:
            parsed_keywords = {"error": str(e)}
            keywords_valid = False
        
        # Step 5: Create detailed debug report
        debug_report = {
            "debug_completed": True,
            "total_debug_time": time.time() - start_time,
            "data_analysis": {
                "total_documents": len(docs),
                "full_text_length": len(full_text),
                "sample_text_length": len(sample_text),
                "sample_chunks_used": 5,
                "first_chunk_preview": docs[0]["page_content"][:100] + "..." if docs else "No data"
            },
            "extraction_results": {
                "extraction_time": extraction_time,
                "keywords_valid": keywords_valid,
                "keywords_length": len(keywords),
                "parsed_keywords": parsed_keywords
            },
            "text_samples": {
                "chunk_examples": sample_chunks[:3],  # First 3 chunks
                "full_text_preview": full_text[:500] + "..." if len(full_text) > 500 else full_text
            },
            "recommendations": []
        }
        
        # Add recommendations based on findings
        if len(full_text) < 100:
            debug_report["recommendations"].append("Text too short - upload more detailed resumes")
        
        if not keywords_valid:
            debug_report["recommendations"].append("Model output is not valid JSON - check model configuration")
        
        if keywords_valid and all(len(v) == 0 for v in parsed_keywords.values() if isinstance(v, list)):
            debug_report["recommendations"].append("All extracted fields are empty - text may lack clear skill/job information")
        
        chunk_sizes = [len(doc["page_content"]) for doc in docs[:10]]
        avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
        if avg_chunk_size < 50:
            debug_report["recommendations"].append(f"Chunks too small (avg: {avg_chunk_size:.0f} chars) - increase chunk size in data loader")
        
        logger.info(f"🎉 Debug extraction completed:")
        logger.info(f"   • Keywords valid: {keywords_valid}")
        logger.info(f"   • Extraction time: {extraction_time:.2f}s")
        logger.info(f"   • Text length: {len(sample_text)} chars")
        logger.info(f"   • Recommendations: {len(debug_report['recommendations'])}")
        
        return debug_report
        
    except Exception as e:
        logger.error(f"❌ Debug extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug extraction failed: {str(e)}")

@app.post("/regenerate-vector-store")
async def regenerate_vector_store():
    """Regenerate vector store from existing PDF files with improved chunking"""
    logger.info("🔄 REGENERATE VECTOR STORE ENDPOINT CALLED")
    start_time = time.time()
    global vector_store, chain
    
    try:
        # Check if we have PDF files
        data_path = Path(DATA_FOLDER)
        pdf_files = list(data_path.glob("*.pdf"))
        
        if not pdf_files:
            raise HTTPException(
                status_code=400,
                detail="No PDF files found to process. Please upload resumes first."
            )
        
        logger.info(f"📁 Found {len(pdf_files)} PDF files to process:")
        for i, file_path in enumerate(pdf_files, 1):
            logger.info(f"  [{i}] {file_path.name}")
        
        # Reset global variables
        logger.info("🔄 Resetting cached objects...")
        vector_store = None
        chain = None
        
        # Clear keyword extraction cache too
        clear_cache()
        logger.info("✓ All caches cleared")
        
        # Regenerate vector store with improved chunking
        logger.info("🔮 Regenerating vector store with improved chunking...")
        regeneration_start = time.time()
        
        new_vector_store = load_resumes()
        
        if new_vector_store:
            vector_store = new_vector_store
            regeneration_time = time.time() - regeneration_start
            
            # Verify the new vector store
            with open("vector_store.json", "r") as f:
                docs = json.load(f)
            
            chunk_sizes = [len(doc["page_content"]) for doc in docs]
            avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
            min_chunk_size = min(chunk_sizes) if chunk_sizes else 0
            max_chunk_size = max(chunk_sizes) if chunk_sizes else 0
            
            result = {
                "regeneration_completed": True,
                "total_time": time.time() - start_time,
                "regeneration_time": regeneration_time,
                "pdf_files_processed": len(pdf_files),
                "vector_store_stats": {
                    "total_chunks": len(docs),
                    "avg_chunk_size": round(avg_chunk_size, 1),
                    "min_chunk_size": min_chunk_size,
                    "max_chunk_size": max_chunk_size,
                    "total_characters": sum(chunk_sizes)
                },
                "improvements": [
                    f"Chunk size increased from 100 to 1000 characters",
                    f"Added chunk overlap of 100 characters for better context",
                    f"Improved text splitting strategy",
                    f"All caches cleared for fresh processing"
                ]
            }
            
            logger.info(f"✅ Vector store regenerated successfully:")
            logger.info(f"   • Total chunks: {len(docs)}")
            logger.info(f"   • Average chunk size: {avg_chunk_size:.1f} chars")
            logger.info(f"   • Processing time: {regeneration_time:.2f}s")
            
            return result
            
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to regenerate vector store"
            )
    
    except Exception as e:
        logger.error(f"❌ Vector store regeneration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vector store regeneration failed: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Starting server with uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
