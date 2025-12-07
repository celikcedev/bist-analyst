from sqlalchemy import create_engine, text
from config import DB_CONNECTION_STR

def init_db():
    engine = create_engine(DB_CONNECTION_STR)
    
    # 1. Tickers Tablosu (Hisse Listesi)
    # update_at: Listenin en son ne zaman güncellendiği
    sql_tickers = """
    CREATE TABLE IF NOT EXISTS public.tickers (
        symbol VARCHAR(20) PRIMARY KEY,
        name VARCHAR(255),
        type VARCHAR(50),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 2. Market Data Tablosu (Fiyat Verileri)
    # (symbol, date) çifti benzersizdir (Composite Primary Key)
    sql_data = """
    CREATE TABLE IF NOT EXISTS public.market_data (
        symbol VARCHAR(20) NOT NULL,
        date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        volume BIGINT,
        CONSTRAINT market_data_pkey PRIMARY KEY (symbol, date),
        CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES public.tickers(symbol)
    );
    
    CREATE INDEX IF NOT EXISTS idx_data_symbol ON public.market_data (symbol);
    CREATE INDEX IF NOT EXISTS idx_data_date ON public.market_data (date);
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql_tickers))
        conn.execute(text(sql_data))
        conn.commit()
        print("Veritabanı tabloları başarıyla oluşturuldu/kontrol edildi.")

if __name__ == "__main__":
    init_db()

