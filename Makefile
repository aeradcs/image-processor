.PHONY: build up down logs restart clean test

# Docker operations
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f python-ocr-service

logs-all:
	docker compose logs -f

restart:
	docker compose restart python-ocr-service

# Development operations
clean:
	docker compose down -v
	docker system prune -f

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d

# Testing
test-send:
	python ping_kafka.py

test-receive:
	python test_consumer.py

# Full development cycle
dev: build up logs

# Production deployment
prod: clean rebuild logs