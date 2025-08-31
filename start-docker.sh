#!/bin/bash

# JustWork Docker Compose Startup Script
# This script helps you get started with JustWork using Docker

set -e  # Exit on any error

echo "🚀 JustWork Docker Setup Script"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Function to use docker-compose or docker compose
docker_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

echo "✅ Docker and Docker Compose are available"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# JustWork Environment Configuration
API_KEY=your_mistral_api_key_here
DATA_FOLDER=data
EMBEDDING_MODEL=all-MiniLM-L12-V2
KEYWORD_MODEL=numind/NuExtract-tiny
EOF
    echo "✅ Created .env file"
    echo "⚠️  IMPORTANT: Please edit .env and add your Mistral AI API key!"
    echo "   Get your API key from: https://console.mistral.ai/"
    echo ""
    read -p "Press Enter after you've updated the API_KEY in .env file..."
fi

# Verify API key is set
if grep -q "your_mistral_api_key_here" .env; then
    echo "❌ Please update the API_KEY in .env file with your actual Mistral AI API key"
    echo "   Edit .env and replace 'your_mistral_api_key_here' with your real API key"
    exit 1
fi

echo "✅ Environment file configured"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs
echo "✅ Directories created"

# Check if we should build or just start
if [ "$1" = "--build" ] || [ ! "$(docker images -q justwork-justwork-backend 2>/dev/null)" ]; then
    echo "🔨 Building Docker images (this may take a few minutes on first run)..."
    docker_compose_cmd build
    echo "✅ Docker images built successfully"
fi

# Start the services
echo "🚀 Starting JustWork services..."
docker_compose_cmd up -d

# Wait a moment for services to start
sleep 5

# Check service status
echo "📊 Checking service status..."
docker_compose_cmd ps

# Test backend connectivity
echo "🔍 Testing backend connectivity..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Backend is running and healthy!"
        break
    else
        echo "⏳ Waiting for backend to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Backend failed to start properly. Check logs:"
    echo "   docker-compose logs justwork-backend"
    exit 1
fi

# Test frontend connectivity
echo "🔍 Testing frontend connectivity..."
max_attempts=15
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo "✅ Frontend is running and healthy!"
        break
    else
        echo "⏳ Waiting for frontend to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Frontend failed to start properly. Check logs:"
    echo "   docker-compose logs justwork-frontend"
    exit 1
fi

echo ""
echo "🎉 JustWork is now running successfully!"
echo ""
echo "📱 Access the application:"
echo "   • Frontend (Streamlit):    http://localhost:8501"
echo "   • Backend API:             http://localhost:8000"
echo "   • API Documentation:       http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   • View logs:              docker-compose logs -f"
echo "   • Stop services:          docker-compose down"
echo "   • Restart services:       docker-compose restart"
echo "   • Update services:        docker-compose pull && docker-compose up -d"
echo ""
echo "🔧 Troubleshooting:"
echo "   • If you see connection errors, check: docker-compose logs"
echo "   • If models are downloading, it may take a few minutes on first run"
echo "   • For help, see: DOCKER.md"
echo ""
echo "✨ Happy job matching!"
