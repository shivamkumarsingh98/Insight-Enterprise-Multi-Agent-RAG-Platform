# Deployment Guide

## Local Development

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development without Docker)
- Git

### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd Backend

# Copy environment file
cp .env.example .env

# Build and run with Docker Compose
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Access API
curl http://localhost:8000/docs
```

### Using Make Commands

```bash
# Build Docker image
make build

# Start development environment
make dev

# View logs
make logs

# Stop environment
make down

# Open shell in container
make shell
```

## Docker Build

### Building Locally

```bash
# Build image
docker build -t insight-backend:latest .

# Build with specific tag
docker build -t insight-backend:v1.0.0 .

# Build and run
docker run -p 8000:8000 insight-backend:latest
```

### Image Details

- **Base Image**: `python:3.11-slim`
- **Working Directory**: `/app`
- **Port**: 8000
- **Health Check**: Available at `/health` endpoint
- **User**: Non-root user (appuser:1000)

## GitHub Actions CI/CD Pipeline

### Workflows

1. **ci-cd.yml** - Main pipeline
   - Lint & Test: Runs on all pushes and PRs
   - Build: Builds Docker image on pushes
   - Deploy Dev: Deploys to dev on develop branch
   - Deploy Prod: Deploys to production on main branch
   - Security Scan: Runs Trivy vulnerability scanner

2. **docker-build.yml** - Focused Docker build
   - Builds and pushes to GitHub Container Registry
   - Automatic tagging (branch, SHA, semver)

### Setting Up GitHub Actions

1. **Enable Workflows**
   - Go to repository → Settings → Actions
   - Ensure workflows are enabled

2. **Configure Secrets** (if needed)
   - Go to Settings → Secrets → Actions
   - Add any required secrets:
     - `DOCKER_USERNAME` (if using Docker Hub)
     - `DOCKER_PASSWORD` (if using Docker Hub)
     - `DEPLOY_TOKEN` (for deployment)
     - `LLM_API_KEY` (for runtime)

3. **Container Registry Access**
   - Workflows automatically use `GITHUB_TOKEN` for `ghcr.io`
   - No additional configuration needed for GitHub Container Registry

### Triggering Workflows

```bash
# Push to main/develop branches
git push origin main
git push origin develop

# Create pull request
git push origin feature/my-feature

# Manual trigger (if workflow has workflow_dispatch)
# Use GitHub Actions UI under "Run workflow"
```

## Production Deployment

### Docker Compose Production

```bash
# Copy environment for production
cp .env.example .env.prod
# Edit .env.prod with production values

# Start with production overrides
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or use make command
make prod
```

### Kubernetes Deployment (Optional)

If deploying to Kubernetes, create manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insight-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: insight-backend
  template:
    metadata:
      labels:
        app: insight-backend
    spec:
      containers:
        - name: backend
          image: ghcr.io/your-org/insight-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DEBUG
              value: "False"
            - name: LOG_LEVEL
              value: "INFO"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

## Monitoring

### View Logs

```bash
# Docker Compose
docker-compose logs backend -f

# Docker
docker logs -f <container-id>

# Inside container
make shell
cat logs/app.log
```

### Health Check

```bash
# Check container health
docker inspect insight-backend | grep -A 5 '"Health"'

# API health endpoint
curl http://localhost:8000/health
```

## Environment Variables

See `.env.example` for all available configuration options.

### Key Variables

- `DEBUG`: Enable debug mode (True/False)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `PORT`: API port (default: 8000)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `CHROMADB_PATH`: Path to ChromaDB data

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
docker run -p 8080:8000 insight-backend:latest
```

### Container Won't Start

```bash
# View logs
docker-compose logs backend

# Rebuild image
docker-compose up --build --force-recreate

# Check if dependencies are installed
docker run -it insight-backend:latest python -m pip list
```

### GitHub Actions Failing

1. Check workflow logs in Actions tab
2. Verify secrets are set correctly
3. Check Docker Hub/Registry credentials
4. Ensure Dockerfile is correct

## Best Practices

1. **Always use specific Python versions** in Dockerfile
2. **Use multi-stage builds** to reduce image size
3. **Define health checks** for containers
4. **Use environment variables** for configuration
5. **Never commit secrets** - use `.env.example` instead
6. **Test locally** before pushing
7. **Use semantic versioning** for tags
8. **Monitor logs** regularly
9. **Keep base images updated**
10. **Use resource limits** in production

## Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [GitHub Actions Workflows](https://docs.github.com/en/actions/using-workflows)
- [Container Registry Help](https://docs.github.com/en/packages/working-with-a-container-registry)
