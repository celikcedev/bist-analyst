# ============================================================================
# BIST Analyst - Makefile
# ============================================================================

.PHONY: help dev prod build up down logs clean restart test

# Default target
help:
	@echo "BIST Analyst - Available Commands:"
	@echo ""
	@echo "  make dev          - Start development environment"
	@echo "  make prod         - Deploy production environment"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start containers"
	@echo "  make down         - Stop containers"
	@echo "  make logs         - View logs"
	@echo "  make clean        - Clean up containers and volumes"
	@echo "  make restart      - Restart all services"
	@echo "  make test         - Run tests"
	@echo ""

# Development
dev:
	@echo "🚀 Starting development environment..."
	docker-compose up -d
	@echo "✅ Development environment started"
	@echo "   Backend:  http://localhost:5001"
	@echo "   Main:     http://localhost:3000"
	@echo "   Screener: http://localhost:3001"

# Production
prod:
	@echo "🚀 Deploying production environment..."
	./scripts/deploy.sh

# Build images
build:
	@echo "📦 Building Docker images..."
	docker-compose build --no-cache

build-prod:
	@echo "📦 Building production Docker images..."
	docker-compose -f docker-compose.prod.yml build --no-cache

# Start containers
up:
	@echo "🚀 Starting containers..."
	docker-compose up -d

up-prod:
	@echo "🚀 Starting production containers..."
	docker-compose -f docker-compose.prod.yml up -d

# Stop containers
down:
	@echo "🛑 Stopping containers..."
	docker-compose down

down-prod:
	@echo "🛑 Stopping production containers..."
	docker-compose -f docker-compose.prod.yml down

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f main-app screener-app

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Cleanup complete"

# Restart services
restart:
	@echo "🔄 Restarting services..."
	docker-compose restart

restart-backend:
	docker-compose restart backend

restart-frontend:
	docker-compose restart main-app screener-app

# Database operations
db-migrate:
	docker-compose exec backend alembic upgrade head

db-reset:
	docker-compose exec backend alembic downgrade base
	docker-compose exec backend alembic upgrade head

# Testing
test:
	@echo "🧪 Running tests..."
	docker-compose exec backend pytest

# Health check
health:
	@echo "🔍 Checking service health..."
	@curl -s http://localhost:5001/api/health | python -m json.tool || echo "❌ Backend unhealthy"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Main app healthy" || echo "❌ Main app unhealthy"
	@curl -s http://localhost:3001 > /dev/null && echo "✅ Screener healthy" || echo "❌ Screener unhealthy"
