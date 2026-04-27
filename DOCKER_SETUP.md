# Insight Backend - Docker & CI/CD Setup Guide

## 📦 Files Created

### Docker Files

- **[Dockerfile](Dockerfile)** - Multi-stage build for production-optimized image
- **[docker-compose.yml](docker-compose.yml)** - Local development environment
- **[docker-compose.prod.yml](docker-compose.prod.yml)** - Production overrides
- **[.dockerignore](.dockerignore)** - Excludes unnecessary files from Docker build

### CI/CD Pipelines (GitHub Actions)

- **[.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)** - Complete CI/CD pipeline
  - Lint & Test on all pushes/PRs
  - Build Docker image on pushes
  - Deploy to dev (develop branch)
  - Deploy to prod (main branch)
  - Security scanning with Trivy

- **[.github/workflows/docker-build.yml](.github/workflows/docker-build.yml)** - Docker build & push
  - Builds and pushes to GitHub Container Registry
  - Automatic semantic versioning tags

### Configuration Files

- **[.env.example](.env.example)** - Environment variables template
- **[Makefile](Makefile)** - Convenient make commands
- **[pytest.ini](pytest.ini)** - Testing configuration
- **[requirements-dev.txt](requirements-dev.txt)** - Development dependencies

### Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide

---

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone and setup
git clone <repo>
cd Backend
cp .env.example .env

# Start development environment
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# API will be available at: http://localhost:8000/docs
```

### Option 2: Using Make Commands

```bash
make dev        # Start development environment
make logs       # View logs
make shell      # Access container shell
make down       # Stop environment
```

### Option 3: Manual Docker Commands

```bash
# Build image
docker build -t insight-backend:latest .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=True \
  -v $(pwd)/app:/app/app \
  insight-backend:latest
```

---

## 📋 Docker Architecture

### Multi-Stage Build

1. **Builder Stage** - Installs all dependencies (smaller final image)
2. **Runtime Stage** - Contains only production dependencies
3. **Result** - Optimized production image (~500MB)

### Features

- ✅ Non-root user (security)
- ✅ Health checks enabled
- ✅ Volume mounts for development
- ✅ Proper signal handling
- ✅ Optimized caching layers

---

## 🔄 CI/CD Pipeline

### Workflow Overview

```
Push to Repository
    ↓
[Lint & Test] (all branches)
    ↓
    ├─→ [Build Docker Image] (main, develop, feature branches)
    │    ↓
    │    ├─→ [Deploy Dev] (develop branch)
    │    └─→ [Deploy Prod] (main branch)
    │
    └─→ [Security Scan] (Trivy)
```

### Pipeline Stages

1. **Lint & Test**
   - Python linting (Black, Flake8, Pylint)
   - Unit tests with pytest
   - Coverage reports to Codecov

2. **Build**
   - Docker image build
   - Push to GitHub Container Registry
   - Automatic tagging

3. **Deploy Dev**
   - Triggered on `develop` branch
   - Deploy to staging environment

4. **Deploy Prod**
   - Triggered on `main` branch
   - Deploy to production environment

5. **Security Scan**
   - Trivy vulnerability scanning
   - Results in GitHub Security tab

---

## 📝 Environment Variables

Key variables in `.env.example`:

```env
# Server
DEBUG=False
LOG_LEVEL=INFO
PORT=8000

# Database
CHROMADB_PATH=./chroma_db

# Security
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000

# External APIs
ARXIV_API_TIMEOUT=30
LLM_API_KEY=your-key
```

---

## 🛠️ Make Commands

```bash
make help               # Show all commands
make build              # Build Docker image
make run                # Build and run locally
make dev                # Start docker-compose environment
make prod               # Start production environment
make logs               # View container logs
make shell              # Open shell in container
make test               # Run tests
make lint               # Run linting
make format             # Format code with Black
make stop               # Stop container
make clean              # Remove containers and images
```

---

## 🔐 Security Features

1. **Non-root User** - Container runs as `appuser` (UID 1000)
2. **Minimal Base Image** - Python 3.11-slim
3. **Security Scanning** - Trivy in CI/CD pipeline
4. **Health Checks** - Built-in container health monitoring
5. **Secrets Management** - Never commit `.env` files
6. **CORS Protection** - Configurable allowed origins

---

## 📊 Performance Optimizations

1. **Multi-stage Builds** - Reduces image size
2. **Layer Caching** - Dependencies cached separately
3. **Resource Limits** - CPU and memory limits in production
4. **Health Checks** - Container auto-restart on failure
5. **Non-blocking I/O** - FastAPI async handling

---

## 🚨 Troubleshooting

### Port Already in Use

```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up --build --force-recreate
```

### GitHub Actions Not Running

1. Verify workflows are enabled in Settings → Actions
2. Check branch protection rules
3. Verify `.github/workflows/*.yml` syntax

---

## 📚 Next Steps

1. **Initialize Git Repository** (if not already done)

   ```bash
   git init
   git add .
   git commit -m "Initial commit with Docker and CI/CD"
   git branch -M main
   git remote add origin <repo-url>
   git push -u origin main
   ```

2. **Configure Deployment**
   - Edit deployment scripts in `.github/workflows/ci-cd.yml`
   - Add deployment secrets to GitHub

3. **Test Locally**

   ```bash
   make dev
   make test
   ```

4. **Push to Repository**
   - CI/CD will automatically trigger
   - Monitor Actions tab in GitHub

---

## 📖 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Docker Docs](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/actions)
- [Container Registry](https://docs.github.com/packages)

---

## ✅ Checklist

- [ ] Review and customize `.env.example`
- [ ] Update deployment scripts in CI/CD workflows
- [ ] Test locally with `make dev`
- [ ] Push to repository
- [ ] Verify GitHub Actions runs successfully
- [ ] Configure deployment environments
- [ ] Set required secrets in GitHub
- [ ] Monitor first deployment

---

**Last Updated**: April 2026
