#!/bin/bash
# =============================================================================
# BIST Analyst - Production Deployment Script
# =============================================================================
# Usage: ./deploy.sh [build|up|down|restart|logs|status]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env.production"

# Check if .env.production exists
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}Error: .env.production not found!${NC}"
        echo "Copy env.production.example to .env.production and fill in the values"
        exit 1
    fi
}

# Print header
header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  BIST Analyst - Production Deployment${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

# Build Docker images
build() {
    header
    echo -e "${YELLOW}Building Docker images...${NC}"
    cd "$PROJECT_DIR/.."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    echo -e "${GREEN}✓ Build complete!${NC}"
}

# Start services
up() {
    header
    check_env
    echo -e "${YELLOW}Starting services...${NC}"
    cd "$PROJECT_DIR/.."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    echo -e "${GREEN}✓ Services started!${NC}"
    echo ""
    echo "Services:"
    echo "  - Main App:     http://localhost:3000"
    echo "  - Screener App: http://localhost:3001"
    echo "  - Backend API:  http://localhost:5001"
    echo ""
    echo "Run './deploy.sh logs' to view logs"
}

# Stop services
down() {
    header
    echo -e "${YELLOW}Stopping services...${NC}"
    cd "$PROJECT_DIR/.."
    docker compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✓ Services stopped!${NC}"
}

# Restart services
restart() {
    header
    echo -e "${YELLOW}Restarting services...${NC}"
    down
    up
}

# View logs
logs() {
    cd "$PROJECT_DIR/.."
    docker compose -f "$COMPOSE_FILE" logs -f "$@"
}

# Check status
status() {
    header
    echo -e "${YELLOW}Service Status:${NC}"
    echo ""
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    
    # Health checks
    echo -e "${YELLOW}Health Checks:${NC}"
    echo -n "  Backend API: "
    if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "  Main App:    "
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "  Screener:    "
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    echo ""
}

# Run database migrations
migrate() {
    header
    echo -e "${YELLOW}Running database migrations...${NC}"
    docker compose -f "$COMPOSE_FILE" exec backend alembic upgrade head
    echo -e "${GREEN}✓ Migrations complete!${NC}"
}

# Backup database
backup() {
    header
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    echo -e "${YELLOW}Creating database backup: $BACKUP_FILE${NC}"
    docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres bist_analyst > "$PROJECT_DIR/backups/$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup saved to: backups/$BACKUP_FILE${NC}"
}

# Pull latest code and redeploy
update() {
    header
    echo -e "${YELLOW}Pulling latest code...${NC}"
    cd "$PROJECT_DIR/.."
    git pull origin main
    
    echo -e "${YELLOW}Rebuilding and restarting...${NC}"
    build
    restart
    
    echo -e "${YELLOW}Running migrations...${NC}"
    migrate
    
    echo -e "${GREEN}✓ Update complete!${NC}"
}

# Show help
help() {
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build     Build Docker images"
    echo "  up        Start all services"
    echo "  down      Stop all services"
    echo "  restart   Restart all services"
    echo "  logs      View logs (optional: service name)"
    echo "  status    Check service status"
    echo "  migrate   Run database migrations"
    echo "  backup    Backup database"
    echo "  update    Pull latest code and redeploy"
    echo "  help      Show this help message"
    echo ""
}

# Main
case "${1:-help}" in
    build)   build ;;
    up)      up ;;
    down)    down ;;
    restart) restart ;;
    logs)    shift; logs "$@" ;;
    status)  status ;;
    migrate) migrate ;;
    backup)  backup ;;
    update)  update ;;
    help)    help ;;
    *)       echo "Unknown command: $1"; help; exit 1 ;;
esac

