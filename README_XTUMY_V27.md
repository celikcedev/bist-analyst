# 📊 XTUMY V27 Python Screener - Kullanım Kılavuzu

## ✅ **DURUM: %100 PINE SCRIPT UYUMLU**

Bu Python Screener, TradingView Pine Script XTUMY V27 göstergesinin **tam uyumlu** Python implementasyonudur.

**Son Güncelleme:** 9 Aralık 2024  
**Commit:** 130c9e5  
**Uyumluluk:** ✅ Tüm 7 sinyal tipi Pine Screener ile bire bir eşleşiyor

---

## 🎯 **SİNYAL TİPLERİ (7 Adet)**

### 1️⃣ **KURUMSAL DİP** (Silent Accumulation)
**Ne Zaman:** Düşen trendde sessiz mal toplama  
**Koşullar:**
- Ayı piyasası yapısı (EMA20 < EMA50)
- Fiyat EMA20'yi yukarı keser
- RSI momentum artışı (RSI > RSI MA)
- Stabil hacim (0.3x - 1.5x ortalama)
- Yeşil mum

**Psikoloji:** Kurumsal yatırımcılar sessizce dip topluyor

---

### 2️⃣ **TREND BAŞLANGIÇ** (EMA50 Breakout)
**Ne Zaman:** Ana trendin başlangıcı  
**Koşullar:**
- Fiyat EMA50'yi yukarı keser
- Güçlü hacim (> ortalama)
- Yeşil mum
- DI+ > DI- (yön onayı)
- Confirmation bars kadar üstte kalma

**Psikoloji:** Yeni yükseliş trendi başlıyor

---

### 3️⃣ **PULLBACK AL** (EMA50 Retest)
**Ne Zaman:** Sağlıklı geri çekilme  
**Koşullar:**
- Trend başladıktan en az 3 bar sonra
- Fiyat EMA50'ye dokunuyor ama kırmıyor
- EMA50'nin üzerinde kapanış
- Güçlü hacim + yeşil mum
- RSI > 45, ADX > 20

**Psikoloji:** Kar realizasyonu sonrası güvenli alım noktası

---

### 4️⃣ **DİP AL** (Fibonacci Bottom)
**Ne Zaman:** Fibonacci 0.000 seviyesinde dip dönüşü  
**Koşullar:**
- Fiyat Fibo dip seviyesine yakın (±2%)
- Yeşil mum
- RSI momentum artışı
- DI+ > DI-

**Psikoloji:** Destek seviyesinden sert dönüş

---

### 5️⃣ **ALTIN KIRILIM** (Golden Ratio Breakout)
**Ne Zaman:** Fibonacci 0.618 direnci kırıldı  
**Koşullar:**
- Fiyat 0.618 seviyesini yukarı keser
- **Güçlü hacim** (> 1.2x ortalama)
- **Yeşil mum**
- **DI+ > DI-**
- **Cooldown:** Son 10 bar içinde geçerli ALTIN KIRILIM yok

**Önemli:** Cooldown sadece **tüm koşulları sağlayan** sinyalleri sayar!  
Crossover var ama hacim/mum/DI+ şartları yoksa → cooldown başlamaz

**Psikoloji:** Orta seviye direnç kırıldı, ivme artıyor

---

### 6️⃣ **ZİRVE KIRILIMI** (ATH Breakout)
**Ne Zaman:** Fibonacci 1.000 (tavan) kırıldı  
**Koşullar:**
- Fiyat Fibo tavana yukarı keser
- **Güçlü hacim** (> 1.2x ortalama)
- **Yeşil mum**
- **DI+ > DI-**
- **Cooldown:** Son 10 bar içinde geçerli ZİRVE KIRILIMI yok

**Önemli:** Cooldown mantığı ALTIN KIRILIM ile aynı

**Psikoloji:** Yeni zirveye doğru patlama

---

### 7️⃣ **DİRENÇ REDDİ** (Resistance Rejection) ⚠️
**Ne Zaman:** Direnç test edildi ama red edildi  
**Koşullar:**
- High >= Fibo tavan (direnci test etti)
- Close < Fibo tavan (red edildi)

**Önemli:** Bu bir **UYARI SİNYALİ** (satış baskısı)

**Psikoloji:** Alıcılar direnci kıramadı, satış baskısı var

**Pine Script Notu:**  
Pine Script'te 3 uyarı tipi var (bearDiv, overBoughtDrop, isRejection) ama **alertcondition sadece isRejection kullanır**. Screener alertcondition mantığını takip eder.

---

## 🔧 **PARAMETRELER**

```python
emaLen = 50          # Ana trend EMA
emaShortLen = 20     # Kurumsal iz EMA
confirmBars = 1      # Trend kırılım onay bar sayısı
pbWaitBars = 3       # Pullback için trend oturma süresi
pullPct = 2.0        # EMA yakınlık toleransı (%)
volMult = 1.2        # Hacim çarpanı (breakout için)
adxThresh = 20       # ADX eşiği (trend gücü)
useDiCheck = true    # DI+ > DI- şartı
rsiMin = 45          # Minimum RSI (AL için)
fibLen = 144         # Fibonacci periyodu
cooldown = 10        # Fibo sinyal soğuma süresi (bar)
```

---

## 🧪 **COOLDOWN MANTIĞI - KRİTİK DETAY**

### **Pine Script Referansı:**
```pine
var bool isGoldBreakValid = false
barsSinceLastGoldBreak = ta.barssince(isGoldBreakValid)
isCooledDownGold = na(barsSinceLastGoldBreak) or (barsSinceLastGoldBreak > cooldown)
isGoldBreakValid := breakGold and (volume > (avgVol * volMult)) and (close > open) and isDirectionUp and isCooledDownGold
```

### **Anahtar Nokta:**
`ta.barssince(isGoldBreakValid)` → **Tam geçerli sinyalden** bu yana geçen bar sayısı

### **Python Implementasyonu:**
```python
# Cooldown içinde TÜM koşulları kontrol et
past_crossover = (past_prev['close'] <= past_prev['wall_gold']) and (past_bar['close'] > past_bar['wall_gold'])
if past_crossover:
    # Crossover var, ama diğer koşullar da sağlanıyor muydu?
    past_valid = (
        (past_bar['volume'] > (past_bar['avgVol'] * params.volMult)) and
        (past_bar['close'] > past_bar['open']) and
        (past_bar['diplus'] > past_bar['diminus'])
    )
    if past_valid:  # Sadece tam geçerli sinyaller cooldown'u tetikler
        cooldown_ok = False
        break
```

### **Örnek Senaryo:**
```
Bar 1: Crossover ✅, Hacim ❌, Yeşil ❌, DI+ ❌ → Geçersiz, cooldown başlamaz
Bar 5: Crossover ✅, Hacim ✅, Yeşil ✅, DI+ ✅ → Geçerli sinyal!
Bar 10: Crossover ✅, ... → Red (cooldown içinde, bar 5'ten bu yana 5 bar geçti)
Bar 16: Crossover ✅, ... → Kabul (bar 5'ten bu yana 11 bar geçti > 10)
```

---

## 📊 **VERİ GEREKSİNİMLERİ**

### **Minimum Bar Sayısı:**
- Temel strateji: **60 bar** (EMA50 + ADX)
- Fibonacci sinyalleri: **194 bar** (144 + 50)
- Güvenilir sonuçlar: **250 bar** önerilir

### **Göstergeler:**
- EMA 50, EMA 20
- RSI 14, RSI MA 14
- ADX 14, DI+ 14, DI- 14
- Volume (20 bar SMA)
- Fibonacci: High/Low (144 bar)

---

## 🎨 **UI/UX ÖZELLİKLERİ**

### **Modern Tasarım:**
- TradingView-inspired dark theme
- Gradient accents (blue → purple → pink)
- Card-based responsive layout
- Full-screen loading animation (conic-gradient spinner)

### **Özellikler:**
- ✅ Sıralama (symbol, price, RSI, ADX, date)
- ✅ Renk kodlu göstergeler (RSI: yeşil/sarı/kırmızı, ADX: kırmızı/sarı/yeşil)
- ✅ Signal type badges (custom colors per type)
- ✅ Responsive dropdown menus (z-index hierarchy)
- ✅ Centered parameter modal (backdrop blur)
- ✅ Real-time scan timestamp footer

---

## 🚀 **KULLANIM**

### **Backend Başlatma:**
```bash
cd /Users/ademcelik/Desktop/bist_analyst
source .venv/bin/activate
python backend/api/server.py
```

### **Frontend Başlatma:**
```bash
cd frontend/screener-app
npm run dev
```

### **Browser:**
```
http://localhost:3000
```

### **Tarama:**
1. Sinyal tiplerini seçin (varsayılan: tümü)
2. Parametreleri ayarlayın (⚙️ ikonu)
3. "TARA" butonuna tıklayın
4. Sonuçları inceleyin (sıralama, filtreleme)

---

## 🔄 **VERİ GÜNCELLEME**

### **Manuel Güncelleme:**
```bash
# Ticker listesini güncelle (günlük)
python fetch_tickers.py

# Market verilerini güncelle (günlük)
python update_market_data.py
```

### **Cron Jobs:**
```bash
# Ticker listesi: Her gün 09:00
0 9 * * * cd /Users/ademcelik/Desktop/bist_analyst && source .venv/bin/activate && python fetch_tickers.py

# Market data: Her gün 19:00 (borsa kapandıktan sonra)
0 19 * * * cd /Users/ademcelik/Desktop/bist_analyst && source .venv/bin/activate && python update_market_data.py
```

---

## ✅ **DOĞRULAMA**

### **Test Metodolojisi:**
1. TradingView Pine Screener'da tarama yap (tüm sinyal tipleri)
2. Python Screener'da aynı taramayı yap
3. Sonuçları karşılaştır (ticker listesi, sinyal sayısı)

### **Son Test Sonuçları:** (9 Aralık 2024)
```
✅ KURUMSAL DİP: %100 eşleşme
✅ TREND BAŞLANGIÇ: %100 eşleşme
✅ PULLBACK AL: %100 eşleşme
✅ DİP AL: %100 eşleşme
✅ ALTIN KIRILIM: %100 eşleşme (DOGUB sorunu çözüldü)
✅ ZİRVE KIRILIMI: %100 eşleşme
✅ DİRENÇ REDDİ: %100 eşleşme (7 ticker: ALTIN, BIGCH, CWENE, ENKAI, KTLEV, RALYH, TAVHL)
```

---

## 📚 **DOKÜMANTASYON**

- `COOLDOWN_ANALIZ.md`: Cooldown mantığı detaylı analizi
- `FINAL_RAPOR.md`: Tüm implementasyon raporu
- `PINE_SCRIPT_DOGRULAMA.md`: Pine Script doğrulama ve alertcondition vs plotshape
- `VERITABANI_VE_UI_RAPORU.md`: Veritabanı durumu ve UI/UX iyileştirmeleri

---

## 🐛 **BİLİNEN SORUNLAR VE ÇÖZÜMLER**

### **Problem:** Tarama sonuç vermiyor
**Çözüm:** Market data boş olabilir
```bash
python update_market_data.py
```

### **Problem:** UI değişiklikleri görünmüyor
**Çözüm:** Next.js cache temizle
```bash
cd frontend/screener-app
rm -rf .next
npm run dev
```

### **Problem:** Modal sol kenarda açılıyor
**Çözüm:** Browser hard refresh (Cmd+Shift+R)

### **Problem:** Dropdown görünmüyor
**Çözüm:** `globals.css` z-index kontrol et

---

## 🙏 **TEŞEKKÜRLER**

Bu proje şu araçlar kullanılarak geliştirildi:
- TradingView Pine Script XTUMY V27 (original strategy)
- Python, Flask, SQLAlchemy (backend)
- Next.js, React, Tailwind CSS (frontend)
- PostgreSQL (database)
- tvDatafeed (market data)

**Strateji Sahibi:** XTUMY V27 yaratıcısı  
**Geliştirici:** Python Screener implementasyonu

---

## 📧 **İLETİŞİM & DESTEK**

Sorularınız ve geri bildirimleriniz için:
- GitHub Issues: [bist-analyst](https://github.com/celikcedev/bist-analyst/issues)
- Email: [Proje sahibi ile iletişim]

---

**Son Güncelleme:** 9 Aralık 2024  
**Versiyon:** 1.0.0  
**Durum:** ✅ Production Ready - %100 Pine Script Uyumlu
