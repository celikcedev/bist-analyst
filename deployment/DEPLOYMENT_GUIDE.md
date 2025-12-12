# 🚀 BIST Analyst - Production Deployment Guide

**Domain:** hisseleme.com  
**VPS:** Ubuntu 22.04 (2 CPU, 6GB RAM, 40GB SSD)  
**SSL:** Let's Encrypt via Certbot  
**DNS:** Cloudflare

---

## 📋 Subdomain Yapısı

| Subdomain | Servis | Port |
|-----------|--------|------|
| hisseleme.com | Main Landing Page | 3000 |
| screener.hisseleme.com | Python Screener | 3001 |
| api.hisseleme.com | Backend API | 5001 |

---

## 🔧 Adım 1: VPS'e Bağlan ve Sistem Güncelle

```bash
# VPS'e SSH ile bağlan
ssh root@<VPS_IP_ADRESI>

# Sistem güncelle
apt update && apt upgrade -y

# Gerekli paketleri kur
apt install -y curl git wget nano ufw htop
```

---

## 🔥 Adım 2: Firewall Ayarları

```bash
# UFW firewall yapılandır
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Durumu kontrol et
ufw status
```

---

## 🐳 Adım 3: Docker Kurulumu

```bash
# Docker kur
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose plugin kur
apt install -y docker-compose-plugin

# Docker'ı başlat ve otomatik başlatmayı etkinleştir
systemctl start docker
systemctl enable docker

# Versiyonları kontrol et
docker --version
docker compose version
```

---

## 🌐 Adım 4: Nginx Kurulumu

```bash
# Nginx kur
apt install -y nginx

# Başlat ve otomatik başlatmayı etkinleştir
systemctl start nginx
systemctl enable nginx
```

---

## 🔒 Adım 5: Certbot (Let's Encrypt) Kurulumu

```bash
# Certbot kur
apt install -y certbot python3-certbot-nginx
```

---

## 📁 Adım 6: Proje Dosyalarını Kopyala

```bash
# Proje dizini oluştur
mkdir -p /opt/bist-analyst
cd /opt/bist-analyst

# GitHub'dan klonla
git clone https://github.com/celikcedev/bist-analyst.git .

# Dizin yapısını kontrol et
ls -la
```

---

## ☁️ Adım 7: Cloudflare DNS Ayarları

Cloudflare Dashboard'a git ve aşağıdaki A kayıtlarını ekle:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | @ | VPS_IP_ADRESI | DNS only (grey cloud) |
| A | www | VPS_IP_ADRESI | DNS only (grey cloud) |
| A | screener | VPS_IP_ADRESI | DNS only (grey cloud) |
| A | api | VPS_IP_ADRESI | DNS only (grey cloud) |

**ÖNEMLİ:** SSL sertifikası almak için Cloudflare proxy'sini geçici olarak kapat (grey cloud). SSL aldıktan sonra tekrar açabilirsin (orange cloud).

---

## 🔐 Adım 8: SSL Sertifikası Al

```bash
# Tüm subdomainler için SSL sertifikası al
certbot --nginx -d hisseleme.com -d www.hisseleme.com -d screener.hisseleme.com -d api.hisseleme.com

# Email adresini gir ve koşulları kabul et
# Otomatik yenileme test et
certbot renew --dry-run
```

---

## ⚙️ Adım 9: Nginx Yapılandırması

```bash
# Nginx config dosyasını kopyala
cp /opt/bist-analyst/deployment/nginx/nginx.conf /etc/nginx/sites-available/hisseleme.com

# Symlink oluştur
ln -sf /etc/nginx/sites-available/hisseleme.com /etc/nginx/sites-enabled/

# Default config'i kaldır
rm -f /etc/nginx/sites-enabled/default

# Nginx config'i test et
nginx -t

# Nginx'i yeniden yükle
systemctl reload nginx
```

---

## 📝 Adım 10: Environment Dosyasını Yapılandır

```bash
# Deployment dizinine git
cd /opt/bist-analyst/deployment

# .env.production dosyasını oluştur
cp env.production.example .env.production

# Dosyayı düzenle
nano .env.production
```

Aşağıdaki değerleri güncelle:
```bash
# Güçlü bir şifre oluştur
POSTGRES_PASSWORD=<GÜÇLÜ_ŞİFRE>

# Telegram bilgilerini ekle (opsiyonel)
TELEGRAM_BOT_TOKEN=<BOT_TOKEN>
TELEGRAM_CHAT_IDS=<CHAT_ID>
```

---

## 🚀 Adım 11: Docker Build ve Deploy

```bash
# Deployment dizinine git
cd /opt/bist-analyst/deployment

# Deploy script'e çalıştırma izni ver
chmod +x scripts/deploy.sh

# Docker images'ları build et (bu 5-10 dakika sürebilir)
./scripts/deploy.sh build

# Servisleri başlat
./scripts/deploy.sh up

# Durumu kontrol et
./scripts/deploy.sh status
```

---

## 🗃️ Adım 12: Database Migration

```bash
# Alembic migration'ları çalıştır
./scripts/deploy.sh migrate
```

---

## ✅ Adım 13: Test Et

```bash
# Health check
curl https://api.hisseleme.com/api/health

# Main app
curl -I https://hisseleme.com

# Screener app
curl -I https://screener.hisseleme.com
```

Tarayıcıda kontrol et:
- https://hisseleme.com
- https://screener.hisseleme.com
- https://api.hisseleme.com/api/health

---

## 📊 Yönetim Komutları

```bash
# Servisleri başlat
./scripts/deploy.sh up

# Servisleri durdur
./scripts/deploy.sh down

# Servisleri yeniden başlat
./scripts/deploy.sh restart

# Logları görüntüle
./scripts/deploy.sh logs

# Belirli servisin logları
./scripts/deploy.sh logs backend
./scripts/deploy.sh logs screener-app

# Durum kontrolü
./scripts/deploy.sh status

# Database backup
./scripts/deploy.sh backup

# Güncelleme (git pull + rebuild + restart)
./scripts/deploy.sh update
```

---

## 🔄 Otomatik Yenileme (Cron Jobs)

```bash
# Crontab düzenle
crontab -e

# Aşağıdaki satırları ekle:
# SSL sertifikası otomatik yenileme (ayda 2 kez)
0 0 1,15 * * certbot renew --quiet && systemctl reload nginx

# Günlük performans takibi (hafta içi 19:00)
0 19 * * 1-5 cd /opt/bist-analyst && docker compose -f deployment/docker-compose.prod.yml exec backend python scripts/track_performance.py >> logs/performance.log 2>&1
```

---

## 🐛 Sorun Giderme

### Docker build hatası
```bash
# Cache'i temizle ve yeniden build et
docker system prune -a -f
./scripts/deploy.sh build
```

### Database bağlantı hatası
```bash
# Database container'ını kontrol et
docker logs bist-postgres

# Database'e manuel bağlan
docker exec -it bist-postgres psql -U postgres -d bist_analyst
```

### Nginx hatası
```bash
# Nginx config'i test et
nginx -t

# Nginx loglarını kontrol et
tail -f /var/log/nginx/error.log
```

### SSL sertifikası hatası
```bash
# Sertifikayı yenile
certbot renew --force-renewal

# Nginx'i yeniden yükle
systemctl reload nginx
```

---

## 📈 Monitoring

### Disk kullanımı
```bash
df -h
```

### Memory kullanımı
```bash
free -h
```

### Docker container'ları
```bash
docker stats
```

### Nginx access log
```bash
tail -f /var/log/nginx/access.log
```

---

## 🔐 Güvenlik Önerileri

1. **Root kullanıcısı yerine sudo kullanıcısı oluştur**
2. **SSH key-based authentication kullan**
3. **Fail2ban kur** (brute-force koruması)
4. **Düzenli backup al**
5. **Docker images'ları güncel tut**

---

## 📞 Destek

- GitHub Issues: https://github.com/celikcedev/bist-analyst/issues
- Telegram: @bist_analyst_bot

---

**Son Güncelleme:** 12 Aralık 2025  
**Versiyon:** 1.0.0

