import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'flower-secret-key-2026-petal-blossom')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'flower_shop_db')
    
    # SQLite fallback file (for instant out-of-the-box local execution if MySQL service is inactive)
    SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flower_shop.db')
    
    # Business logic defaults
    STANDARD_DELIVERY_CHARGE = 50.00
    FREE_DELIVERY_THRESHOLD = 2000.00
    DEFAULT_DISCOUNT = 100.00
    LOW_STOCK_THRESHOLD = 5
