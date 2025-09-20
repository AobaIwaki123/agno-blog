# Agno Blog Application Makefile

.PHONY: help install dev build run test clean deploy stop logs shell

# Variables
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := agno-blog
IMAGE_NAME := $(PROJECT_NAME)
CONTAINER_NAME := $(PROJECT_NAME)-app

# Default target
help:
	@echo "Agno Blog Application - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  build       - Build Docker image"
	@echo "  run         - Run with Docker Compose"
	@echo "  stop        - Stop Docker containers"
	@echo "  logs        - View Docker logs"
	@echo "  shell       - Access container shell"
	@echo ""
	@echo "Production:"
	@echo "  deploy      - Deploy to production"
	@echo "  deploy-prod - Deploy with production profile"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean up temporary files"
	@echo "  backup      - Backup database"
	@echo "  restore     - Restore database"

# Development commands
install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r src/requirements.txt
	@echo "Dependencies installed!"

dev:
	@echo "Starting development server..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your API keys"; \
	fi
	cd src && $(PYTHON) main.py

test:
	@echo "Running tests..."
	cd src && $(PYTHON) -m pytest tests/ -v
	@echo "Tests completed!"

lint:
	@echo "Running code linting..."
	cd src && $(PYTHON) -m flake8 . --max-line-length=100 --ignore=E203,W503
	@echo "Linting completed!"

format:
	@echo "Formatting code..."
	cd src && $(PYTHON) -m black . --line-length=100
	@echo "Code formatted!"

# Docker commands
build:
	@echo "Building Docker image..."
	$(DOCKER) build -t $(IMAGE_NAME) .
	@echo "Docker image built successfully!"

run:
	@echo "Starting services with Docker Compose..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your API keys"; \
	fi
	$(DOCKER_COMPOSE) up -d
	@echo "Services started! Access the application at http://localhost:8000"

stop:
	@echo "Stopping Docker containers..."
	$(DOCKER_COMPOSE) down
	@echo "Containers stopped!"

logs:
	@echo "Viewing logs..."
	$(DOCKER_COMPOSE) logs -f $(CONTAINER_NAME)

shell:
	@echo "Accessing container shell..."
	$(DOCKER_COMPOSE) exec agno-blog /bin/bash

# Production deployment
deploy:
	@echo "Deploying to production..."
	$(DOCKER_COMPOSE) -f docker-compose.yml up -d --build
	@echo "Deployment completed!"

deploy-prod:
	@echo "Deploying with production profile..."
	$(DOCKER_COMPOSE) --profile production up -d --build
	@echo "Production deployment completed!"

deploy-monitoring:
	@echo "Deploying with monitoring..."
	$(DOCKER_COMPOSE) --profile monitoring up -d --build
	@echo "Monitoring deployment completed!"

# Database commands
backup:
	@echo "Creating database backup..."
	@mkdir -p backups
	$(DOCKER_COMPOSE) exec postgres pg_dump -U agno agno_blog > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/ directory"

restore:
	@echo "Restoring database..."
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore FILE=backups/backup_file.sql"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) exec -T postgres psql -U agno agno_blog < $(FILE)
	@echo "Database restored!"

# Utility commands
clean:
	@echo "Cleaning up..."
	# Remove Python cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	
	# Remove temporary files
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	
	# Remove Docker artifacts
	$(DOCKER) system prune -f
	@echo "Cleanup completed!"

clean-all: clean
	@echo "Performing deep cleanup..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER) rmi $(IMAGE_NAME) 2>/dev/null || true
	@echo "Deep cleanup completed!"

# Health checks
health:
	@echo "Checking application health..."
	@curl -f http://localhost:8000/health || echo "Application is not healthy"

status:
	@echo "Service status:"
	$(DOCKER_COMPOSE) ps

# Environment setup
setup:
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created from example"; \
	fi
	make install
	@echo "Environment setup completed!"
	@echo "Please edit .env file with your API keys before running the application"

# Quick start
quick-start: setup build run
	@echo "Quick start completed!"
	@echo "Application is running at http://localhost:8000"

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r src/requirements.txt
	@echo "Dependencies updated!"

# Generate requirements
freeze:
	@echo "Generating requirements.txt..."
	$(PIP) freeze > src/requirements.txt
	@echo "Requirements generated!"

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Documentation generation not implemented yet"

# Performance testing
load-test:
	@echo "Running load tests..."
	@echo "Load testing not implemented yet"

# Security scan
security-scan:
	@echo "Running security scan..."
	$(PIP) install safety bandit
	safety check -r src/requirements.txt
	bandit -r src/ -f json -o security-report.json
	@echo "Security scan completed!"