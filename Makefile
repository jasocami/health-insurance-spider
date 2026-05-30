# Docker Compose Configuration
COMPOSE_FILE := devops/docker-compose.yml

# Phony targets
.PHONY: up stop down init up-service help

# Display help information
help:
	@echo "Health Insurance Spider - Makefile Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make init              Initialize environment files from samples"
	@echo "                         (copies env.db.sample → env.db and backend/env.sample → backend/.env)"
	@echo ""
	@echo "  make up                Start all Docker Compose services in background"
	@echo ""
	@echo "  make up-service        Start a specific service or list all available services"
	@echo "                         Usage: make up-service SERVICE=<service-name>"
	@echo "                         Example: make up-service SERVICE=backend"
	@echo "                         Run without SERVICE argument to list all services"
	@echo ""
	@echo "  make stop              Stop all running Docker Compose services"
	@echo ""
	@echo "  make down              Stop and remove all Docker Compose containers"
	@echo ""
	@echo "  make help              Display this help message"
	@echo ""

# Initialize environment files from samples
init:
	cp ./env.db.sample ./env.db
	cp ./backend/env.sample ./backend/.env

# Start a single service or list all services
up-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Available services:"; \
		docker-compose -f $(COMPOSE_FILE) config --services; \
	else \
		docker-compose -f $(COMPOSE_FILE) up -d $(SERVICE); \
	fi

# Start Docker Compose
up:
	docker-compose -f $(COMPOSE_FILE) up -d

# Stop Docker Compose
stop:
	docker-compose -f $(COMPOSE_FILE) stop

# Down Docker Compose (stop and remove containers)
down:
	docker-compose -f $(COMPOSE_FILE) down
