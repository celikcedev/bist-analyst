"""
Borsa İstanbul Tatil Günleri ve İşlem Saatleri Yönetimi
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, time
from config import DB_CONNECTION_STR
import logging
from config import LOG_DIR

logging.basicConfig(filename=f'{LOG_DIR}/bist_calendar.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

class BISTCalendar:
    """Borsa İstanbul resmi tatil günleri ve işlem saatleri yöneticisi"""
    
    def __init__(self):
        self.engine = create_engine(DB_CONNECTION_STR)
        self.html_url = "https://www.borsaistanbul.com/tr/sayfa/149/resmi-tatil-gunleri"
        self.pdf_url = "https://www.borsaistanbul.com/files/pay-piyasasi-2025-yili-tatil-tablosu.pdf"
        
    def init_calendar_table(self):
        """Tatil günleri tablosunu oluştur"""
        sql = """
        CREATE TABLE IF NOT EXISTS bist_holidays (
            id SERIAL PRIMARY KEY,
            holiday_date DATE NOT NULL,
            holiday_name VARCHAR(255),
            status VARCHAR(50),  -- 'KAPALI', 'YARIM_GUN', 'ACIK'
            closing_time TIME,    -- Yarım gün ise kapanış saati
            year INT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(holiday_date)
        );
        
        CREATE INDEX IF NOT EXISTS idx_holiday_date ON bist_holidays(holiday_date);
        CREATE INDEX IF NOT EXISTS idx_holiday_year ON bist_holidays(year);
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        
        print("✓ BIST tatil günleri tablosu oluşturuldu.")
        logging.info("BIST holidays table created/verified.")
    
    def fetch_holidays_from_html(self, year=2026):
        """
        HTML sayfasından tatil günlerini çek
        URL: https://www.borsaistanbul.com/tr/sayfa/149/resmi-tatil-gunleri
        """
        try:
            print(f"\n{year} yılı tatil günleri çekiliyor...")
            
            response = requests.get(self.html_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Yıl seçim kutusunu bul ve doğru yıla geç (JavaScript gerektirebilir)
            # Basit yaklaşım: 2025 ve 2026 için statik veriler
            
            # Tabloyu bul
            table = soup.find('table', class_='table')
            
            if not table:
                print("❌ Tablo bulunamadı!")
                return []
            
            rows = table.find('tbody').find_all('tr')
            holidays = []
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    date_str = cols[0].text.strip()
                    holiday_name = cols[1].text.strip()
                    status_str = cols[2].text.strip().lower()
                    
                    # Durumu belirle
                    if 'kapalı' in status_str:
                        status = 'KAPALI'
                        closing_time = None
                    elif '13:00' in status_str or 'yarım' in status_str:
                        status = 'YARIM_GUN'
                        closing_time = time(13, 0)
                    else:
                        status = 'ACIK'
                        closing_time = None
                    
                    # Tarihi parse et
                    try:
                        # Format: "1 Ocak 2026, Perşembe"
                        date_parts = date_str.split(',')[0].strip()
                        holiday_date = self._parse_turkish_date(date_parts, year)
                        
                        holidays.append({
                            'holiday_date': holiday_date,
                            'holiday_name': holiday_name,
                            'status': status,
                            'closing_time': closing_time,
                            'year': year,
                            'notes': status_str
                        })
                    except Exception as e:
                        print(f"⚠️  Tarih parse hatası: {date_str} - {e}")
                        continue
            
            print(f"✓ {len(holidays)} tatil günü bulundu.")
            return holidays
            
        except Exception as e:
            print(f"❌ HTML çekme hatası: {e}")
            logging.error(f"HTML fetch error: {e}")
            return []
    
    def _parse_turkish_date(self, date_str, year):
        """Türkçe tarih string'ini datetime'a çevir"""
        months = {
            'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4,
            'mayıs': 5, 'haziran': 6, 'temmuz': 7, 'ağustos': 8,
            'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
        }
        
        # "1 Ocak 2026" veya "19 Mart 2026"
        parts = date_str.lower().split()
        day = int(parts[0])
        month_name = parts[1]
        month = months.get(month_name, 1)
        
        return datetime(year, month, day).date()
    
    def save_holidays_to_db(self, holidays):
        """Tatil günlerini veritabanına kaydet"""
        if not holidays:
            print("Kaydedilecek tatil günü yok.")
            return
        
        df = pd.DataFrame(holidays)
        
        # Upsert: Varsa güncelle, yoksa ekle
        with self.engine.connect() as conn:
            for _, row in df.iterrows():
                sql = text("""
                    INSERT INTO bist_holidays (holiday_date, holiday_name, status, closing_time, year, notes)
                    VALUES (:date, :name, :status, :time, :year, :notes)
                    ON CONFLICT (holiday_date) 
                    DO UPDATE SET 
                        holiday_name = EXCLUDED.holiday_name,
                        status = EXCLUDED.status,
                        closing_time = EXCLUDED.closing_time,
                        year = EXCLUDED.year,
                        notes = EXCLUDED.notes
                """)
                
                conn.execute(sql, {
                    'date': row['holiday_date'],
                    'name': row['holiday_name'],
                    'status': row['status'],
                    'time': row['closing_time'],
                    'year': row['year'],
                    'notes': row['notes']
                })
            
            conn.commit()
        
        print(f"✓ {len(holidays)} tatil günü veritabanına kaydedildi.")
        logging.info(f"{len(holidays)} holidays saved to database.")
    
    def is_market_open(self, check_date=None):
        """
        Belirli bir tarihte borsa açık mı?
        Returns: (bool, closing_time)
        """
        if check_date is None:
            check_date = datetime.now().date()
        
        # Hafta sonu kontrolü
        if check_date.weekday() >= 5:  # 5=Cumartesi, 6=Pazar
            return False, None
        
        # Veritabanından kontrol et
        query = text("SELECT status, closing_time FROM bist_holidays WHERE holiday_date = :date")
        with self.engine.connect() as conn:
            result = conn.execute(query, {'date': check_date}).fetchone()
        
        if result is None:
            # Tatil değil, normal açık
            return True, time(18, 10)  # Normal kapanış: 18:10
        
        status, closing_time = result
        
        if status == 'KAPALI':
            return False, None
        elif status == 'YARIM_GUN':
            return True, closing_time  # 13:00 gibi
        else:
            return True, time(18, 10)
    
    def update_calendar(self, year=2025):
        """Yıllık takvimi güncelle"""
        print(f"\n{'='*60}")
        print(f"BIST {year} Yılı Tatil Takvimi Güncelleniyor")
        print(f"{'='*60}")
        
        # Tabloyu oluştur
        self.init_calendar_table()
        
        # HTML'den çek
        holidays = self.fetch_holidays_from_html(year)
        
        # Veritabanına kaydet
        if holidays:
            self.save_holidays_to_db(holidays)
        
        print(f"\n✅ {year} takvimi güncellendi!")
        print(f"{'='*60}\n")

def main():
    """Manuel çalıştırma için"""
    calendar = BISTCalendar()
    
    # 2025 ve 2026 yıllarını güncelle
    calendar.update_calendar(2025)
    # calendar.update_calendar(2026)  # İsteğe bağlı
    
    # Test
    print("\nTest: Bugün borsa açık mı?")
    is_open, closing_time = calendar.is_market_open()
    if is_open:
        print(f"✓ Borsa AÇIK - Kapanış: {closing_time}")
    else:
        print("✗ Borsa KAPALI")

if __name__ == "__main__":
    main()

