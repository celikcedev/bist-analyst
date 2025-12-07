"""
Otomatik BIST Tatil Günleri Güncelleme
Her yıl Ocak ayının ilk haftasında yeni yıl tatillerini kontrol eder
"""
import os
import sys
from datetime import datetime
from bist_calendar import BISTCalendar
from sqlalchemy import create_engine, text
from config import DB_CONNECTION_STR, LOG_DIR
import logging

logging.basicConfig(filename=f'{LOG_DIR}/holiday_update.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

def check_and_update_holidays():
    """
    Yıl başında yeni tatil bilgilerini kontrol et ve güncelle
    - Ocak 1-7 arasında her gün çalışır
    - Başarılı güncelleme olursa işaretler
    - Bir sonraki yıla kadar bekler
    """
    current_year = datetime.now().year
    engine = create_engine(DB_CONNECTION_STR)
    
    print(f"{'='*60}")
    print(f"BIST Tatil Takvimi Otomatik Güncelleme - {current_year}")
    print(f"{'='*60}\n")
    
    # Bu yıl için tatil verisi var mı kontrol et
    query = text("SELECT COUNT(*) FROM bist_holidays WHERE year = :year")
    with engine.connect() as conn:
        count = conn.execute(query, {'year': current_year}).scalar()
    
    if count > 0:
        print(f"✓ {current_year} yılı takvimi zaten mevcut ({count} tatil günü)")
        print(f"  Güncelleme gerekmiyor.\n")
        logging.info(f"{current_year} calendar already exists with {count} holidays.")
        return True
    
    # Tatil bilgisi yok, güncelleme dene
    print(f"⚠️  {current_year} yılı takvimi bulunamadı!")
    print(f"📥 HTML'den çekiliyor...\n")
    
    try:
        calendar = BISTCalendar()
        calendar.init_calendar_table()
        
        # HTML'den çekmeyi dene
        holidays = calendar.fetch_holidays_from_html(current_year)
        
        if holidays and len(holidays) > 0:
            calendar.save_holidays_to_db(holidays)
            print(f"✅ {current_year} takvimi başarıyla güncellendi!")
            logging.info(f"{current_year} calendar updated with {len(holidays)} holidays.")
            return True
        else:
            print(f"⚠️  HTML'den veri çekilemedi.")
            print(f"   Statik veri modülünü kontrol edin: bist_holidays_{current_year}.py")
            logging.warning(f"Could not fetch {current_year} holidays from HTML.")
            
            # Statik dosya var mı kontrol et
            static_file = f"bist_holidays_{current_year}.py"
            if os.path.exists(static_file):
                print(f"   {static_file} dosyası bulundu, çalıştırılıyor...")
                os.system(f"python3.11 {static_file}")
                return True
            else:
                print(f"   ❌ {static_file} dosyası bulunamadı!")
                print(f"   Manuel olarak oluşturup çalıştırın.")
                return False
                
    except Exception as e:
        print(f"❌ Hata: {e}")
        logging.error(f"Holiday update error: {e}")
        return False

def main():
    """
    Kullanım:
    - Manuel: python3.11 auto_update_holidays.py
    - Cron: Her gün Ocak 1-7 arasında 00:05'te çalışır
    """
    now = datetime.now()
    
    # Sadece Ocak 1-7 arasındaysa veya --force flag varsa çalış
    if '--force' in sys.argv:
        print("🔧 FORCE modu aktif - Yıl kontrolü atlandı\n")
        check_and_update_holidays()
    elif now.month == 1 and now.day <= 7:
        check_and_update_holidays()
    else:
        print(f"ℹ️  Bugün {now.strftime('%d %B %Y')}")
        print(f"   Ocak 1-7 arasında değil, güncelleme atlandı.")
        print(f"   Manuel güncelleme için: python3.11 auto_update_holidays.py --force")

if __name__ == "__main__":
    main()

