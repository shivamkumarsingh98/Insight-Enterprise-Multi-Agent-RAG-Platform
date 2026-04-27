@echo off
REM Quick Setup Script for Insight Backend with Docker & CI/CD (Windows)
REM Usage: setup.bat

setlocal enabledelayedexpansion

echo.
echo 🚀 Setting up Insight Backend with Docker ^& CI/CD...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install it first.
    echo    Visit: https://docs.docker.com/compose/install/
    exit /b 1
)

echo ✓ Docker and Docker Compose are installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✓ .env file created. Please edit it with your configuration.
) else (
    echo ✓ .env file already exists
)

echo.
echo 📦 Building Docker image...
docker-compose build

echo.
echo 🐳 Starting development environment...
docker-compose up -d

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 5 /nobreak

echo.
echo ✅ Setup complete!
echo.
echo 📊 Available endpoints:
echo    - API:          http://localhost:8000
echo    - API Docs:     http://localhost:8000/docs
echo    - ReDoc:        http://localhost:8000/redoc
echo.
echo 📋 Useful commands:
echo    - View logs:    docker-compose logs -f backend
echo    - Open shell:   docker-compose exec backend bash
echo    - Stop services: docker-compose down
echo    - Run tests:    docker-compose exec backend pytest
echo.
echo 📚 For more info, see:
echo    - DOCKER_SETUP.md   (Quick reference)
echo    - DEPLOYMENT.md     (Complete guide)
echo.
