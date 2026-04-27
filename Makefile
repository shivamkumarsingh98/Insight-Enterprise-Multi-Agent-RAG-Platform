.PHONY: help build run stop clean test lint format dev prod logs

help:
	@echo "Available commands:"
	@echo "  make build          - Build Docker image"
	@echo "  make run            - Run Docker container locally"
	@echo "  make stop           - Stop Docker container"
	@echo "  make clean          - Remove Docker container and images"
	@echo "  make dev            - Start development environment with docker-compose"
	@echo "  make prod           - Start production environment"
	@echo "  make logs           - View Docker logs"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linting"
	@echo "  make format         - Format code with black"
	@echo "  make shell          - Open shell in running container"

build:
	docker build -t insight-backend:latest .
	@echo "✓ Docker image built successfully"

run: build
	docker run -p 8000:8000 \
		-v $(PWD)/app:/app/app \
		-v $(PWD)/data:/app/data \
		-e DEBUG=True \
		--name insight-backend-dev \
		insight-backend:latest
	@echo "✓ Container running on http://localhost:8000"

stop:
	docker stop insight-backend-dev || true
	docker rm insight-backend-dev || true
	@echo "✓ Container stopped"

clean: stop
	docker rmi insight-backend:latest || true
	@echo "✓ Cleaned up Docker resources"

dev:
	docker-compose up -d --build
	@echo "✓ Development environment started"
	@echo "📊 API: http://localhost:8000"

prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✓ Production environment started"

logs:
	docker-compose logs -f backend

logs-app:
	docker logs -f insight-backend-dev || docker-compose logs -f backend

shell:
	docker-compose exec backend /bin/bash || docker exec -it insight-backend-dev /bin/bash

test:
	pytest tests/ -v --cov=app

lint:
	pylint app/
	flake8 app/

format:
	black app/

ps:
	docker-compose ps

restart:
	docker-compose restart backend

down:
	docker-compose down

.DEFAULT_GOAL := help
