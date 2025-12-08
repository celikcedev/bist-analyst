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

### Terminal 2 - Main App Frontend:

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

### Terminal 3 - Screener App Frontend (YENİ! 🎉):

```bash
cd /Users/ademcelik/Desktop/bist_analyst/frontend/screener-app

# Development server başlat
npm run dev
```

**Göreceğiniz:**
```
▲ Next.js 16.0.7
- Local: http://localhost:3001
✓ Ready in 500ms
```

---

## ✅ TEST

1. **Backend:** http://localhost:5001/api/health
2. **Main App:** http://localhost:3000
3. **Screener App:** http://localhost:3001

**Main App'te:**
- ✅ "Screener →" butonuna tıklayın
- ✅ Port 3001'e yönlendirileceksiniz

**Screener App'te (TradingView benzeri UI):**
- ✅ Dark theme (TradingView stili)
- ✅ Watchlist: "BIST TUM"
- ✅ Strategy: "XTUMY Sniper - Trend & Divergence Hunter"
- ✅ Signal type chips (TREND BAŞLANGIÇ, PULLBACK AL, DIP AL, vb.)
- ✅ Settings icon ile parametre düzenleme
- ✅ Scan butonu ile tarama
- ✅ Sonuçları tablo halinde görüntüleme

---

## 🎯 Şimdi Durum:

✅ Sprint 0, 1, 2, 3, **4** TAMAMLANDI!
✅ Backend API çalışıyor (port 5001)
✅ Main landing page çalışıyor (port 3000)
✅ **Screener UI çalışıyor (port 3001)** 🎉
🚀 **Sprint 5 - Production deployment için HAZIR!**

---

## 🎨 Screener UI Özellikleri:

- **TradingView Pine Screener benzeri dark theme**
- **Watchlist selector** (BIST TUM)
- **Strategy selector** (dropdown ile değiştirilebilir)
- **Signal type filtering** (chip-based aktif/pasif toggle)
- **Parameter modal** (Grouped inputs - Ana Trend, Güç & Yön, Fibo, Uyarı Ayarları)
- **Real-time scanning** (Scan butonu)
- **Dynamic results table** (Logo, symbol, signal type, price, RSI, ADX)
- **Responsive design** (Mobile-friendly)

---

## 💡 İlk Kullanım:

1. Backend'i başlatın (Terminal 1)
2. Main app'i başlatın (Terminal 2)
3. Screener app'i başlatın (Terminal 3)
4. http://localhost:3001 açın
5. Settings icon'a tıklayarak parametreleri inceleyin
6. Signal type chip'lerine tıklayarak aktif/pasif yapın
7. "Scan" butonuna tıklayın!

---

## 🐛 Sorun Giderme:

**"Network Error" görüyorsanız:**
- Backend'in çalıştığından emin olun (Terminal 1)
- http://localhost:5001/api/health kontrol edin

**"Port already in use" hatası:**
- Port 3000: `lsof -ti:3000 | xargs kill -9`
- Port 3001: `lsof -ti:3001 | xargs kill -9`
- Port 5001: `lsof -ti:5001 | xargs kill -9`
