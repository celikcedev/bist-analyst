# BIST Analyst - Çalıştırma Talimatları

## 🚀 Hızlı Başlangıç

### ⚠️ ÖNEMLI: macOS Port 5000 Sorunu

macOS'ta port 5000 AirPlay Receiver tarafından kullanılıyor. **Port 5001** kullanıyoruz.

---

### 1. Backend API'yi Başlat (Port 5001)

```bash
cd /Users/ademcelik/Desktop/bist_analyst
PORT=5001 python3 run_backend.py
```

Backend şurada çalışacak: **http://localhost:5001**

Test et:
```bash
curl http://localhost:5001/api/health
```

---

### 2. Frontend (Main App) Başlat

```bash
cd /Users/ademcelik/Desktop/bist_analyst/frontend/main-app

# Development server başlat
npm run dev
```

Frontend şurada çalışacak: **http://localhost:3000**

**Not:** `.env.local` otomatik olarak port 5001'e ayarlı.

---

### 3. Browser'da Test Et

1. Backend health: http://localhost:5001/api/health
2. Frontend: http://localhost:3000
3. Landing page'de veri görüyor musun

---

## 🐛 Sorun Giderme

### "Address already in use" (Port 5000)

**Çözüm:** Port 5001 kullan:
```bash
PORT=5001 python3 run_backend.py
```

### "Network Error" on Frontend

**Çözüm:** 
1. Backend'in port 5001'de çalıştığından emin ol
2. `.env.local` dosyasında `NEXT_PUBLIC_API_URL=http://localhost:5001` olmalı
3. Frontend'i yeniden başlat (Ctrl+C, sonra `npm run dev`)

---

## ✅ Doğru Kullanım

### Terminal 1 (Backend):
```bash
cd /Users/ademcelik/Desktop/bist_analyst
PORT=5001 python3 run_backend.py
```

### Terminal 2 (Frontend):
```bash
cd /Users/ademcelik/Desktop/bist_analyst/frontend/main-app
npm run dev
```

**Not:** Frontend'i başlattıktan sonra browser'da otomatik açılacak veya http://localhost:3000'e git.

---

## 🎯 Şimdi Test Et:

1. ✅ Backend çalışıyor mu: http://localhost:5001/api/health
2. ✅ Frontend çalışıyor mu: http://localhost:3000
3. ✅ Landing page veri gösteriyor mu?

Tüm testler başarılıysa **Sprint 4 - Screener UI** ile devam edebiliriz! 🚀
