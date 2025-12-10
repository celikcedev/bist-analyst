#!/bin/bash
# ============================================================================
# BIST Analyst - Production Deployment Script
# ============================================================================

set -e  # Exit on error

echo "🚀 Starting BIST Analyst Deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env from .env.example"
    exit 1
fi

# Load environment variables
source .env

echo -e "${YELLOW}📦 Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}🔍 Checking service health...${NC}"

if docker ps | grep -q bist-analyst-backend-prod; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    docker logs bist-analyst-backend-prod --tail 50
    exit 1
fi

if docker ps | grep -q bist-analyst-main-app-prod; then
    echo -e "${GREEN}✅ Main app is running${NC}"
else
    echo -e "${RED}❌ Main app failed to start${NC}"
    docker logs bist-analyst-main-app-prod --tail 50
    exit 1
fi

if docker ps | grep -q bist-analyst-screener-app-prod; then
    echo -e "${GREEN}✅ Screener app is running${NC}"
else
    echo -e "${RED}❌ Screener app failed to start${NC}"
    docker logs bist-analyst-screener-app-prod --tail 50
    exit 1
fi

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""
echo "Services:"
echo "  Backend:      http://localhost:5001"
echo "  Main App:     http://localhost:3000"
echo "  Screener App: http://localhost:3001"
echo ""
echo "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
