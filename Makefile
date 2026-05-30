# Docker Compose Configuration
COMPOSE_FILE := devops/docker-compose.yaml

# Phony targets
.PHONY: up stop down init

# Initialize environment files from samples
init:
	cp ./env.db.sample ./env.db
	cp ./backend/env.sample ./backend/.env

# Start Docker Compose
up:
	docker-compose -f $(COMPOSE_FILE) up -d

# Stop Docker Compose
stop:
	docker-compose -f $(COMPOSE_FILE) stop

# Down Docker Compose (stop and remove containers)
down:
	docker-compose -f $(COMPOSE_FILE) down
