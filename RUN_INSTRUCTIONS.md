# BIST Analyst - DOĞRU Çalıştırma Talimatları

## ⚠️ ÖNEMLİ: Virtual Environment Kullanın!

Projenizde `.venv` klasörü var, bunu kullanmalısınız!

---

## 🚀 DOĞRU KULLANIM

### Terminal 1 - Backend (Virtual Environment ile):

```bash
cd /Users/ademcelik/Desktop/bist_analyst

# Virtual environment aktifleştir
source .venv/bin/activate

# Backend başlat (port 5001)
PORT=5001 python run_backend.py
```

**Göreceğiniz:**
```
🚀 Starting BIST Analyst API on port 5001
 * Serving Flask app 'backend.main'
 * Running on http://127.0.0.1:5001
```

### Terminal 2 - Frontend:

```bash
cd /Users/ademcelik/Desktop/bist_analyst/frontend/main-app

# Development server başlat
npm run dev
```

**Göreceğiniz:**
```
▲ Next.js 16.0.7
- Local: http://localhost:3000
✓ Ready in 477ms
```

---

## ✅ TEST

1. **Backend:** http://localhost:5001/api/health
2. **Frontend:** http://localhost:3000

**Landing Page'de:**
- ✅ Toplam Hisse: 593
- ✅ Aktif Hisse: 593
- ✅ Veri Noktası: 0 (normal - henüz data çekilmemiş)
- ✅ "Screener (Yakında)" butonu

---

## 🎯 Şimdi Durum:

✅ Sprint 0, 1, 2, 3 TAMAMLANDI
✅ Backend API çalışıyor
✅ Frontend landing page çalışıyor
🚀 **Sprint 4 - Screener UI geliştirme için HAZIR!**

---

## 💡 Not:

"Screener" butonu şu an için placeholder. Sprint 4'te:
- Screener app (port 3001) oluşturulacak
- Signal table, filters, charts eklenecek
- TradingView entegrasyonu yapılacak
