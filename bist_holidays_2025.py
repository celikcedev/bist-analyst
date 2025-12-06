"""
BIST 2025 Yılı Resmi Tatil Günleri (Statik Veri - PDF'den)
Kaynak: https://www.borsaistanbul.com/files/pay-piyasasi-2025-yili-tatil-tablosu.pdf
"""
from datetime import datetime, time

BIST_HOLIDAYS_2025 = [
    # Yılbaşı
    {
        'holiday_date': datetime(2025, 1, 1).date(),
        'holiday_name': 'Yılbaşı',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '1 Ocak 2025 Çarşamba seans yapılmayacaktır.'
    },
    
    # Ramazan Bayramı
    {
        'holiday_date': datetime(2025, 3, 29).date(),
        'holiday_name': 'Ramazan Bayramı Arifesi',
        'status': 'YARIM_GUN',
        'closing_time': time(13, 0),
        'year': 2025,
        'notes': '29 Mart 2025 Cumartesi (Arife-Yarım gün)'
    },
    {
        'holiday_date': datetime(2025, 3, 30).date(),
        'holiday_name': 'Ramazan Bayramı 1. Gün',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '30 Mart 2025 Pazar'
    },
    {
        'holiday_date': datetime(2025, 3, 31).date(),
        'holiday_name': 'Ramazan Bayramı 2. Gün',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '31 Mart 2025 Pazartesi'
    },
    {
        'holiday_date': datetime(2025, 4, 1).date(),
        'holiday_name': 'Ramazan Bayramı 3. Gün',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '1 Nisan 2025 Salı'
    },
    
    # Ulusal Egemenlik ve Çocuk Bayramı
    {
        'holiday_date': datetime(2025, 4, 23).date(),
        'holiday_name': 'Ulusal Egemenlik ve Çocuk Bayramı',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '23 Nisan 2025 Çarşamba seans yapılmayacaktır.'
    },
    
    # Emek ve Dayanışma Günü
    {
        'holiday_date': datetime(2025, 5, 1).date(),
        'holiday_name': 'Emek ve Dayanışma Günü',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '1 Mayıs 2025 Perşembe seans yapılmayacaktır.'
    },
    
    # Atatürk'ü Anma, Gençlik ve Spor Bayramı
    {
        'holiday_date': datetime(2025, 5, 19).date(),
        'holiday_name': 'Atatürk\'ü Anma, Gençlik ve Spor Bayramı',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '19 Mayıs 2025 Pazartesi seans yapılmayacaktır.'
    },
    
    # Kurban Bayramı
    {
        'holiday_date': datetime(2025, 6, 5).date(),
        'holiday_name': 'Kurban Bayramı Arifesi',
        'status': 'YARIM_GUN',
        'closing_time': time(13, 0),
        'year': 2025,
        'notes': '5 Haziran 2025 Perşembe yarım gün seans yapılacaktır.'
    },
    {
        'holiday_date': datetime(2025, 6, 6).date(),
        'holiday_name': 'Kurban Bayramı 1. Gün',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '6 Haziran 2025 Cuma'
    },
    {
        'holiday_date': datetime(2025, 6, 7).date(),
        'holiday_name': 'Kurban Bayramı 2. Gün',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '7 Haziran 2025 Cumartesi'
    },
    {
        'holiday_date': datetime(2025, 6, 8).date(),
        'holiday_name': 'Kurban Bayramı 3. Gün',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '8 Haziran 2025 Pazar'
    },
    {
        'holiday_date': datetime(2025, 6, 9).date(),
        'holiday_name': 'Kurban Bayramı 4. Gün',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '9 Haziran 2025 Pazartesi'
    },
    
    # Demokrasi ve Milli Birlik Günü
    {
        'holiday_date': datetime(2025, 7, 15).date(),
        'holiday_name': 'Demokrasi ve Milli Birlik Günü',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '15 Temmuz 2025 Salı seans yapılmayacaktır.'
    },
    
    # Zafer Bayramı
    {
        'holiday_date': datetime(2025, 8, 30).date(),
        'holiday_name': 'Zafer Bayramı',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '30 Ağustos 2025 Cumartesi seans yapılmayacaktır.'
    },
    
    # Cumhuriyet Bayramı
    {
        'holiday_date': datetime(2025, 10, 28).date(),
        'holiday_name': 'Cumhuriyet Bayramı Arifesi',
        'status': 'YARIM_GUN',
        'closing_time': time(13, 0),
        'year': 2025,
        'notes': '28 Ekim 2025 Salı yarım gün seans yapılacaktır.'
    },
    {
        'holiday_date': datetime(2025, 10, 29).date(),
        'holiday_name': 'Cumhuriyet Bayramı',
        'status': 'KAPALI',
        'closing_time': None,
        'year': 2025,
        'notes': '29 Ekim 2025 Çarşamba seans yapılmayacaktır.'
    },
]

def load_2025_holidays_to_db():
    """2025 tatillerini veritabanına yükle"""
    from bist_calendar import BISTCalendar
    
    calendar = BISTCalendar()
    calendar.init_calendar_table()
    calendar.save_holidays_to_db(BIST_HOLIDAYS_2025)
    
    print("✅ 2025 yılı tatilleri yüklendi!")

if __name__ == "__main__":
    load_2025_holidays_to_db()

