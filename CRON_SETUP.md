# Cron Job Kurulum Kılavuzu

## 🎯 Otomatik Günlük İşlemler

Borsa kapandıktan sonra her gün otomatik olarak:
1. **18:35** - Günün bar verileri çekilir (sadece yeni günler)
2. **18:40** - Tarama yapılır ve sinyaller üretilir
3. **18:40** - Telegram bildirimi gönderilir (isteğe bağlı)

---

## 📋 Özellikler

### 1. Günlük Veri Güncellemesi (`run_data_update.py`)

**Ne yapar:**
- Veritabanında son tarihi kontrol eder
- Sadece eksik günleri çeker (upsert mantığı)
- İlk günden sonra çok hızlıdır (~2-3 dakika)
- Rate limit'e takılmaz

**Örnek:**
```
Veritabanında son tarih: 2025-12-06
Bugün: 2025-12-07
→ Sadece 2025-12-07 verisi çekilir (593 hisse)
```

### 2. Günlük Tarama (`scripts/run_scan.py`)

**Ne yapar:**
- XTUMY V27 stratejisini çalıştırır
- Bugünün sinyallerini bulur
- Veritabanına kaydeder
- Telegram'a bildirim gönderir

---

## 🔧 Kurulum Adımları

### Adım 1: Setup Script'ini Çalıştırın

```bash
cd /Users/ademcelik/Desktop/bist_analyst
./setup_cron_jobs.sh
```

Bu size kopyalayabileceğiniz cron job komutlarını gösterecek.

### Adım 2: Crontab'ı Düzenleyin

```bash
crontab -e
```

### Adım 3: Aşağıdaki Satırları Ekleyin

```bash
# BIST Analyst - Daily Market Data Update
35 18 * * 1-5 cd /Users/ademcelik/Desktop/bist_analyst && source .venv/bin/activate && python3 run_data_update.py >> logs/data_update_cron.log 2>&1

# BIST Analyst - Daily Signal Scan
40 18 * * 1-5 cd /Users/ademcelik/Desktop/bist_analyst && source .venv/bin/activate && python3 scripts/run_scan.py XTUMYV27Strategy >> logs/scan_cron.log 2>&1
```

**Açıklama:**
- `35 18 * * 1-5` → Pazartesi-Cuma, 18:35
- `40 18 * * 1-5` → Pazartesi-Cuma, 18:40
- `>> logs/...log 2>&1` → Çıktıyı log dosyasına yaz

### Adım 4: Kaydet ve Çık

Vi/Vim editöründe:
1. `i` tuşuna basın (insert mode)
2. Yukarıdaki satırları yapıştırın
3. `ESC` tuşuna basın
4. `:wq` yazıp `ENTER` basın

---

## ✅ Kontrol

### Cron Job'ları Listele

```bash
crontab -l
```

**Göreceğiniz:**
```
# BIST Analyst - Daily Market Data Update
35 18 * * 1-5 cd /Users/ademcelik/Desktop/bist_analyst...
# BIST Analyst - Daily Signal Scan
40 18 * * 1-5 cd /Users/ademcelik/Desktop/bist_analyst...
```

### Log Dosyalarını Takip Et

```bash
# Veri güncelleme logu
tail -f logs/data_update_cron.log

# Tarama logu
tail -f logs/scan_cron.log
```

---

## 🧪 Manuel Test

Cron job eklemeden önce manuel test edin:

### Test 1: Veri Güncellemesi

```bash
cd /Users/ademcelik/Desktop/bist_analyst
source .venv/bin/activate
python3 run_data_update.py
```

**Beklenen:** "Güncelleme tamamlandı. X hisse güncellendi, Y atlandı (güncel)"

### Test 2: Tarama

```bash
cd /Users/ademcelik/Desktop/bist_analyst
source .venv/bin/activate
python3 scripts/run_scan.py XTUMYV27Strategy
```

**Beklenen:** "Tarama tamamlandı. X sinyal bulundu."

---

## ⚙️ Gelişmiş Ayarlar

### Telegram Bildirimlerini Aktifleştir

`.env` dosyasında:

```bash
ENABLE_TELEGRAM=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Farklı Saatte Çalıştır

Örneğin 19:00 ve 19:05 için:

```bash
0 19 * * 1-5 cd /Users/ademcelik/Desktop/bist_analyst...
5 19 * * 1-5 cd /Users/ademcelik/Desktop/bist_analyst...
```

### Sadece Belirli Günler

Örneğin sadece Cuma:

```bash
35 18 * * 5 cd /Users/ademcelik/Desktop/bist_analyst...
```

---

## 🐛 Sorun Giderme

### Cron Job Çalışmıyor

1. **Cron log'unu kontrol edin:**
   ```bash
   tail -100 logs/data_update_cron.log
   ```

2. **Cron daemon çalışıyor mu:**
   ```bash
   sudo launchctl list | grep cron
   ```

3. **Manuel olarak çalışıyor mu:**
   ```bash
   cd /Users/ademcelik/Desktop/bist_analyst
   source .venv/bin/activate
   python3 run_data_update.py
   ```

### Veri Güncellenmiyor

- TradingView credentials doğru mu? (`.env`)
- Internet bağlantısı var mı?
- Rate limit'e takılmış olabilir (1 saat bekleyin)

### Telegram Bildirimi Gelmiyor

- `ENABLE_TELEGRAM=true` mi?
- Bot token ve chat ID doğru mu?
- Bot chat'e eklenmiş mi?

---

## 📊 Günlük İşlem Akışı

```
17:30 → Borsa kapanır
18:00 → TradingView verileri günceller
18:35 → Cron: Veri çekme başlar
18:37 → Veri çekme tamamlanır (593 hisse, ~2 dakika)
18:40 → Cron: Tarama başlar
18:42 → Tarama tamamlanır, sinyaller kaydedilir
18:42 → Telegram bildirimi gönderilir
```

---

## 💡 Pro Tips

1. **İlk Hafta:** Log'ları her gün kontrol edin
2. **Yedekleme:** Veritabanını haftalık yedekleyin
3. **Monitoring:** Cron job çalışmazsa e-posta bildirimi ekleyin
4. **Performans:** İlk ay sonra istatistikleri inceleyin

---

## 📚 Kaynaklar

- Cron syntax: https://crontab.guru/
- Cron troubleshooting: `man cron`
- Log rotation: `man logrotate`
