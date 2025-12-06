# 🚀 BIST Analyst - Autonomous Trading Signal Scanner

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-14+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production](https://img.shields.io/badge/status-production-green.svg)]()

**BIST Analyst**, Borsa İstanbul (BIST) hisselerini **XTUMY V27** teknik analiz stratejisiyle otomatik olarak tarayan, gerçek zamanlı sinyal üreten ve Telegram bildirimleri gönderen otonom bir Python sistemidir.

TradingView Pine Script algoritmasının **%100 matematiksel uyumlu** Python implementasyonu ile günlük sinyal taraması yapar.

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Sinyal Türleri](#-sinyal-türleri)
- [Teknolojiler](#-teknolojiler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Otomasyon](#-otomasyon)
- [Mimari](#-mimari)
- [Performans](#-performans)
- [Gelecek Özellikler](#-gelecek-özellikler)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

---

## ✨ Özellikler

### 🎯 6 Farklı Sinyal Türü
1. **KURUMSAL DİP** - Ayı yapısında sessiz kurumsal toplama
2. **TREND BAŞLANGIÇ** - EMA50 kırılımı ile yeni yükseliş trendi
3. **PULLBACK AL** - EMA50 retesti (geri çekilme alımı)
4. **DİP AL** - Fibonacci 0.000 (dip) seviyesi
5. **ALTIN KIRILIM** - Golden ratio (0.618) breakout
6. **ZİRVE KIRILIMI** - Resistance breakout (ATH kırılımı)

### 🔧 Temel Özellikler
- ✅ **TradingView %100 Uyumlu** - Pine Script ile matematiksel eşdeğer
- ✅ **Otomatik Veri Güncelleme** - Günlük OHLCV verisi çekimi
- ✅ **Telegram Bildirimleri** - Gerçek zamanlı sinyal uyarıları
- ✅ **Multi-User Destek** - Birden fazla kullanıcıya bildirim
- ✅ **Akıllı Zamanlayıcı** - Yarım gün/normal mesai otomatik tespit
- ✅ **Tatil Takvimi** - BIST resmi tatil günleri entegrasyonu
- ✅ **Health Check** - Sistem sağlık monitörü
- ✅ **PostgreSQL** - Yerel veritabanı ile hızlı erişim

---

## 📊 Sinyal Türleri

### 1. KURUMSAL DİP 🏦
Ayı yapısında (EMA20 < EMA50) sessiz kurumsal toplama sinyali.

**Kriterler:**
- Fiyat EMA20'yi yukarı kesiyor
- RSI > RSI MA ve yükseliyor
- Hacim stabil (0.3x - 1.5x)
- Yeşil mum kapanışı

### 2. TREND BAŞLANGIÇ 🚀
EMA50 kırılımı ile yeni yükseliş trendi başlangıcı.

**Kriterler:**
- 1 bar önce EMA50 crossover
- Hacim güçlü (>1.0x)
- Fiyat EMA50 üstünde kaldı
- DI+ > DI-

### 3. PULLBACK AL ↩️
Trend oturduktan sonra EMA50'ye geri çekilme alımı.

**Kriterler:**
- Trend mature (crossover + 3 bar)
- Fiyat EMA50'ye yaklaştı (%2 tolerans)
- Hala EMA50 üstünde
- RSI > 45, Hacim güçlü

### 4. DİP AL 📉
Fibonacci 0.000 (son 144 bar dibi) yakınında alım.

**Kriterler:**
- Fiyat dip seviyesinin %2'si içinde
- RSI yükseliyor
- Yeşil mum, DI+ > DI-

### 5. ALTIN KIRILIM 🥇
Golden ratio (0.618) Fibonacci seviyesi kırılımı.

**Kriterler:**
- 0.618 seviyesi crossover
- Hacim güçlü (>1.2x)
- 10 bar cooldown

### 6. ZİRVE KIRILIMI ⛰️
Son 144 bar en yüksek seviyesi (ATH) kırılımı.

**Kriterler:**
- Resistance breakout
- Hacim güçlü (>1.2x)
- 10 bar cooldown

---

## 🛠️ Teknolojiler

| Teknoloji | Versiyon | Açıklama |
|-----------|----------|----------|
| **Python** | 3.11+ | Ana programlama dili |
| **PostgreSQL** | 14+ | Veritabanı |
| **SQLAlchemy** | 2.0+ | ORM ve veritabanı yönetimi |
| **Pandas** | 2.0+ | Veri işleme |
| **NumPy** | 1.24+ | Sayısal hesaplamalar |
| **tvDatafeed** | 2.1+ | TradingView veri kaynağı |
| **tradingview-screener** | 3.0+ | Ticker listesi |
| **python-telegram-bot** | 22.0+ | Telegram entegrasyonu |
| **BeautifulSoup4** | 4.14+ | HTML parsing (tatil takvimi) |
| **Cron** | - | Otomatik zamanlama |

---

## 🚀 Kurulum

### 1. Ön Gereksinimler

```bash
# macOS
brew install python@3.11 postgresql@14

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql-14
```

### 2. PostgreSQL Kurulumu

```bash
# PostgreSQL başlat
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux

# Kullanıcı ve veritabanı oluştur
createuser -s postgres
psql postgres -c "ALTER USER postgres PASSWORD 'your_password';"
createdb -U postgres trading_db
```

### 3. Proje Kurulumu

```bash
# Repository'yi klonla
git clone https://github.com/celikcedev/bist-analyst.git
cd bist-analyst

# Virtual environment oluştur
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 4. Konfigürasyon

```bash
# .env dosyası oluştur
cp .example-env .env
nano .env
```

**`.env` dosyasını düzenle:**
```bash
# Database
DB_PASS=your_postgresql_password

# TradingView
TV_USERNAME=your_email@example.com
TV_PASSWORD=your_tv_password

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_BotFather
TELEGRAM_CHAT_ID=your_chat_id,friend_chat_id  # Virgülle ayır
ENABLE_TELEGRAM=true
```

### 5. Veritabanı İlklendirme

```bash
python db_manager.py
python bist_holidays_2025.py
```

### 6. İlk Veri Çekimi

```bash
# Ticker listesi (~590 hisse)
python fetch_tickers.py

# 1 yıllık OHLCV verisi (~1.5 dakika)
python update_market_data.py
```

### 7. İlk Tarama

```bash
# Konsola yazdır
python scanner_xtumy.py

# Telegram'a gönder
python scanner_xtumy.py --telegram
```

---

## 💻 Kullanım

### Manuel Tarama

```bash
# Aktif et
source .venv/bin/activate

# Tarama yap
python scanner_xtumy.py

# Telegram ile
python scanner_xtumy.py --telegram
```

### Sistem Sağlık Kontrolü

```bash
python health_check.py
```

### Veri Güncelleme

```bash
# Eksik günleri otomatik tamamlar
python update_market_data.py
```

---

## 🤖 Otomasyon

### Cron Jobs Kurulumu

```bash
# Crontab düzenle
crontab -e

# Aşağıdaki satırları ekle (yolları düzenle):
```

```cron
# Değişkenler
PYTHON=/opt/homebrew/bin/python3.11
PROJECT=/path/to/bist_analyst

# Health check (Her sabah 09:00)
0 9 * * * $PYTHON $PROJECT/health_check.py >> $PROJECT/logs/cron_health.log 2>&1

# Veri güncelleme (Hafta içi 13:05 ve 18:35)
5 13 * * 1-5 $PYTHON $PROJECT/smart_scheduler.py --update >> $PROJECT/logs/cron_data.log 2>&1
35 18 * * 1-5 $PYTHON $PROJECT/smart_scheduler.py --update >> $PROJECT/logs/cron_data.log 2>&1

# Tarama + Telegram (Hafta içi 13:10 ve 18:40)
10 13 * * 1-5 $PYTHON $PROJECT/scanner_xtumy.py --telegram >> $PROJECT/logs/cron_scanner.log 2>&1
40 18 * * 1-5 $PYTHON $PROJECT/scanner_xtumy.py --telegram >> $PROJECT/logs/cron_scanner.log 2>&1

# Ticker güncelleme (Pazar 23:00)
0 23 * * 0 $PYTHON $PROJECT/fetch_tickers.py >> $PROJECT/logs/cron_ticker.log 2>&1

# Tatil güncelleme (Ocak 1-7, 00:05)
5 0 1-7 1 * $PYTHON $PROJECT/auto_update_holidays.py >> $PROJECT/logs/cron_holidays.log 2>&1
```

### macOS Cron İzinleri

```bash
# System Settings > Privacy & Security > Full Disk Access
# /usr/sbin/cron'u ekle
```

---

## 🏗️ Mimari

```
bist_analyst/
├── config.py                   # Merkezi konfigürasyon
├── db_manager.py               # Veritabanı setup
├── fetch_tickers.py            # Ticker listesi güncelleme
├── update_market_data.py       # OHLCV veri güncelleme
├── scanner_xtumy.py            # XTUMY V27 tarayıcı (ana motor)
├── telegram_bot.py             # Telegram entegrasyonu
├── bist_calendar.py            # Tatil takvimi yönetimi
├── bist_holidays_2025.py       # 2025 tatil verileri
├── auto_update_holidays.py     # Otomatik tatil güncelleme
├── smart_scheduler.py          # Akıllı zamanlayıcı
├── health_check.py             # Sistem monitörü
├── .env                        # Çevre değişkenleri (GİZLİ!)
├── .example-env                # Örnek konfigürasyon
├── requirements.txt            # Python bağımlılıkları
├── logs/                       # Log dosyaları
│   ├── cron_scanner.log
│   ├── cron_data.log
│   ├── cron_health.log
│   └── telegram.log
└── README.md
```

---

## 📈 Performans

| Metrik | Değer |
|--------|-------|
| **Tarama Süresi** | ~6 saniye (593 hisse) |
| **Veri Güncelleme** | ~1.5 saniye (günlük), ~15 dakika (ilk çekim) |
| **Bellek Kullanımı** | ~200MB |
| **CPU** | Minimal (single-core yeterli) |
| **TradingView Uyumu** | %100 ✅ |
| **Veri Window** | 250 bar (~1 yıl) - İstatistiksel %100 trend coverage |

---

## 📱 Telegram Bildirimleri

### Bot Oluşturma

1. Telegram'da [@BotFather](https://t.me/BotFather)'a mesaj atın
2. `/newbot` komutunu kullanın
3. Bot token'ınızı alın
4. Chat ID öğrenmek için [@userinfobot](https://t.me/userinfobot)'a mesaj atın

### Örnek Bildirim

```
🚀 XTUMY V27 Tarama Sonuçları
📅 07 Aralık 2025
📊 Toplam 38 Sinyal
──────────────────────────────

🏦 KURUMSAL DİP (23 adet)
──────────────────────────────
• AFYON - 13.13 TL
  RSI: 48.5 | ADX: 17.3
  📈 Grafiği Aç

• ASELS - 188.20 TL
  RSI: 49.1 | ADX: 22.6
  📈 Grafiği Aç

...
```

---

## 🔮 Gelecek Özellikler

### Kısa Vadede (1-2 Hafta)
- [ ] **Performans İzleme** - Sinyal başarı oranı tracking
- [ ] **Backtest Modülü** - Geçmiş 1 yıl simülasyonu
- [ ] **Watchlist** - Belirli hisseleri takip

### Uzun Vadede (1-2 Ay)
- [ ] **Web Dashboard** - Flask + Next.js UI
- [ ] **Multi-Timeframe** - 1H, 4H, günlük analiz
- [ ] **Docker Deployment** - Containerization
- [ ] **API** - REST API endpoints

Detaylar: [NEXT_STEPS.md](NEXT_STEPS.md)

---

## 🛠️ Troubleshooting

### Veri Çekilmiyor

```bash
# TradingView credentials kontrol
cat .env | grep TV_

# Manuel test
python -c "from tvdatafeed import TvDatafeed; tv = TvDatafeed('email', 'pass'); print(tv.get_hist('THYAO', 'BIST'))"
```

### Sinyal Bulunamıyor

```bash
# Veri kontrol
psql -U postgres -d trading_db -c "SELECT COUNT(*) FROM market_data WHERE date > NOW() - INTERVAL '7 days';"

# Log kontrol
tail -f logs/scanner.log
```

### Telegram Gönderilmiyor

```bash
# Bot'a /start yazıldı mı kontrol et
# Credentials test
python telegram_bot.py

# Log kontrol
tail -f logs/telegram.log
```

---

## 🤝 Katkıda Bulunma

Katkılar memnuniyetle karşılanır! Lütfen:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

## 👤 Yazar

**Adem Celik**
- Email: mysound74@hotmail.com
- GitHub: [@celikcedev](https://github.com/celikcedev)
- TradingView: XTUMY V27 Strategy

---

## 🙏 Teşekkürler

- [TradingView](https://www.tradingview.com) - Pine Script ve veri kaynağı
- [tvDatafeed](https://github.com/rongardF/tvdatafeed) - TradingView data library
- [Borsa İstanbul](https://www.borsaistanbul.com) - Resmi tatil takvimi

---

## 📊 Proje Durumu

![GitHub last commit](https://img.shields.io/github/last-commit/celikcedev/bist-analyst)
![GitHub issues](https://img.shields.io/github/issues/celikcedev/bist-analyst)
![GitHub stars](https://img.shields.io/github/stars/celikcedev/bist-analyst)

**Durum:** 🟢 Production - Aktif Kullanımda

---

**Son Güncelleme:** 7 Aralık 2025  
**Versiyon:** 3.1

