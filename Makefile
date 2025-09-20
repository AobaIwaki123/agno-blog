# Agno Blog Application Makefile
# Updated for latest Agno framework

.PHONY: help install dev prod test lint format clean logs health status deploy

# Default Python version for the project
PYTHON := python3.12
PIP := pip

# Project paths
SRC_DIR := src
DOCKER_COMPOSE := docker-compose.yml

# Colors for output
BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Agno Blog Application$(NC)"
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r $(SRC_DIR)/requirements.txt
	@echo "$(GREEN)Dependencies installed successfully$(NC)"

dev: ## Start development server
	@echo "$(BLUE)Starting development server...$(NC)"
	cd $(SRC_DIR) && $(PYTHON) main.py

prod: ## Start production server with Docker Compose
	@echo "$(BLUE)Starting production server...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Production server started$(NC)"

quick-start: ## Quick start with Docker (build and run)
	@echo "$(BLUE)Quick starting Agno Blog...$(NC)"
	docker-compose up --build -d
	@echo "$(GREEN)Application started at http://localhost:8000$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	cd $(SRC_DIR) && $(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)Tests completed$(NC)"

lint: ## Run linting with ruff
	@echo "$(BLUE)Running linter...$(NC)"
	cd $(SRC_DIR) && ruff check .
	@echo "$(GREEN)Linting completed$(NC)"

format: ## Format code with black and ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	cd $(SRC_DIR) && black .
	cd $(SRC_DIR) && ruff format .
	@echo "$(GREEN)Code formatted$(NC)"

clean: ## Clean up containers and volumes
	@echo "$(BLUE)Cleaning up...$(NC)"
	docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

logs: ## Show application logs
	docker-compose logs -f agno-blog

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	@curl -f http://localhost:8000/health || echo "$(RED)Application not responding$(NC)"

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	docker-compose ps

# Development workflows
dev-setup: install ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from example...$(NC)"; \
		cp .env.example .env 2>/dev/null || echo "OPENAI_API_KEY=\nANTHROPIC_API_KEY=" > .env; \
	fi
	@echo "$(GREEN)Development environment ready$(NC)"
	@echo "$(YELLOW)Please update .env file with your API keys$(NC)"

# Deployment workflows
deploy-prod: ## Deploy to production with monitoring
	@echo "$(BLUE)Deploying to production...$(NC)"
	docker-compose --profile production up -d
	@echo "$(GREEN)Production deployment completed$(NC)"

deploy-monitoring: ## Deploy with monitoring stack
	@echo "$(BLUE)Deploying with monitoring...$(NC)"
	docker-compose --profile monitoring up -d
	@echo "$(GREEN)Monitoring stack deployed$(NC)"
	@echo "$(YELLOW)Grafana: http://localhost:3000 (admin/admin)$(NC)"
	@echo "$(YELLOW)Prometheus: http://localhost:9090$(NC)"

# Database operations
db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	docker-compose exec agno-blog python -c "from main import db; db.create_tables()"
	@echo "$(GREEN)Database initialized$(NC)"

db-backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	docker-compose exec postgres pg_dump -U agno agno_blog > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Database backup completed$(NC)"

db-restore: ## Restore database (requires BACKUP_FILE=filename.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Please specify BACKUP_FILE=filename.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(BACKUP_FILE)...$(NC)"
	docker-compose exec -T postgres psql -U agno agno_blog < $(BACKUP_FILE)
	@echo "$(GREEN)Database restored$(NC)"

# SSL and security
ssl-cert: ## Generate SSL certificates for production
	@echo "$(BLUE)Generating SSL certificates...$(NC)"
	mkdir -p ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout ssl/private.key \
		-out ssl/certificate.crt \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
	@echo "$(GREEN)SSL certificates generated$(NC)"

# Monitoring and debugging
debug: ## Start in debug mode
	@echo "$(BLUE)Starting in debug mode...$(NC)"
	DEBUG=true docker-compose up

monitor: ## Show real-time resource usage
	watch docker stats

shell: ## Open shell in the application container
	docker-compose exec agno-blog /bin/bash

# Update and maintenance
update: ## Update dependencies and rebuild
	@echo "$(BLUE)Updating application...$(NC)"
	$(PIP) install --upgrade -r $(SRC_DIR)/requirements.txt
	docker-compose build --no-cache
	@echo "$(GREEN)Update completed$(NC)"

security-scan: ## Run security scan on dependencies
	@echo "$(BLUE)Running security scan...$(NC)"
	$(PIP) install safety
	safety check -r $(SRC_DIR)/requirements.txt
	@echo "$(GREEN)Security scan completed$(NC)"

# Environment management
env-check: ## Check environment configuration
	@echo "$(BLUE)Environment Configuration:$(NC)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Docker: $(shell docker --version)"
	@echo "Docker Compose: $(shell docker-compose --version)"
	@if [ -f .env ]; then \
		echo "$(GREEN).env file exists$(NC)"; \
	else \
		echo "$(RED).env file missing$(NC)"; \
	fi

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	# Add documentation generation commands here
	@echo "$(GREEN)Documentation generated$(NC)"

# Performance testing
benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	# Add benchmark commands here
	@echo "$(GREEN)Benchmarks completed$(NC)"
