import pandas as pd
from tradingview_screener import Query, Column
from sqlalchemy import create_engine, text
from datetime import datetime
from config import DB_CONNECTION_STR, LOG_DIR
import logging

# Log Ayarları
logging.basicConfig(filename=f'{LOG_DIR}/tickers.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def update_ticker_list():
    engine = create_engine(DB_CONNECTION_STR)
    logging.info("Ticker listesi güncelleme işlemi başladı.")
    print("TradingView Screener üzerinden BIST listesi çekiliyor...")
    
    try:
        # 1. TradingView Sorgusu (Sizin belirttiğiniz kriterler)
        # Type: Stock ve Fund | TypeSpecs: ETF OLMAYANLAR
        query = (Query()
            .set_markets('turkey')
            .where(
                Column('type').isin(['stock', 'fund']),
                Column('exchange').isin(['BIST']),
                Column('currency_id') == 'TRY',
                Column('typespecs').has_none_of(['etf']),
            )
            .select('name', 'type', 'description')
            .order_by('name', ascending=True)
            .limit(3000) 
            .get_scanner_data())
        
        # Tuple döner: (count, dataframe)
        df = query[1]
        
        if df.empty:
            logging.warning("Liste boş döndü, işlem iptal edildi.")
            return
        
        # 2. Veri Temizleme
        # Ticker formatı "BIST:THYAO" gelir, "THYAO" yapalım.
        df['ticker'] = df['ticker'].str.replace('BIST:', '', regex=False)
        
        # 3. Veritabanına Kayıt (Upsert Mantığı)
        # Önce mevcut listeyi temizleyebiliriz veya üzerine yazabiliriz.
        # Temiz bir liste için 'replace' stratejisi yerine 'upsert' daha güvenlidir ama 
        # listeden çıkan hisseleri yönetmek için 'TRUNCATE' edip yeniden doldurmak 
        # haftalık güncellemeler için daha temizdir.
        
        with engine.connect() as conn:
            # Eski hisseleri sil ama CASCADE kullanma (market_data'yı silmesin)
            conn.execute(text("DELETE FROM tickers;")) 
            conn.commit()
            
        # DataFrame kolonlarını DB ile eşleştir
        # DB: symbol, name, type
        df_db = df[['ticker', 'name', 'type']].copy()
        df_db.rename(columns={'ticker': 'symbol'}, inplace=True)
        df_db['updated_at'] = datetime.now()
        
        # Veritabanına yaz
        df_db.to_sql('tickers', engine, if_exists='append', index=False)
        
        msg = f"Başarılı. Toplam {len(df_db)} adet enstrüman (Hisse + Fon) veritabanına kaydedildi."
        print(msg)
        logging.info(msg)
        
    except Exception as e:
        logging.error(f"Hata oluştu: {str(e)}")
        print(f"Hata: {e}")

if __name__ == "__main__":
    update_ticker_list()

