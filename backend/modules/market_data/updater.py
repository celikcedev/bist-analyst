import pandas as pd
from sqlalchemy import create_engine, text
from tvDatafeed import TvDatafeed, Interval
from config import DB_CONNECTION_STR, LOG_DIR
import logging
import time

# Log Ayarları
logging.basicConfig(filename=f'{LOG_DIR}/data_update.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def get_last_date(engine, symbol):
    """Veritabanında bir hisse için en son hangi tarihli veri var?"""
    query = text("SELECT MAX(date) FROM market_data WHERE symbol = :sym")
    with engine.connect() as conn:
        result = conn.execute(query, {"sym": symbol}).scalar()
    return result

def get_missing_days_count(engine, symbol):
    """
    Veritabanındaki son tarih ile bugün arasında kaç gün eksik?
    Hafta sonları ve tatil günleri hariç iş günü sayısı
    """
    from datetime import datetime, timedelta
    
    last_date = get_last_date(engine, symbol)
    if last_date is None:
        return None  # Hiç veri yok
    
    # Son tarih ile bugün arasındaki fark
    today = datetime.now().date()
    last_date = last_date.date() if hasattr(last_date, 'date') else last_date
    
    # Eğer son tarih bugünse, eksik gün yok
    if last_date >= today:
        return 0
    
    # Aradaki iş günü sayısını hesapla (basit: hafta sonları hariç)
    days_diff = (today - last_date).days
    
    # Hafta içi günleri say (yaklaşık)
    business_days = 0
    current_date = last_date + timedelta(days=1)
    while current_date <= today:
        # Hafta sonu değilse say (0=Pazartesi, 6=Pazar)
        if current_date.weekday() < 5:  # 0-4 = Pazartesi-Cuma
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

def run_daily_update():
    engine = create_engine(DB_CONNECTION_STR)
    # TradingView credentials kullanarak bağlan
    tv = TvDatafeed(username='mysound74@hotmail.com', password='Acelik5225.')
    
    logging.info("Günlük veri güncelleme rutini başladı.")
    
    # 1. Ticker Listesini Veritabanından Çek
    try:
        tickers_df = pd.read_sql("SELECT symbol FROM tickers", engine)
        ticker_list = tickers_df['symbol'].tolist()
        print(f"Toplam {len(ticker_list)} adet hisse/fon güncellenecek.")
    except Exception as e:
        logging.error(f"Ticker listesi alınamadı: {e}")
        return
    
    # 2. Döngü
    updated_count = 0
    error_count = 0
    skipped_count = 0
    
    for symbol in ticker_list:
        try:
            # Son tarihi kontrol et
            last_date = get_last_date(engine, symbol)
            missing_days = get_missing_days_count(engine, symbol)
            
            # Ne kadar veri çekilecek?
            if last_date is None:
                # İlk defa çekiliyorsa 1 yıllık (veya 250 bar)
                print(f"[{symbol}] İlk veri çekimi...")
                df = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=250)
            elif missing_days and missing_days > 0:
                # Eksik günler var, onları çek
                # Güvenlik payı ekle: eksik gün sayısı + 5 (tatil günleri için)
                bars_to_fetch = min(missing_days + 5, 20)
                print(f"[{symbol}] {missing_days} eksik gün tespit edildi, {bars_to_fetch} bar çekiliyor...")
                df = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=bars_to_fetch)
                if df is not None and not df.empty:
                    df = df[df.index > last_date]
            elif missing_days == 0:
                # Veri güncel, atla
                skipped_count += 1
                continue
            else:
                # missing_days None ise (hiç veri yok), 250 bar çek
                print(f"[{symbol}] Veri yok, ilk çekim...")
                df = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=250)
            
            # Veritabanına Yazma
            if df is not None and not df.empty:
                df = df.reset_index()  # Tarih index'ten kolona
                
                # Kolon isimlerini küçük harfe çevir ve eşleştir
                # tvDatafeed: symbol, datetime, open, high, low, close, volume
                df.columns = [c.lower() for c in df.columns]
                
                # Eğer tvDatafeed 'symbol' kolonu göndermiyorsa manuel ekle
                if 'symbol' not in df.columns:
                    df['symbol'] = symbol
                else:
                    # tvDatafeed "BIST:SYMBOL" formatında döner, sadece "SYMBOL" yapalım
                    df['symbol'] = df['symbol'].str.replace('BIST:', '', regex=False)
                
                # DB şemasına uygun dataframe
                df_to_write = df[['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume']].rename(
                    columns={'datetime': 'date'}
                )
                
                df_to_write.to_sql('market_data', engine, if_exists='append', index=False)
                updated_count += 1
                print(f"[{symbol}] Güncellendi. (+{len(df_to_write)} satır)")
            
            # Rate Limit yememek için kısa bekleme (opsiyonel)
            time.sleep(0.1)
            
        except Exception as e:
            logging.error(f"[{symbol}] Hata: {e}")
            print(f"[{symbol}] Hata: {e}")
            error_count += 1
            continue
    
    msg = f"Güncelleme tamamlandı. {updated_count} hisse güncellendi, {skipped_count} atlandı (güncel), {error_count} hata."
    print(msg)
    logging.info(msg)

if __name__ == "__main__":
    run_daily_update()

