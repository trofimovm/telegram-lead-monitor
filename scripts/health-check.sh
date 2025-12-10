#!/bin/bash

# ==========================================
# Health Check Script for Telegram Lead Monitor
# ==========================================
# This script checks the health status of all Docker services
# Usage: ./scripts/health-check.sh

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo ""
echo "=========================================="
echo "  Telegram Lead Monitor - Health Check"
echo "=========================================="
echo ""

# Track overall health
ALL_HEALTHY=true

# ==========================================
# PostgreSQL
# ==========================================
echo -n "PostgreSQL:          "
if docker-compose exec -T postgres pg_isready -U telegram_monitor > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    ALL_HEALTHY=false
fi

# ==========================================
# Redis
# ==========================================
echo -n "Redis:               "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    ALL_HEALTHY=false
fi

# ==========================================
# Backend API
# ==========================================
echo -n "Backend API:         "
if curl -f -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    ALL_HEALTHY=false
fi

# ==========================================
# Frontend
# ==========================================
echo -n "Frontend:            "
if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    ALL_HEALTHY=false
fi

# ==========================================
# Worker (check if running)
# ==========================================
echo -n "Worker:              "
if docker-compose ps worker | grep -q "Up"; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not Running${NC}"
    ALL_HEALTHY=false
fi

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}All services are healthy! ✓${NC}"
    echo "=========================================="
    echo ""
    exit 0
else
    echo -e "${RED}Some services are unhealthy! ✗${NC}"
    echo "=========================================="
    echo ""
    echo "Troubleshooting:"
    echo "  • Check logs: make docker-logs"
    echo "  • Restart services: make docker-down && make docker-up"
    echo "  • Full documentation: DOCKER.md"
    echo ""
    exit 1
fi
