# Docker Setup Guide for JustWork

This guide explains how to run JustWork using Docker Compose.

## Quick Start

1. **Set up environment variables:**
   ```bash
   # Create a .env file in the project root
   echo "API_KEY=your_mistral_api_key_here" > .env
   echo "DATA_FOLDER=data" >> .env
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend (Streamlit): http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Environment Variables

### Required
- `API_KEY`: Your Mistral AI API key (get it from https://console.mistral.ai/)

### Optional
- `DATA_FOLDER`: Directory for uploaded PDF files (default: "data")
- `EMBEDDING_MODEL`: HuggingFace embedding model (default: "all-MiniLM-L12-V2")
- `KEYWORD_MODEL`: Keyword extraction model (default: "numind/NuExtract-tiny")

## Docker Services

### Backend (`justwork-backend`)
- **Port:** 8000
- **Purpose:** FastAPI server with AI models
- **Health Check:** GET /
- **Data Volume:** `./data:/app/data`
- **Logs Volume:** `./logs:/app/logs`

### Frontend (`justwork-frontend`)
- **Port:** 8501
- **Purpose:** Streamlit web interface
- **Depends on:** Backend health check
- **Environment:** `BACKEND_URL=http://justwork-backend:8000`

## Networking

Services communicate via the `justwork-network` bridge network:
- Frontend connects to backend using hostname `justwork-backend`
- Both services are accessible from host via port mapping

## Troubleshooting

### Frontend can't connect to backend
1. **Check container logs:**
   ```bash
   docker-compose logs justwork-frontend
   docker-compose logs justwork-backend
   ```

2. **Verify backend health:**
   ```bash
   curl http://localhost:8000/
   ```

3. **Check network connectivity:**
   ```bash
   docker-compose exec justwork-frontend curl -f http://justwork-backend:8000/
   ```

### Backend fails to start
1. **Check API key:**
   - Ensure `.env` file exists with valid `API_KEY`
   - Verify API key works: https://console.mistral.ai/

2. **Check model downloads:**
   - First run downloads models (~1-2GB)
   - Check logs for download progress

3. **Check disk space:**
   - Models require ~2-3GB free space
   - Data uploads need additional space

### Memory issues
1. **Backend requires:**
   - Minimum: 4GB RAM
   - Recommended: 8GB+ RAM
   - GPU support: CUDA-compatible GPU (optional)

2. **Increase Docker memory limits:**
   ```bash
   # Docker Desktop: Settings > Resources > Memory
   # Linux: Edit /etc/docker/daemon.json
   ```

## Advanced Configuration

### Using GPU acceleration
```yaml
# Add to backend service in docker-compose.yml
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all
```

### Custom model paths
```bash
# In .env file
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
KEYWORD_MODEL=microsoft/DialoGPT-large
```

### Production deployment
```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Development

### Run only backend
```bash
docker-compose up justwork-backend
```

### Run with local frontend
```bash
# Start only backend in Docker
docker-compose up justwork-backend

# Run frontend locally
cd frontend
BACKEND_URL=http://localhost:8000 streamlit run app.py
```

### Rebuild after changes
```bash
# Rebuild specific service
docker-compose build justwork-backend
docker-compose up justwork-backend

# Rebuild all services
docker-compose build
docker-compose up
```

## Monitoring

### View real-time logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f justwork-backend
```

### Check service status
```bash
# Service health
docker-compose ps

# Resource usage
docker stats $(docker-compose ps -q)
```

### API endpoints for monitoring
```bash
# Health check
curl http://localhost:8000/

# System status
curl http://localhost:8000/status

# Cache statistics
curl http://localhost:8000/cache-stats
```

## Data Persistence

### Volumes
- `./data:/app/data` - Uploaded PDF files
- `./logs:/app/logs` - Application logs

### Backup
```bash
# Backup uploaded files
tar -czf backup-data-$(date +%Y%m%d).tar.gz data/

# Backup logs
tar -czf backup-logs-$(date +%Y%m%d).tar.gz logs/
```
