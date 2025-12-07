import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'trading_db')

# SQLAlchemy Connection String
DB_CONNECTION_STR = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

# Log Directory
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# TradingView Configuration
TV_USERNAME = os.getenv('TV_USERNAME', '')
TV_PASSWORD = os.getenv('TV_PASSWORD', '')

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
ENABLE_TELEGRAM = os.getenv('ENABLE_TELEGRAM', 'false').lower() == 'true'

# Scanner Configuration
ENABLE_AUTO_SCAN = os.getenv('ENABLE_AUTO_SCAN', 'true').lower() == 'true'
SCAN_AFTER_UPDATE = os.getenv('SCAN_AFTER_UPDATE', 'true').lower() == 'true'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

