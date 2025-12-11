# Docker Troubleshooting & Alternative Deployment

## 🐛 Known Issues

### Docker Build I/O Errors (macOS)

**Problem:** Docker build commands fail with I/O errors or timeout
```
ERROR: write /var/lib/docker/buildkit/metadata_v2.db: input/output error
```

**Possible Causes:**
1. Docker Desktop resource limits
2. Disk space issues
3. BuildKit cache corruption
4. macOS file system issues

**Solutions:**

### Option 1: Increase Docker Resources
1. Open Docker Desktop
2. Settings → Resources
3. Increase:
   - CPUs: 4-6 cores
   - Memory: 8-12 GB
   - Disk image size: 64+ GB
4. Apply & Restart

### Option 2: Clean Docker System
```bash
# Remove all unused data
docker system prune -a -f

# Remove build cache
docker builder prune -a -f

# Restart Docker Desktop
killall Docker && open -a Docker
```

### Option 3: Use Alternative Build Methods

#### A) Cloud Build (GitHub Actions)
```yaml
# .github/workflows/docker-build.yml
name: Docker Build
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build images
        run: docker-compose build
```

#### B) Production Server Build
Build directly on your production server where resources are better:
```bash
# SSH to production server
ssh user@your-server

# Clone repository
git clone https://github.com/yourusername/bist-analyst.git
cd bist-analyst

# Build on production
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

#### C) Pre-built Images (Docker Hub/GHCR)
Push pre-built images to a registry:
```bash
# Tag and push
docker tag bist-analyst-backend:latest yourusername/bist-analyst-backend:latest
docker push yourusername/bist-analyst-backend:latest
```

---

## 🚀 Alternative Deployment Strategies

### Strategy 1: Development Environment (Current)

**✅ Works perfectly!**

```bash
# Terminal 1: Backend
cd /Users/ademcelik/Desktop/bist_analyst
source .venv/bin/activate
PORT=5001 python run_backend.py

# Terminal 2: Main App
cd frontend/main-app
npm run dev

# Terminal 3: Screener App
cd frontend/screener-app
npm run dev
```

**Pros:**
- Fast development cycle
- Easy debugging
- Hot reload
- No Docker overhead

**Cons:**
- Manual process management
- Not production-ready
- Environment-specific

---

### Strategy 2: VPS/Cloud Deployment

**Recommended for production:**

#### DigitalOcean/Linode/Hetzner:
1. Create droplet (4GB RAM, 2 CPUs minimum)
2. Install Docker & Docker Compose
3. Clone repository
4. Run: `./scripts/deploy.sh`

#### AWS EC2:
1. Launch t3.medium instance
2. Install Docker
3. Use docker-compose.prod.yml
4. Setup Nginx for SSL

#### Railway/Render/Fly.io:
1. Connect GitHub repository
2. Auto-deploy on push
3. Managed PostgreSQL
4. Built-in SSL

---

### Strategy 3: Kubernetes (Future)

For scaling beyond single server:

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bist-analyst-backend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: bist-analyst-backend:latest
```

---

## 📊 Current Status

| Component | Development | Docker | Production |
|-----------|------------|--------|------------|
| Backend | ✅ Working | ⚠️ Build issues | 🔄 VPS recommended |
| Main App | ✅ Working | ⚠️ Build issues | 🔄 VPS recommended |
| Screener | ✅ Working | ⚠️ Build issues | 🔄 VPS recommended |
| Database | ✅ Working | ✅ Ready | ✅ Ready |
| Nginx | N/A | ✅ Ready | ✅ Ready |

---

## 🎯 Recommended Deployment Path

### Phase 1: Development (Current) ✅
- Local development environment
- Manual process management
- Perfect for development

### Phase 2: Staging (VPS)
1. Rent VPS (DigitalOcean $12/month)
2. Install Docker on VPS
3. Build images on VPS (better resources)
4. Deploy with docker-compose.prod.yml
5. Setup domain & SSL (Let's Encrypt)

### Phase 3: Production (Cloud)
1. AWS/GCP for reliability
2. Managed PostgreSQL (RDS/Cloud SQL)
3. Load balancer
4. Auto-scaling
5. Monitoring (CloudWatch/Datadog)

---

## 🔧 Quick Fixes

### If Backend won't start:
```bash
cd /Users/ademcelik/Desktop/bist_analyst
source .venv/bin/activate
pip install -r backend/requirements.txt
PORT=5001 python run_backend.py
```

### If Frontend won't build:
```bash
cd frontend/main-app  # or screener-app
rm -rf .next node_modules
npm install
npm run dev
```

### If Database connection fails:
```bash
# Check PostgreSQL
psql -U postgres -d trading_db -c "SELECT version();"

# Restart PostgreSQL
brew services restart postgresql
```

---

## 📞 Support

If issues persist:
1. Check GitHub Issues
2. Docker Desktop diagnostics
3. Try cloud build alternative
4. Contact maintainer

**Last Updated:** December 11, 2025
