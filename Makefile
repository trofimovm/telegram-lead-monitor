.PHONY: help setup docker-up docker-down docker-logs docker-build docker-rebuild clean migrate shell-backend shell-frontend backend frontend worker test health-check

# ==========================================
# Help Command
# ==========================================
help:
	@echo "=========================================="
	@echo "Telegram Lead Monitor - Docker Commands"
	@echo "=========================================="
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup          - Create .env files from examples"
	@echo "  make docker-up      - Start all services (build + run)"
	@echo ""
	@echo "Development:"
	@echo "  make docker-logs    - View logs from all services"
	@echo "  make backend        - View backend logs only"
	@echo "  make frontend       - View frontend logs only"
	@echo "  make worker         - View worker logs only"
	@echo ""
	@echo "Management:"
	@echo "  make docker-down    - Stop all services"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-rebuild - Rebuild images without cache"
	@echo "  make migrate        - Run database migrations"
	@echo "  make health-check   - Check health of all services"
	@echo ""
	@echo "Shell Access:"
	@echo "  make shell-backend  - Shell into backend container"
	@echo "  make shell-frontend - Shell into frontend container"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run backend tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove all containers, volumes, and images"
	@echo ""
	@echo "=========================================="

# ==========================================
# Setup
# ==========================================
setup:
	@echo "🔧 Setting up environment files..."
	@if [ ! -f backend/.env ]; then \
		if [ -f backend/.env.example ]; then \
			cp backend/.env.example backend/.env; \
			echo "✅ Created backend/.env from .env.example"; \
		else \
			echo "⚠️  backend/.env.example not found"; \
		fi \
	else \
		echo "ℹ️  backend/.env already exists"; \
	fi
	@if [ ! -f frontend/.env.local ]; then \
		if [ -f frontend/.env.local.example ]; then \
			cp frontend/.env.local.example frontend/.env.local; \
			echo "✅ Created frontend/.env.local from .env.local.example"; \
		else \
			echo "⚠️  frontend/.env.local.example not found"; \
		fi \
	else \
		echo "ℹ️  frontend/.env.local already exists"; \
	fi
	@echo ""
	@echo "=========================================="
	@echo "Next Steps:"
	@echo "1. Edit backend/.env with your credentials"
	@echo "   - Telegram API credentials (API_ID, API_HASH)"
	@echo "   - LLM API key"
	@echo "   - Email settings (optional)"
	@echo ""
	@echo "2. Edit frontend/.env.local if needed"
	@echo "   - Default: NEXT_PUBLIC_API_URL=http://localhost:8000"
	@echo ""
	@echo "3. Start the application:"
	@echo "   make docker-up"
	@echo "=========================================="

# ==========================================
# Docker Operations
# ==========================================
docker-up:
	@echo "🐳 Starting all services..."
	docker-compose up -d --build
	@echo ""
	@echo "=========================================="
	@echo "✅ All services are starting up!"
	@echo "=========================================="
	@echo ""
	@echo "Services:"
	@echo "  🌐 Frontend:  http://localhost:3000"
	@echo "  🚀 Backend:   http://localhost:8000"
	@echo "  📚 API Docs:  http://localhost:8000/docs"
	@echo "  🗄️  PostgreSQL: localhost:5432"
	@echo "  💾 Redis:     localhost:6379"
	@echo ""
	@echo "View logs with:"
	@echo "  make docker-logs    - All services"
	@echo "  make backend        - Backend only"
	@echo "  make frontend       - Frontend only"
	@echo "  make worker         - Worker only"
	@echo ""
	@echo "Check health:"
	@echo "  make health-check"
	@echo "=========================================="

docker-down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ All services stopped"

docker-logs:
	@echo "📋 Viewing logs from all services (Ctrl+C to exit)..."
	docker-compose logs -f

docker-build:
	@echo "🔨 Building Docker images..."
	docker-compose build
	@echo "✅ Docker images built"

docker-rebuild:
	@echo "🔨 Rebuilding Docker images (no cache)..."
	docker-compose build --no-cache
	@echo "✅ Docker images rebuilt"

# ==========================================
# Service-Specific Logs
# ==========================================
backend:
	@echo "📋 Viewing backend logs (Ctrl+C to exit)..."
	docker-compose logs -f backend

frontend:
	@echo "📋 Viewing frontend logs (Ctrl+C to exit)..."
	docker-compose logs -f frontend

worker:
	@echo "📋 Viewing worker logs (Ctrl+C to exit)..."
	docker-compose logs -f worker

# ==========================================
# Database Operations
# ==========================================
migrate:
	@echo "🔄 Running database migrations..."
	docker-compose exec backend alembic upgrade head
	@echo "✅ Migrations completed"

# ==========================================
# Shell Access
# ==========================================
shell-backend:
	@echo "🐚 Opening shell in backend container..."
	docker-compose exec backend /bin/bash

shell-frontend:
	@echo "🐚 Opening shell in frontend container..."
	docker-compose exec frontend /bin/sh

# ==========================================
# Testing
# ==========================================
test:
	@echo "🧪 Running backend tests..."
	docker-compose exec backend pytest
	@echo "✅ Tests completed"

# ==========================================
# Health Check
# ==========================================
health-check:
	@echo "🏥 Checking health of services..."
	@echo ""
	@echo "PostgreSQL:"
	@docker-compose exec -T postgres pg_isready -U telegram_monitor > /dev/null 2>&1 && \
		echo "  ✅ Healthy" || echo "  ❌ Unhealthy"
	@echo ""
	@echo "Redis:"
	@docker-compose exec -T redis redis-cli ping > /dev/null 2>&1 && \
		echo "  ✅ Healthy" || echo "  ❌ Unhealthy"
	@echo ""
	@echo "Backend:"
	@curl -f http://localhost:8000/api/health > /dev/null 2>&1 && \
		echo "  ✅ Healthy" || echo "  ❌ Unhealthy"
	@echo ""
	@echo "Frontend:"
	@curl -f http://localhost:3000 > /dev/null 2>&1 && \
		echo "  ✅ Healthy" || echo "  ❌ Unhealthy"
	@echo ""

# ==========================================
# Cleanup
# ==========================================
clean:
	@echo "⚠️  WARNING: This will remove all containers, volumes, and images!"
	@echo "⚠️  All data will be lost!"
	@echo ""
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker-compose rm -f
	@echo "Removing volumes..."
	-docker volume rm telegram-monitor-postgres-data 2>/dev/null || true
	-docker volume rm telegram-monitor-redis-data 2>/dev/null || true
	-docker volume rm telegram-monitor-sessions 2>/dev/null || true
	@echo "Pruning unused volumes..."
	docker volume prune -f
	@echo "✅ Cleanup completed"
