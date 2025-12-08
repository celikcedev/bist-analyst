# Backend Restart Talimatları (Parametre Hatası Düzeltildi!)

## 🐛 Sorun:
"Parametreler kaydedilemedi. Lütfen tekrar deneyin." hatası alıyordunuz.

## ✅ Çözüm:
1. Backend endpoint'leri `strategy_name` (string) kabul edecek şekilde güncellendi
2. `StrategyParameter` modeline yeni kolonlar eklendi:
   - `parameter_type` (int/float/str/bool)
   - `display_name` (Türkçe görünen isim)
   - `display_group` (Grup başlığı)
   - `display_order` (Sıralama)
3. Database migration çalıştırıldı
4. Tüm parametreler veritabanına kaydedildi

---

## 🔄 Backend'i Yeniden Başlatın:

### Adım 1: Backend'i Durdurun
Backend terminalinde `Ctrl+C` yapın veya:

```bash
lsof -ti:5001 | xargs kill -9
```

### Adım 2: Backend'i Tekrar Başlatın
```bash
cd /Users/ademcelik/Desktop/bist_analyst
source .venv/bin/activate
PORT=5001 python run_backend.py
```

**Göreceğiniz:**
```
🚀 Starting BIST Analyst API on port 5001
 * Serving Flask app 'backend.main'
 * Running on http://127.0.0.1:5001
```

---

## ✅ Test Edin:

1. **Backend çalışıyor mu?**
   ```bash
   curl http://localhost:5001/api/health
   ```
   Beklenen: `{"status": "healthy"}`

2. **Parametreler yükleniyor mu?**
   ```bash
   curl http://localhost:5001/api/screener/strategies/XTUMYV27Strategy/parameters
   ```
   Beklenen: 12 adet parametre döner

3. **Screener UI'da test edin:**
   - http://localhost:3001 açın
   - Settings (⚙️) icon'a tıklayın
   - **Beklenen:** Parametreler gruplu şekilde görünecek:
     - ANA TREND AYARLARI
     - GÜÇ VE YÖN FİLTRELERİ
     - FİBO KIRILIM AYARLARI
     - PULLBACK (GERİ ÇEKİLME) AYARLARI
     - KURUMSAL DİP (SESSİZ TOPLAMA) AYARLARI
     - UYARI AYARLARI

---

## 🎯 Şimdi Yapılacaklar:

1. ✅ Backend'i restart edin (yukarıdaki adımlar)
2. ✅ Settings modal'ı açın
3. ✅ Parametreleri görün
4. ✅ Bir parametreyi değiştirin (örn: ADX Eşiği: 20 → 25)
5. ✅ "Uygula" butonuna tıklayın
6. ✅ **BAŞARILI!** Modal kapanacak
7. ✅ Tekrar açıp değişikliği kontrol edin

---

## 🎉 Sonuç:

Artık parametreler:
- ✅ Gruplu şekilde gösterilecek
- ✅ Türkçe isimlerle gösterilecek
- ✅ Düzenlenebilecek
- ✅ Veritabanına kaydedilecek
- ✅ Her kullanıcı için ayrı saklanacak
