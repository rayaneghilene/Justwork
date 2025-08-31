# JustWork - AI-Powered Fair Hiring Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> Eliminating unjust discrimination in the job market through AI-powered resume analysis and fair candidate assessment.

## 🎯 Overview

JustWork is dedicated to creating a fair and bias-free job market where every individual is judged by their skills, not by bias. Our AI-powered platform provides tools and frameworks that help employers make fair hiring decisions, increase transparency, and create equal opportunities for all candidates.

### Key Features

- 🤖 **AI-Powered Analysis**: Advanced keyword extraction and candidate assessment using Mistral AI
- 📄 **Resume Processing**: Automated PDF resume processing with vector embeddings
- 🔍 **Skills Extraction**: Structured keyword and skills extraction from resumes
- 📊 **Fair Assessment**: Bias-free candidate evaluation and job matching
- 🚀 **REST API**: Complete RESTful API with interactive documentation
- 🌐 **Web Interface**: User-friendly Streamlit frontend for easy interaction
- 🐳 **Docker Ready**: Containerized deployment for easy scaling

## 📋 Prerequisites

Before getting started, ensure you have:

- **Python 3.8+** installed
- **Git** for cloning the repository
- **Mistral AI API Key** ([Get one here](https://docs.mistral.ai/api/))
- **Docker** (optional, for containerized deployment)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/rayaneghilene/Justwork.git
cd Justwork

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create or update `backend/config.json`:

```json
{
  "api_key": "YOUR_MISTRAL_API_KEY",
  "data_folder": "data",
  "embedding_model": "all-MiniLM-L12-V2",
  "keyword_model": "numind/NuExtract-tiny"
}
```

### 3. Run the Services

#### Option A: Backend API Only
```bash
# Start the FastAPI backend
python backend/main.py

# Or using the dedicated runner
python backend/run_server.py

# For production
python backend/run_server.py --production
```

#### Option B: Full Stack (Backend + Frontend)
```bash
# Terminal 1: Start backend
python backend/main.py

# Terminal 2: Start frontend
cd frontend
streamlit run app.py
```

### 4. Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:8501 (if running Streamlit)

## 🐳 Docker Deployment

### Quick Docker Run

```bash
# Build and run backend only
docker build -t justwork-api .
docker run -p 8000:8000 -e API_KEY=your_mistral_api_key justwork-api
```

### Full Stack with Docker Compose

```bash
# Backend only
docker-compose up --build

# With frontend
docker-compose --profile frontend up --build
```

### Environment Variables for Docker

⚠️ **Security Notice**: Never commit API keys to version control!

```bash
# 1. Copy the environment template
cp env.example .env

# 2. Edit .env with your actual API key
# Replace 'your_mistral_api_key_here' with your real Mistral API key
nano .env
```

Required environment variables:
- `API_KEY`: Your Mistral AI API key (**REQUIRED**)
- `DATA_FOLDER`: Data storage folder (default: data)
- `EMBEDDING_MODEL`: HuggingFace embedding model
- `KEYWORD_MODEL`: Keyword extraction model

## 📚 API Documentation

### Core Endpoints

#### Health & Status
```bash
GET /              # Health check
GET /status        # Detailed system status
```

#### Resume Processing
```bash
POST /upload-resumes     # Upload PDF resumes
POST /analyze-resumes    # Complete resume analysis
```

#### AI Services
```bash
POST /extract-keywords   # Extract structured keywords
POST /assess-candidate   # Generate candidate assessment
```

### Example Usage

#### 1. Upload Resume
```bash
curl -X POST "http://localhost:8000/upload-resumes" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@resume.pdf"
```

#### 2. Analyze Resume
```bash
curl -X POST "http://localhost:8000/analyze-resumes" \
     -H "Content-Type: application/json" \
     -d "{}"
```

#### 3. Extract Keywords
```bash
curl -X POST "http://localhost:8000/extract-keywords" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Software engineer with 5 years Python experience...",
       "schema": "{\"Skills\": [], \"Experience Years\": []}"
     }'
```

## 🌐 Frontend Usage

The Streamlit frontend provides an intuitive interface:

1. **Upload**: Drag & drop or click to upload PDF resumes
2. **Analyze**: Click "Analyze CV & Find Matches" 
3. **Review**: View extracted keywords and job match assessments
4. **Export**: Download results for further processing

### Frontend Features

- 📁 **File Upload**: Support for multiple PDF files
- 📊 **Progress Tracking**: Real-time analysis progress
- 🔍 **Interactive Results**: Expandable keyword and assessment sections
- ⚡ **Real-time Updates**: Live backend health monitoring
- 📱 **Responsive Design**: Works on desktop and mobile

## ⚙️ Configuration Options

### Basic Configuration (`backend/config.json`)

```json
{
  "api_key": "your_mistral_api_key",
  "data_folder": "data",
  "embedding_model": "all-MiniLM-L12-V2",
  "keyword_model": "numind/NuExtract-tiny"
}
```

### Advanced Environment Variables

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# File Processing
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf

# Caching
ENABLE_KEYWORD_CACHE=true
CACHE_TTL_SECONDS=3600
```

### Environment Setup Helper

Use the included setup script for easy configuration:

```bash
python setup_env.py
```

This script will:
- Create environment variable templates
- Update configuration files
- Check Docker setup
- Provide deployment commands

## 🏗️ Project Structure

```
JustWork/
├── backend/                 # FastAPI backend
│   ├── app.py              # FastAPI application
│   ├── main.py             # Application entry point
│   ├── run_server.py       # Production server runner
│   ├── data_loader.py      # PDF processing and embeddings
│   ├── keyword_extractor.py # AI keyword extraction
│   ├── llm_chain.py        # LLM integration
│   ├── models.py           # Pydantic models
│   └── config.json         # Configuration file
├── frontend/               # Streamlit frontend
│   ├── app.py              # Main Streamlit app
│   └── README.md           # Frontend documentation
├── data/                   # Uploaded resumes storage
├── logs/                   # Application logs
├── docker-compose.yml      # Multi-service deployment
├── Dockerfile              # Backend container
├── Dockerfile.frontend     # Frontend container
├── requirements.txt        # Python dependencies
├── setup_env.py           # Environment setup helper
├── DEPLOYMENT.md          # Detailed deployment guide
└── README.md              # This file
```

## 🔧 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Verify API key configuration
cat backend/config.json

# Check dependencies
pip list | grep fastapi
```

#### Upload Fails
```bash
# Check file permissions
ls -la data/

# Verify file size (must be < 10MB by default)
ls -lh your-resume.pdf

# Check backend logs
tail -f backend.log
```

#### Model Loading Issues
```bash
# Clear model cache
rm -rf ~/.cache/huggingface/

# Check internet connection for model downloads
ping huggingface.co

# Verify disk space for model storage
df -h
```

#### Docker Issues
```bash
# Check Docker status
docker ps

# View container logs
docker logs justwork-backend

# Rebuild containers
docker-compose down && docker-compose up --build
```

### Security Issues

#### Missing API Key
```bash
# Check if .env file exists and contains API_KEY
cat .env | grep API_KEY

# Verify environment variable is loaded
echo $API_KEY

# For Docker: check if .env is in same directory as docker-compose.yml
ls -la .env docker-compose.yml
```

#### Environment Variable Not Loading
```bash
# Make sure .env is in project root
cp env.example .env

# Check Docker Compose reads .env correctly
docker-compose config

# Restart containers after .env changes
docker-compose down && docker-compose up
```

### Performance Optimization

- **First Request**: May be slower due to model loading (this is normal)
- **Memory Usage**: Monitor with large PDF files
- **Caching**: Enable keyword caching for better performance
- **Model Selection**: Consider smaller models for faster inference

## 🚀 Deployment Options

### 1. Local Development
- Use `python backend/main.py` for development
- Automatic reload enabled
- Ideal for testing and development

### 2. Production Server
- Use `python backend/run_server.py --production`
- Optimized for production workloads
- Better error handling and logging

### 3. Docker Deployment
- Single service: `docker-compose up`
- Full stack: `docker-compose --profile frontend up`
- Scalable and portable

### 4. Cloud Deployment
- **Supabase**: See `DEPLOYMENT.md` for detailed instructions
- **AWS/GCP/Azure**: Use Docker containers
- **Heroku**: Git-based deployment ready

## 📊 Example Output

### Candidate Assessment Sample

```text
Candidate Assessment:
Based on the information provided, this candidate has a strong skillset in machine learning, 
with expertise in various algorithms, modeling techniques, and tools. Their current position 
as a Senior Data Scientist demonstrates their ability to apply these skills professionally.

Strengths:
- Proficient in machine learning techniques (regression, recommender systems, time series)
- Strong background in Python and SQL
- Experience with cloud platforms (Google Cloud Platform)
- Familiar with various databases (BigQuery, MySQL, ClickHouse, PostgreSQL)

Job Suitability:
Given the candidate's strong background in machine learning and data science, they appear 
well-suited for roles involving data analysis, modeling, and machine learning engineering.
```

## 🔒 Security Best Practices

### Environment Variables
- **Never commit** `.env` files or API keys to version control
- Use `env.example` as a template for required variables
- Store sensitive data in environment variables, not config files
- Regularly rotate API keys and access tokens

### Production Deployment
- Use secrets management systems (AWS Secrets Manager, Azure Key Vault, etc.)
- Enable HTTPS/TLS for all API endpoints
- Implement rate limiting and request validation
- Monitor for suspicious API usage patterns

### API Key Management
```bash
# Good: Using environment variables
export API_KEY="your-secure-api-key"

# Bad: Hardcoding in files
api_key = "hardcoded-key-in-source"  # DON'T DO THIS
```

### Docker Security
- Use multi-stage builds to reduce attack surface
- Run containers as non-root users when possible
- Scan images for vulnerabilities regularly
- Use Docker secrets for sensitive data in swarm mode

## 🤝 Contributing

We welcome contributions to enhance JustWork! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure Docker builds work
- Test both frontend and backend changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Support

For questions, issues, or feedback:

- **Email**: rayane.ghilene@ensea.fr
- **Issues**: Open a GitHub issue
- **Documentation**: Check `DEPLOYMENT.md` for detailed guides

## 🌟 Vision

Our vision is a global job market where talent is recognized without prejudice, and workplaces reflect the richness of human diversity. Through AI-powered fair hiring practices, we're building a future where every candidate has an equal opportunity to showcase their skills and potential.

---

**Made with ❤️ for fair hiring and equal opportunities**