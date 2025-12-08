# Market Data Kurulum Talimatları

## 🎯 Durum:
- ✅ 593 hisse kodu veritabanında var
- ❌ OHLCV bar verileri yok (0 adet)
- ❌ Bu yüzden tarama yapılamıyor

## 📥 İlk Veri Çekimi (1 Yıllık):

### Adım 1: .env Dosyanızı Kontrol Edin

`/Users/ademcelik/Desktop/bist_analyst/.env` dosyasında TradingView bilgilerinizin olduğundan emin olun:

```bash
# TradingView Credentials
TV_USERNAME=your_username
TV_PASSWORD=your_password
```

### Adım 2: Veri Çekme Scriptini Çalıştırın

**Yeni bir terminal açın:**

```bash
cd /Users/ademcelik/Desktop/bist_analyst
source .venv/bin/activate
python3 run_data_update.py
```

### Adım 3: İşlem Süresi

- **593 hisse** için **1 yıllık** veri çekilecek
- **Tahmini süre:** 15-30 dakika
- Her hisse için ~252 bar (1 yıl günlük)
- **Toplam:** ~150,000 bar verisi

**Göreceğiniz:**
```
📊 Starting market data update for BIST stocks
📅 Fetching data for symbol 1/593: A1CAP
✓ A1CAP: 252 bars fetched
📅 Fetching data for symbol 2/593: ACSEL
✓ ACSEL: 252 bars fetched
...
✅ Market data update completed: 593 symbols processed
```

---

## ⚠️ Önemli Notlar:

1. **TradingView Rate Limit:**
   - TradingView API'si rate limit'e sahip
   - Çok hızlı istek atarsanız geçici olarak engellenebilirsiniz
   - Script otomatik olarak retry yapar

2. **İlk Çekim Uzun Sürer:**
   - 1 yıllık veri çekildiği için ilk çekim uzun sürer
   - Sonraki güncellemeler çok daha hızlı olur (sadece son gün)

3. **Hata Alırsanız:**
   - TV_USERNAME ve TV_PASSWORD'ün doğru olduğundan emin olun
   - TradingView hesabınızın aktif olduğundan emin olun
   - Script'i tekrar çalıştırabilirsiniz (kaldığı yerden devam eder)

---

## ✅ Veri Çekildikten Sonra:

1. **Veriyi Kontrol Edin:**
   ```bash
   PYTHONPATH=/Users/ademcelik/Desktop/bist_analyst python3 -c "
   from backend.core.database import get_db_session
   from backend.modules.market_data.models import MarketData
   
   with get_db_session() as session:
       count = session.query(MarketData).count()
       print(f'Market Data: {count:,} bars')
   "
   ```
   
   **Beklenen:** `Market Data: ~150,000 bars`

2. **Screener'da Tarama Yapın:**
   - http://localhost:3001 açın
   - Signal type chip'lerinden birini **True** yapın
   - **Scan** butonuna tıklayın
   - **SONUÇLAR GELECEK!** 🎉

---

## 🔄 Günlük Güncelleme (Cron Job):

Veri çekimi tamamlandıktan sonra, günlük otomatik güncelleme için:

```bash
# Cron job ekleyin (her gün saat 18:35'te)
crontab -e

# Şunu ekleyin:
35 18 * * 1-5 cd /Users/ademcelik/Desktop/bist_analyst && source .venv/bin/activate && python3 backend/modules/market_data/updater.py >> logs/data_update.log 2>&1
```

---

## 💡 Hızlı Test (Tek Hisse):

Tüm verileri çekmeden önce test etmek isterseniz:

```python
# test_single_fetch.py oluşturun
from tvDatafeed import TvDatafeed, Interval
import os
from dotenv import load_dotenv

load_dotenv()

tv = TvDatafeed(
    username=os.getenv('TV_USERNAME'),
    password=os.getenv('TV_PASSWORD')
)

# Tek hisse test
df = tv.get_hist(
    symbol='THYAO',
    exchange='BIST',
    interval=Interval.in_daily,
    n_bars=10
)

print(df)
```

Çalıştırın:
```bash
python3 test_single_fetch.py
```

Başarılıysa → Tüm verileri çekin!
