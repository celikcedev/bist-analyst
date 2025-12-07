# BIST Analyst - Çalıştırma Talimatları

## 🚀 Hızlı Başlangıç

### 1. Backend API'yi Başlat

**Yöntem 1: Wrapper Script (Önerilen)**
```bash
# Project root'tan çalıştır
cd /Users/ademcelik/Desktop/bist_analyst
python3 run_backend.py
```

**Yöntem 2: Direct**
```bash
# Project root'tan çalıştır
cd /Users/ademcelik/Desktop/bist_analyst
python3 -m backend.main
```

Backend şurada çalışacak: **http://localhost:5000**

Test et:
```bash
curl http://localhost:5000/api/health
```

---

### 2. Frontend (Main App) Başlat

```bash
# Main app dizinine git
cd /Users/ademcelik/Desktop/bist_analyst/frontend/main-app

# İlk kez çalıştırıyorsan dependencies yükle
npm install

# Development server başlat
npm run dev
```

Frontend şurada çalışacak: **http://localhost:3000**

---

### 3. Browser'da Test Et

1. Backend çalışıyor mu: http://localhost:5000/api/health
2. Frontend: http://localhost:3000
3. Landing page'de veri görüyor musun

---

## 🐛 Sorun Giderme

### Backend: "ModuleNotFoundError: No module named 'backend'"

**Çözüm:** `run_backend.py` kullan veya project root'tan çalıştır:
```bash
cd /Users/ademcelik/Desktop/bist_analyst  # Project root
python3 run_backend.py
```

### Frontend: "Could not read package.json"

**Çözüm:** `frontend/main-app` dizininde olduğundan emin ol:
```bash
cd /Users/ademcelik/Desktop/bist_analyst/frontend/main-app
npm run dev
```

### CORS Hatası

**Çözüm:** Backend'in çalıştığından emin ol. Frontend backend'e ulaşamıyorsa CORS hatası verir.

---

## 📁 Dizin Yapısı

```
bist_analyst/
├── run_backend.py          ← Backend başlatıcı (BU DOSYAYI KULLAN)
├── backend/
│   ├── main.py             ← Flask app
│   ├── core/               ← Config, database
│   └── modules/            ← Screener, market_data
├── frontend/
│   └── main-app/           ← Next.js app (CD BU DİZİNE)
│       ├── package.json
│       └── app/
└── scripts/                ← CLI tools
```

---

## ✅ Doğru Kullanım

### Terminal 1 (Backend):
```bash
cd /Users/ademcelik/Desktop/bist_analyst
python3 run_backend.py
```

### Terminal 2 (Frontend):
```bash
cd /Users/ademcelik/Desktop/bist_analyst/frontend/main-app
npm run dev
```

---

## 🎯 Sıradaki Adımlar

1. ✅ Backend çalışıyor (port 5000)
2. ✅ Frontend çalışıyor (port 3000)
3. ✅ Landing page veri gösteriyor
4. 🚀 Sprint 4 - Screener UI geliştirme başlayabilir!
