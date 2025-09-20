# Agno Blog Application Makefile
# Updated for latest Agno framework

.PHONY: help up down clean logs health db-init db-backup db-restore

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

up: ## Start server with Docker Compose
	@echo "$(BLUE)Starting server...$(NC)"
	docker compose up -d
	@echo "$(GREEN) server started$(NC)"

build-up: ## Quick start with Docker (build and run)
	@echo "$(BLUE)Building and starting server...$(NC)"
	docker compose up --build -d
	@echo "$(GREEN)Server started at http://localhost:8000$(NC)"

down: ## Stop server
	@echo "$(BLUE)Stopping server...$(NC)"
	docker compose down
	@echo "$(GREEN)Server stopped$(NC)"

clean: ## Clean up containers and volumes
	@echo "$(BLUE)Cleaning up...$(NC)"
	docker compose down -v
	docker system prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

logs: ## Show application logs
	docker compose logs -f agno-blog

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	@curl -f http://localhost:8000/health || echo "$(RED)Application not responding$(NC)"

# Database operations
db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	docker compose exec agno-blog python -c "from main import db; db.create_tables()"
	@echo "$(GREEN)Database initialized$(NC)"

db-backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	docker compose exec postgres pg_dump -U agno agno_blog > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Database backup completed$(NC)"

db-restore: ## Restore database (requires BACKUP_FILE=filename.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Please specify BACKUP_FILE=filename.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(BACKUP_FILE)...$(NC)"
	docker compose exec -T postgres psql -U agno agno_blog < $(BACKUP_FILE)
	@echo "$(GREEN)Database restored$(NC)"
