"""
Akıllı Zamanlayıcı - Yarım Gün Mesai Kontrolü
Borsa tatil günlerini ve yarım gün mesaileri kontrol ederek
doğru zamanda veri çekmeyi sağlar
"""
import sys
import os
from datetime import datetime, time
from bist_calendar import BISTCalendar
import logging
from config import LOG_DIR

logging.basicConfig(filename=f'{LOG_DIR}/scheduler.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

class SmartScheduler:
    """Akıllı görev zamanlayıcı"""
    
    def __init__(self):
        self.calendar = BISTCalendar()
    
    def should_run_today(self):
        """
        Bugün veri çekimi yapılmalı mı?
        Returns: (should_run: bool, reason: str)
        """
        today = datetime.now().date()
        
        # Hafta sonu kontrolü
        if today.weekday() >= 5:
            return False, "Hafta sonu - borsa kapalı"
        
        # Tatil kontrolü
        is_open, closing_time = self.calendar.is_market_open(today)
        
        if not is_open:
            return False, "Resmi tatil - borsa kapalı"
        
        return True, f"Borsa açık - Kapanış: {closing_time}"
    
    def get_optimal_run_time(self, check_date=None):
        """
        Bugün için optimal çalışma zamanını döndür
        Returns: (should_run: bool, run_time: time, reason: str)
        """
        if check_date is None:
            check_date = datetime.now().date()
        
        # Borsa açık mı?
        is_open, closing_time = self.calendar.is_market_open(check_date)
        
        if not is_open:
            return False, None, "Borsa kapalı"
        
        if closing_time and closing_time.hour == 13:
            # Yarım gün mesai - 13:05'te çalış
            return True, time(13, 5), "Yarım gün mesai"
        else:
            # Normal mesai - 18:35'te çalış (18:10 kapanış + 25 dk)
            return True, time(18, 35), "Normal mesai"
    
    def run_if_time(self, task_func, task_name="Görev"):
        """
        Şu an çalışma zamanı mı kontrol et ve gerekirse görevi çalıştır
        """
        should_run, reason = self.should_run_today()
        
        if not should_run:
            print(f"⏸️  {task_name} atlandı: {reason}")
            logging.info(f"{task_name} skipped: {reason}")
            return False
        
        # Zamanı kontrol et
        should_run_now, optimal_time, timing_reason = self.get_optimal_run_time()
        current_time = datetime.now().time()
        
        print(f"ℹ️  Bugün: {reason}")
        print(f"ℹ️  Optimal zaman: {optimal_time} ({timing_reason})")
        print(f"ℹ️  Şu an: {current_time.strftime('%H:%M:%S')}")
        
        # Zaman kontrolü (±10 dakika tolerans)
        if optimal_time:
            time_diff_minutes = abs(
                (current_time.hour * 60 + current_time.minute) -
                (optimal_time.hour * 60 + optimal_time.minute)
            )
            
            if time_diff_minutes <= 30:  # 30 dakika tolerans
                print(f"✅ Çalışma zamanı! {task_name} başlatılıyor...\n")
                logging.info(f"{task_name} started at {current_time}")
                task_func()
                return True
            else:
                print(f"⏰ Henüz zaman değil. {optimal_time} zamanında çalışmalı.")
                logging.info(f"{task_name} scheduled for {optimal_time}, current: {current_time}")
                return False
        
        return False

def run_daily_update():
    """Günlük veri güncelleme görevi"""
    from update_market_data import run_daily_update
    run_daily_update()

def run_daily_scan():
    """Günlük tarama görevi"""
    import scanner_xtumy
    scanner_xtumy.run_scanner()

def main():
    """
    Kullanım:
    1. Manuel test: python3.11 smart_scheduler.py --test
    2. Cron job: python3.11 smart_scheduler.py --update
    3. Scan: python3.11 smart_scheduler.py --scan
    """
    scheduler = SmartScheduler()
    
    if '--test' in sys.argv:
        print("\n🧪 TEST MODU\n")
        should_run, reason = scheduler.should_run_today()
        print(f"Bugün çalışmalı mı? {should_run}")
        print(f"Sebep: {reason}\n")
        
        should_run_now, optimal_time, timing_reason = scheduler.get_optimal_run_time()
        print(f"Optimal çalışma zamanı: {optimal_time}")
        print(f"Sebep: {timing_reason}\n")
        
    elif '--update' in sys.argv:
        print("\n📥 VERİ GÜNCELLEME GÖREVI\n")
        scheduler.run_if_time(run_daily_update, "Veri Güncelleme")
        
    elif '--scan' in sys.argv:
        print("\n🔍 TARAMA GÖREVI\n")
        scheduler.run_if_time(run_daily_scan, "Sinyal Tarama")
        
    else:
        print("Kullanım:")
        print("  python3.11 smart_scheduler.py --test     # Test modu")
        print("  python3.11 smart_scheduler.py --update   # Veri güncelleme")
        print("  python3.11 smart_scheduler.py --scan     # Tarama")

if __name__ == "__main__":
    main()

