"""
Telegram Bot Integration for BIST Analyst
Tarama sonuçlarını Telegram'a gönderir
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import logging
from config import LOG_DIR

logging.basicConfig(filename=f'{LOG_DIR}/telegram.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# .env dosyasını yükle
load_dotenv()

class TelegramBot:
    """Telegram Bot için wrapper class"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        chat_ids_str = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Multiple chat IDs desteği (virgülle ayrılmış)
        self.chat_ids = [cid.strip() for cid in chat_ids_str.split(',') if cid.strip()]
        
        self.enabled = os.getenv('ENABLE_TELEGRAM', 'false').lower() == 'true'
        
        if not self.bot_token or not self.chat_ids:
            logging.warning("Telegram credentials eksik. .env dosyasını kontrol edin.")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
    
    def send_message(self, text, parse_mode='HTML'):
        """Telegram'a mesaj gönder (multiple chat IDs)"""
        if not self.enabled:
            print("ℹ️  Telegram bildirimleri kapalı (.env'de ENABLE_TELEGRAM=true yapın)")
            return False
        
        if not self.bot_token or not self.chat_ids:
            print("❌ Telegram credentials eksik!")
            return False
        
        success_count = 0
        fail_count = 0
        
        for chat_id in self.chat_ids:
            try:
                payload = {
                    'chat_id': chat_id,
                    'text': text,
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': False
                }
                
                response = requests.post(self.api_url, json=payload, timeout=10)
                response.raise_for_status()
                
                success_count += 1
                logging.info(f"Telegram message sent to {chat_id}")
                
            except Exception as e:
                fail_count += 1
                print(f"❌ Telegram gönderim hatası (chat_id: {chat_id}): {e}")
                logging.error(f"Telegram send error (chat_id: {chat_id}): {e}")
        
        if success_count > 0:
            print(f"✅ Telegram mesajı {success_count} kişiye gönderildi!")
            if fail_count > 0:
                print(f"⚠️  {fail_count} kişiye gönderilemedi.")
            return True
        else:
            print(f"❌ Hiçbir kişiye gönderilemedi!")
            return False
    
    def format_scan_results(self, signals_df):
        """Tarama sonuçlarını Telegram formatında hazırla"""
        if signals_df is None or len(signals_df) == 0:
            return self._format_no_signals()
        
        # Başlık
        today = datetime.now().strftime('%d %B %Y')
        message = f"🚀 <b>XTUMY V27 Tarama Sonuçları</b>\n"
        message += f"📅 {today}\n"
        message += f"📊 Toplam {len(signals_df)} Sinyal\n"
        message += "─" * 30 + "\n\n"
        
        # Sinyal türlerine göre grupla
        signal_types = signals_df['Signal'].unique()
        
        # Emoji mapping
        emoji_map = {
            'KURUMSAL DİP': '🏦',
            'TREND BAŞLANGIÇ': '🚀',
            'PULLBACK AL': '↩️',
            'DİP AL': '📉',
            'ALTIN KIRILIM': '🥇',
            'ZİRVE KIRILIMI': '⛰️'
        }
        
        for signal_type in signal_types:
            signal_df = signals_df[signals_df['Signal'] == signal_type]
            emoji = emoji_map.get(signal_type, '📊')
            
            message += f"\n{emoji} <b>{signal_type}</b> ({len(signal_df)} adet)\n"
            message += "─" * 30 + "\n"
            
            for _, row in signal_df.iterrows():
                symbol = row['Symbol']
                price = row['Close']
                rsi = row['RSI']
                adx = row['ADX']
                
                # TradingView chart linki
                tv_link = f"https://www.tradingview.com/chart/?symbol=BIST%3A{symbol}"
                
                message += f"• <b>{symbol}</b> - {price:.2f} TL\n"
                message += f"  RSI: {rsi:.1f} | ADX: {adx:.1f}\n"
                message += f"  <a href='{tv_link}'>📈 Grafiği Aç</a>\n\n"
        
        message += "─" * 30 + "\n"
        message += "💡 <i>BIST Analyst - Autonomous System</i>"
        
        return message
    
    def _format_no_signals(self):
        """Sinyal bulunamadığında mesaj"""
        today = datetime.now().strftime('%d %B %Y')
        message = f"🚀 <b>XTUMY V27 Tarama Sonuçları</b>\n"
        message += f"📅 {today}\n\n"
        message += "❌ Bugün sinyal kriterlerine uyan hisse bulunamadı.\n\n"
        message += "💡 <i>BIST Analyst - Autonomous System</i>"
        return message
    
    def send_scan_results(self, signals_df):
        """Tarama sonuçlarını formatla ve gönder"""
        message = self.format_scan_results(signals_df)
        return self.send_message(message)

def main():
    """Test için"""
    import pandas as pd
    
    # Test mesajı
    bot = TelegramBot()
    
    # Örnek veri
    test_data = {
        'Symbol': ['THYAO', 'GARAN'],
        'Close': [270.25, 141.5],
        'Signal': ['KURUMSAL DİP', 'TREND BAŞLANGIÇ'],
        'RSI': [48.5, 55.2],
        'ADX': [17.3, 21.8]
    }
    
    df = pd.DataFrame(test_data)
    bot.send_scan_results(df)

if __name__ == "__main__":
    main()

