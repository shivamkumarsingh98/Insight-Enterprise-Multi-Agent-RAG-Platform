#!/bin/bash

# Quick Setup Script for Insight Backend with Docker & CI/CD
# Usage: bash setup.sh

set -e  # Exit on error

echo "🚀 Setting up Insight Backend with Docker & CI/CD..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your configuration."
else
    echo "✓ .env file already exists"
fi

echo ""
echo "📦 Building Docker image..."
docker-compose build

echo ""
echo "🐳 Starting development environment..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Available endpoints:"
echo "   - API:          http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - ReDoc:        http://localhost:8000/redoc"
echo ""
echo "📋 Useful commands:"
echo "   - View logs:    docker-compose logs -f backend"
echo "   - Open shell:   docker-compose exec backend /bin/bash"
echo "   - Stop services: docker-compose down"
echo "   - Run tests:    docker-compose exec backend pytest"
echo ""
echo "📚 For more info, see:"
echo "   - DOCKER_SETUP.md   (Quick reference)"
echo "   - DEPLOYMENT.md     (Complete guide)"
echo ""
