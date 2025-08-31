# JustWork Resume Analysis API

A FastAPI-based REST API for analyzing resumes using AI-powered keyword extraction and candidate assessment.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update configuration:**
   Edit `backend/config.json` and add your Mistral API key:
   ```json
   {
     "api_key": "YOUR_MISTRAL_API_KEY",
     "data_folder": "data",
     "embedding_model": "all-MiniLM-L12-V2",
     "keyword_model": "numind/NuExtract-tiny"
   }
   ```

3. **Run the server:**
   ```bash
   # From the project root
   python backend/main.py
   
   # Or using the dedicated runner
   python backend/run_server.py
   
   # For production
   python backend/run_server.py --production
   ```

4. **Access the API:**
   - API Server: http://localhost:8000
   - Interactive Documentation: http://localhost:8000/docs
   - Alternative Documentation: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check
- **GET** `/` - Check if the API is running
- **GET** `/status` - Get detailed system status

### 2. Resume Upload
- **POST** `/upload-resumes` - Upload PDF resume files
  - Accepts multiple PDF files
  - Creates vector embeddings automatically
  - Clears existing files before uploading new ones

### 3. Keyword Extraction
- **POST** `/extract-keywords` - Extract structured keywords from text
  ```json
  {
    "text": "Your resume text here...",
    "schema": "{\"Skills\": [], \"Job Titles\": [], \"Education\": []}",
    "examples": ["optional", "examples", "array"]
  }
  ```

### 4. Candidate Assessment
- **POST** `/assess-candidate` - Generate candidate assessment
  ```json
  {
    "keywords": "Extracted keywords from previous step"
  }
  ```

### 5. Complete Analysis
- **POST** `/analyze-resumes` - Complete end-to-end analysis
  - Extracts keywords from uploaded resumes
  - Generates comprehensive candidate assessment
  - Returns both keywords and assessment

## Example Workflow

1. **Upload Resumes:**
   ```bash
   curl -X POST "http://localhost:8000/upload-resumes" \
        -H "accept: application/json" \
        -H "Content-Type: multipart/form-data" \
        -F "files=@resume1.pdf" \
        -F "files=@resume2.pdf"
   ```

2. **Analyze All Resumes:**
   ```bash
   curl -X POST "http://localhost:8000/analyze-resumes" \
        -H "accept: application/json" \
        -H "Content-Type: application/json" \
        -d "{}"
   ```

3. **Extract Keywords from Custom Text:**
   ```bash
   curl -X POST "http://localhost:8000/extract-keywords" \
        -H "accept: application/json" \
        -H "Content-Type: application/json" \
        -d '{
          "text": "Software engineer with 5 years Python experience...",
          "schema": "{\"Skills\": [], \"Experience Years\": []}"
        }'
   ```

## Features

- **PDF Resume Processing**: Automatically processes PDF resumes and creates vector embeddings
- **AI Keyword Extraction**: Uses NuExtract model for structured keyword extraction
- **Intelligent Assessment**: Uses Mistral AI for comprehensive candidate evaluation
- **RESTful API**: Clean, documented REST endpoints
- **Auto-reload**: Development server with automatic reloading
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error handling and validation

## Data Flow

1. **Upload**: PDF resumes → Vector embeddings (FAISS)
2. **Extract**: Resume text → Structured keywords (NuExtract)
3. **Assess**: Keywords → Candidate assessment (Mistral AI)
4. **Return**: JSON responses with results

## Configuration

The `config.json` file contains:
- `api_key`: Your Mistral AI API key
- `data_folder`: Folder for storing uploaded PDFs
- `embedding_model`: HuggingFace embedding model name
- `keyword_model`: NuExtract model for keyword extraction

## Error Handling

The API includes comprehensive error handling for:
- Missing or invalid files
- API key issues
- Model loading problems
- Processing failures

All errors return structured JSON responses with helpful error messages.
