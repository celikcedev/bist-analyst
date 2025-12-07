"""
BIST Analyst - Sistem Sağlık Kontrolü
Her gün sistem durumunu kontrol eder ve Telegram'a rapor gönderir
"""
from sqlalchemy import create_engine, text
from config import DB_CONNECTION_STR, LOG_DIR
from datetime import datetime, timedelta
from telegram_bot import TelegramBot
import logging
import os

logging.basicConfig(filename=f'{LOG_DIR}/health_check.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

class SystemHealthCheck:
    """Sistem sağlık kontrolü"""
    
    def __init__(self):
        self.engine = create_engine(DB_CONNECTION_STR)
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def check_database_connection(self):
        """Veritabanı bağlantısı kontrolü"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.successes.append("Veritabanı: Bağlantı OK")
            return True
        except Exception as e:
            self.issues.append(f"Veritabanı: Bağlantı hatası - {e}")
            return False
    
    def check_last_data_update(self):
        """Son veri güncellemesi kontrolü"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT MAX(date) as last_date, COUNT(DISTINCT symbol) as symbol_count
                    FROM market_data
                """))
                row = result.fetchone()
                
                if row and row[0]:
                    last_date = row[0]
                    symbol_count = row[1]
                    today = datetime.now().date()
                    
                    # last_date datetime.date veya datetime.datetime olabilir
                    if isinstance(last_date, datetime):
                        last_date = last_date.date()
                    
                    days_ago = (today - last_date).days
                    
                    if days_ago == 0:
                        self.successes.append(f"Son veri güncelleme: Bugün ({symbol_count} hisse)")
                    elif days_ago == 1:
                        self.successes.append(f"Son veri güncelleme: Dün ({symbol_count} hisse)")
                    elif days_ago <= 3:
                        self.warnings.append(f"Son veri güncelleme: {days_ago} gün önce ({symbol_count} hisse)")
                    else:
                        self.issues.append(f"Son veri güncelleme: {days_ago} gün önce! Güncelleme yapılmalı.")
                    
                    return last_date, symbol_count
                else:
                    self.issues.append("Veritabanında hiç veri yok!")
                    return None, 0
        except Exception as e:
            self.issues.append(f"Veri güncelleme kontrolü hatası: {e}")
            return None, 0
    
    def check_ticker_count(self):
        """Ticker sayısı kontrolü"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM tickers"))
                ticker_count = result.fetchone()[0]
                
                if ticker_count >= 580:
                    self.successes.append(f"Ticker listesi: {ticker_count} hisse")
                elif ticker_count >= 500:
                    self.warnings.append(f"Ticker listesi: {ticker_count} hisse (normalden az)")
                else:
                    self.issues.append(f"Ticker listesi: Sadece {ticker_count} hisse! Güncelleme gerekli.")
                
                return ticker_count
        except Exception as e:
            self.issues.append(f"Ticker kontrolü hatası: {e}")
            return 0
    
    def check_missing_data(self, last_date):
        """Eksik verisi olan hisseler"""
        try:
            with self.engine.connect() as conn:
                # Son günde verisi olmayan hisseler
                result = conn.execute(text("""
                    SELECT t.symbol 
                    FROM tickers t
                    LEFT JOIN market_data m ON t.symbol = m.symbol AND m.date = :last_date
                    WHERE m.symbol IS NULL
                    ORDER BY t.symbol
                """), {"last_date": last_date})
                
                missing_symbols = [row[0] for row in result.fetchall()]
                
                if len(missing_symbols) == 0:
                    self.successes.append("Eksik veri: Yok, tüm hisseler güncel")
                elif len(missing_symbols) <= 10:
                    symbols_preview = ', '.join(missing_symbols[:5])
                    if len(missing_symbols) > 5:
                        symbols_preview += "..."
                    self.warnings.append(f"Eksik veri: {len(missing_symbols)} hisse ({symbols_preview})")
                elif len(missing_symbols) <= 50:
                    self.warnings.append(f"Eksik veri: {len(missing_symbols)} hisse eksik")
                else:
                    # 50'den fazla eksikse, muhtemelen son günde henüz veri çekilmemiş
                    self.warnings.append(f"Eksik veri: {len(missing_symbols)} hisse (henüz güncellenmemiş olabilir)")
                
                return missing_symbols
        except Exception as e:
            self.warnings.append(f"Eksik veri kontrolü hatası: {e}")
            return []
    
    def check_telegram_connection(self):
        """Telegram bağlantısı kontrolü"""
        bot = TelegramBot()
        if bot.enabled and bot.bot_token and bot.chat_ids:
            self.successes.append(f"Telegram: Aktif ({len(bot.chat_ids)} alıcı)")
            return True
        elif not bot.enabled:
            self.warnings.append("Telegram: Devre dışı (.env'de kapalı)")
            return False
        else:
            self.issues.append("Telegram: Credentials eksik!")
            return False
    
    def check_log_files(self):
        """Log dosyalarını kontrol et"""
        log_files = ['cron_data.log', 'cron_scanner.log', 'telegram.log']
        log_status = []
        
        for log_file in log_files:
            log_path = os.path.join(LOG_DIR, log_file)
            if os.path.exists(log_path):
                # Son 24 saatte değişti mi?
                mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
                age_hours = (datetime.now() - mtime).total_seconds() / 3600
                
                if age_hours < 24:
                    log_status.append(f"{log_file} ✓")
                else:
                    log_status.append(f"{log_file} ({int(age_hours)}h önce)")
        
        if log_status:
            self.successes.append(f"Log dosyaları: {', '.join(log_status)}")
    
    def check_holidays(self):
        """Tatil takvimi kontrolü"""
        try:
            with self.engine.connect() as conn:
                current_year = datetime.now().year
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM bist_holidays 
                    WHERE year = :year
                """), {"year": current_year})
                
                holiday_count = result.fetchone()[0]
                
                if holiday_count > 0:
                    self.successes.append(f"Tatil takvimi: {current_year} yılı yüklü ({holiday_count} gün)")
                else:
                    self.warnings.append(f"Tatil takvimi: {current_year} yılı eksik!")
                
                return holiday_count
        except Exception as e:
            self.warnings.append(f"Tatil kontrolü hatası: {e}")
            return 0
    
    def generate_report(self):
        """Rapor oluştur"""
        today = datetime.now().strftime('%d %B %Y, %H:%M')
        
        report = "🏥 <b>Sistem Sağlık Raporu</b>\n"
        report += f"📅 {today}\n"
        report += "─" * 30 + "\n\n"
        
        # Başarılı kontroller
        if self.successes:
            report += "✅ <b>Başarılı</b>\n"
            for success in self.successes:
                report += f"  • {success}\n"
            report += "\n"
        
        # Uyarılar
        if self.warnings:
            report += "⚠️ <b>Uyarılar</b>\n"
            for warning in self.warnings:
                report += f"  • {warning}\n"
            report += "\n"
        
        # Sorunlar
        if self.issues:
            report += "❌ <b>SORUNLAR</b>\n"
            for issue in self.issues:
                report += f"  • {issue}\n"
            report += "\n"
        
        # Genel durum
        report += "─" * 30 + "\n"
        if len(self.issues) == 0 and len(self.warnings) == 0:
            report += "💚 <b>Sistem sağlıklı, sorun yok!</b>"
        elif len(self.issues) == 0:
            report += "💛 <b>Sistem çalışıyor, küçük uyarılar var</b>"
        else:
            report += "🔴 <b>DİKKAT: Sistem sorunları mevcut!</b>"
        
        return report
    
    def run(self):
        """Tüm kontrolleri çalıştır"""
        print("="*70)
        print("BIST ANALYST - SİSTEM SAĞLIK KONTROLÜ")
        print("="*70)
        
        # 1. Veritabanı
        print("\n1. Veritabanı bağlantısı kontrol ediliyor...")
        self.check_database_connection()
        
        # 2. Son veri güncelleme
        print("2. Son veri güncelleme kontrol ediliyor...")
        last_date, symbol_count = self.check_last_data_update()
        
        # 3. Ticker sayısı
        print("3. Ticker listesi kontrol ediliyor...")
        self.check_ticker_count()
        
        # 4. Eksik veri
        if last_date:
            print("4. Eksik veriler kontrol ediliyor...")
            self.check_missing_data(last_date)
        
        # 5. Telegram
        print("5. Telegram bağlantısı kontrol ediliyor...")
        self.check_telegram_connection()
        
        # 6. Log dosyaları
        print("6. Log dosyaları kontrol ediliyor...")
        self.check_log_files()
        
        # 7. Tatil takvimi
        print("7. Tatil takvimi kontrol ediliyor...")
        self.check_holidays()
        
        # Rapor oluştur
        print("\n" + "="*70)
        print("RAPOR OLUŞTURULUYOR...")
        print("="*70)
        
        report = self.generate_report()
        
        # Konsola yazdır (HTML tagları olmadan)
        print("\n" + report.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '').replace('<a href=', '').replace('>', '').replace('</a', ''))
        
        # Telegram'a gönder
        bot = TelegramBot()
        if bot.enabled:
            print("\n📱 Telegram'a gönderiliyor...")
            bot.send_message(report)
        else:
            print("\nℹ️  Telegram devre dışı, rapor sadece konsola yazıldı.")
        
        # Log'a kaydet
        logging.info("Health check completed")
        if self.issues:
            logging.warning(f"Issues found: {len(self.issues)}")
        
        return len(self.issues) == 0

def main():
    health = SystemHealthCheck()
    success = health.run()
    
    if not success:
        exit(1)  # Sorun varsa exit code 1
    else:
        exit(0)  # Her şey OK

if __name__ == "__main__":
    main()

