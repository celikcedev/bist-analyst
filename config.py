import os

# Veritabanı Bilgileri
DB_USER = "postgres"       # Kendi kullanıcı adınız
DB_PASS = "Acelik5225."    # Kendi şifreniz
DB_HOST = "localhost"
DB_NAME = "trading_db"     # Veritabanı adı

# SQLAlchemy Bağlantı Stringi
DB_CONNECTION_STR = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

# Log Klasörü
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

