#!/bin/bash
# =============================================================================
# BIST Analyst - VPS Initial Setup Script
# =============================================================================
# Run this script on a fresh Ubuntu 22.04 VPS
# Usage: curl -sSL https://raw.githubusercontent.com/.../setup-vps.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  BIST Analyst - VPS Setup${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# 1. System Update
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/7] Updating system...${NC}"
apt update && apt upgrade -y
apt install -y curl git wget nano ufw htop

# -----------------------------------------------------------------------------
# 2. Firewall Setup
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/7] Configuring firewall...${NC}"
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo -e "${GREEN}✓ Firewall configured${NC}"

# -----------------------------------------------------------------------------
# 3. Docker Installation
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/7] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Install Docker Compose plugin
    apt install -y docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

docker --version
docker compose version

# -----------------------------------------------------------------------------
# 4. Nginx Installation
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/7] Installing Nginx...${NC}"
apt install -y nginx
systemctl start nginx
systemctl enable nginx
echo -e "${GREEN}✓ Nginx installed${NC}"

# -----------------------------------------------------------------------------
# 5. Certbot (Let's Encrypt) Installation
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/7] Installing Certbot...${NC}"
apt install -y certbot python3-certbot-nginx
echo -e "${GREEN}✓ Certbot installed${NC}"

# -----------------------------------------------------------------------------
# 6. Create Project Directory
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[6/7] Creating project directory...${NC}"
mkdir -p /opt/bist-analyst
mkdir -p /opt/bist-analyst/deployment/backups
mkdir -p /opt/bist-analyst/logs
echo -e "${GREEN}✓ Directories created${NC}"

# -----------------------------------------------------------------------------
# 7. Clone Repository
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[7/7] Cloning repository...${NC}"
cd /opt/bist-analyst
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/celikcedev/bist-analyst.git .
fi
echo -e "${GREEN}✓ Repository cloned${NC}"

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  VPS Setup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure DNS in Cloudflare:"
echo "   - A record: hisseleme.com -> $(curl -s ifconfig.me)"
echo "   - A record: screener.hisseleme.com -> $(curl -s ifconfig.me)"
echo "   - A record: api.hisseleme.com -> $(curl -s ifconfig.me)"
echo ""
echo "2. Create .env.production file:"
echo "   cd /opt/bist-analyst/deployment"
echo "   cp env.production.example .env.production"
echo "   nano .env.production"
echo ""
echo "3. Get SSL certificates:"
echo "   certbot --nginx -d hisseleme.com -d www.hisseleme.com -d screener.hisseleme.com -d api.hisseleme.com"
echo ""
echo "4. Copy Nginx config:"
echo "   cp /opt/bist-analyst/deployment/nginx/nginx.conf /etc/nginx/sites-available/hisseleme.com"
echo "   ln -s /etc/nginx/sites-available/hisseleme.com /etc/nginx/sites-enabled/"
echo "   rm /etc/nginx/sites-enabled/default"
echo "   nginx -t && systemctl reload nginx"
echo ""
echo "5. Deploy application:"
echo "   cd /opt/bist-analyst/deployment"
echo "   chmod +x scripts/deploy.sh"
echo "   ./scripts/deploy.sh build"
echo "   ./scripts/deploy.sh up"
echo "   ./scripts/deploy.sh migrate"
echo ""
echo -e "${BLUE}VPS IP: $(curl -s ifconfig.me)${NC}"
echo ""

