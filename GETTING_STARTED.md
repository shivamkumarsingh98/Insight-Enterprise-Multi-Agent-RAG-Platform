# Getting Started Checklist

## ✅ Pre-Deployment Setup

### System Requirements

- [ ] Docker Desktop installed and running
- [ ] Docker Compose installed (included with Docker Desktop)
- [ ] Git configured (for pushing to GitHub)
- [ ] Text editor or IDE available

### Environment Setup

- [ ] Copy `.env.example` to `.env`
- [ ] Review and update `.env` with your settings
- [ ] Ensure `.env` is in .gitignore (should be already)
- [ ] Verify all required environment variables are set

---

## 🐳 Docker & Local Development

### Build Docker Image

- [ ] Run `docker-compose build` or `make build`
- [ ] Verify image built successfully
- [ ] Check image size: `docker images insight-backend`

### Run Locally

- [ ] Start with `docker-compose up -d` or `make dev`
- [ ] Verify container is running: `docker-compose ps`
- [ ] Check health: `curl http://localhost:8000/health`
- [ ] Access API documentation: http://localhost:8000/docs

### Test Functionality

- [ ] Test API endpoints through Swagger UI
- [ ] View logs: `docker-compose logs -f backend`
- [ ] Run tests: `docker-compose exec backend pytest`
- [ ] Verify health check returns 200 status

---

## 📝 Code Quality

### Local Testing

- [ ] Run linting: `make lint`
- [ ] Format code: `make format`
- [ ] Run tests: `make test`
- [ ] Check coverage: Review test output

### Before Committing

- [ ] Code passes linting
- [ ] All tests pass
- [ ] No uncommitted secrets in code
- [ ] .env file NOT staged for commit

---

## 🔒 Security

### Repository Security

- [ ] `.env` file is in .gitignore
- [ ] No secrets committed
- [ ] No credentials in code
- [ ] Review DOCKER_CI_CD_SETUP.md security section

### Docker Security

- [ ] Health check endpoint implemented
- [ ] Container runs as non-root user
- [ ] Resource limits configured in production
- [ ] Base image is from official registry

---

## 📦 Git & GitHub Setup

### Local Git Setup (if needed)

```bash
git init
git add .
git commit -m "Initial commit with Docker and CI/CD"
git branch -M main
git remote add origin <YOUR_REPO_URL>
```

### GitHub Repository

- [ ] Create repository on GitHub
- [ ] Push code: `git push -u origin main`
- [ ] Create `develop` branch: `git checkout -b develop && git push -u origin develop`
- [ ] Push all branches and commits

### GitHub Configuration

- [ ] Go to Settings → Actions
- [ ] Enable GitHub Actions if disabled
- [ ] Check that workflows are visible

---

## 🔄 CI/CD Pipeline

### Verify Workflows

- [ ] Navigate to Actions tab
- [ ] Confirm both workflows appear:
  - [ ] `ci-cd.yml`
  - [ ] `docker-build.yml`
- [ ] Check workflow syntax is valid

### Test Pipeline

- [ ] Push small change to test branch
- [ ] Watch Actions tab for workflow execution
- [ ] Verify all stages pass:
  - [ ] Lint & Test
  - [ ] Build
  - [ ] Security Scan
- [ ] Check Docker image in GitHub Container Registry

### Configure Deployments (Optional)

- [ ] Update deployment scripts in workflows
- [ ] Add deployment secrets if needed
- [ ] Test deployment to staging environment
- [ ] Configure production deployment

---

## 📊 Monitoring & Logs

### Local Monitoring

- [ ] View container logs: `docker-compose logs -f backend`
- [ ] Check individual service: `docker logs <container-id>`
- [ ] Use `make logs` for convenience
- [ ] Monitor for errors and warnings

### GitHub Monitoring

- [ ] Check Actions tab for workflow status
- [ ] Review job logs for failures
- [ ] Check Docker image in Container Registry
- [ ] Monitor security scan results

---

## 🚀 Deployment (Production)

### Pre-Production Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Code reviewed
- [ ] Production environment variables set
- [ ] Backup existing data (if applicable)

### Production Deployment

- [ ] Pull latest main branch
- [ ] Run production docker-compose: `make prod`
- [ ] Verify health checks passing
- [ ] Monitor logs for errors
- [ ] Test critical endpoints
- [ ] Document deployment time and result

---

## 📋 Daily Development Workflow

### Starting Work

```bash
# Update code
git pull origin develop

# Start environment
make dev

# View logs
make logs
```

### During Development

```bash
# Run tests locally
make test

# Check linting
make lint

# Format code
make format

# Shell access to container
make shell
```

### Before Commit

```bash
# Final tests
make test

# Final linting
make lint

# Check logs for errors
make logs

# Stop environment if done
make down
```

### Pushing Code

```bash
# Stage changes
git add .

# Commit with message
git commit -m "Feature: description"

# Push to feature branch
git push origin feature/name

# Create Pull Request on GitHub
# CI/CD will run automatically
```

---

## 🐛 Debugging

### Container Issues

- [ ] Check logs: `docker-compose logs backend`
- [ ] Verify environment variables: `docker-compose config`
- [ ] Rebuild image: `docker-compose build --no-cache`
- [ ] Force recreation: `docker-compose up --force-recreate`

### Application Issues

- [ ] Check `/health` endpoint
- [ ] Review application logs in `/app/logs`
- [ ] Verify configuration in `.env`
- [ ] Test endpoints via `/docs` (Swagger UI)

### GitHub Actions Issues

- [ ] Check workflow YAML syntax
- [ ] Review action logs in detail
- [ ] Verify all required files present
- [ ] Check branch protection rules

---

## 📚 Documentation Reference

| Document              | Purpose                        |
| --------------------- | ------------------------------ |
| DOCKER_SETUP.md       | Quick reference guide          |
| DEPLOYMENT.md         | Complete deployment guide      |
| DOCKER_CI_CD_SETUP.md | Detailed setup summary         |
| README.md             | Original project documentation |

---

## ✨ Success Indicators

You've successfully completed the setup when:

- [ ] Docker image builds without errors
- [ ] Container starts and runs
- [ ] Health check endpoint returns 200
- [ ] API documentation accessible at `/docs`
- [ ] Tests pass locally
- [ ] Git pushes trigger CI/CD pipeline
- [ ] GitHub Actions workflows complete successfully
- [ ] Docker image appears in Container Registry
- [ ] Code quality checks pass
- [ ] Security scan completes

---

## 🆘 Quick Help

### Command Reference

```bash
# Start development
make dev

# View logs
make logs

# Run tests
make test

# Format code
make format

# Stop services
make down

# Shell access
make shell

# Full help
make help
```

### Useful URLs (when running locally)

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### Contact & Support

For issues:

1. Check DEPLOYMENT.md troubleshooting section
2. Review GitHub Actions logs
3. Check Docker container logs
4. Verify environment variables

---

## 📞 Common Issues & Solutions

### Issue: Port 8000 already in use

**Solution**:

```bash
lsof -i :8000
kill -9 <PID>
# Or use different port in docker-compose.yml
```

### Issue: Docker image won't build

**Solution**:

```bash
docker-compose build --no-cache
# Check requirements.txt for syntax errors
```

### Issue: Container crashes on startup

**Solution**:

```bash
docker-compose logs backend
# Check .env file for missing variables
# Verify all dependencies installed
```

### Issue: CI/CD pipeline not running

**Solution**:

1. Verify `.github/workflows/` files exist
2. Check GitHub Actions is enabled
3. Verify file syntax (YAML)
4. Check branch settings

---

**Last Updated**: April 2026

**Status**: Ready for production deployment ✅

---

## 🎯 Next: What to Do Now

1. **Complete Setup**: Run `setup.sh` (Linux/Mac) or `setup.bat` (Windows)
2. **Test Locally**: Run `make dev` and access http://localhost:8000/docs
3. **Push to Git**: Commit and push to trigger CI/CD
4. **Monitor**: Check Actions tab on GitHub
5. **Deploy**: When ready, deploy to production using provided workflows

**Questions?** Refer to DEPLOYMENT.md or DOCKER_SETUP.md
