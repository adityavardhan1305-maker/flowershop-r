import os
import sqlite3
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# Global database type flag
ACTIVE_DB_TYPE = 'sqlite'  # 'mysql' or 'sqlite'
_mysql_checked = False
_mysql_available = False

def try_connect_mysql():
    """Attempt connecting to MySQL server."""
    global _mysql_checked, _mysql_available
    if _mysql_checked and not _mysql_available:
        return None
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=1
        )
        _mysql_checked = True
        _mysql_available = True
        return conn
    except Exception as e:
        _mysql_checked = True
        _mysql_available = False
        return None

def get_db():
    """Get connection to the active database (MySQL if available, else SQLite)."""
    global ACTIVE_DB_TYPE
    # First try MySQL
    mysql_conn = try_connect_mysql()
    if mysql_conn:
        try:
            with mysql_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
                cur.execute(f"USE {Config.MYSQL_DB}")
            ACTIVE_DB_TYPE = 'mysql'
            return mysql_conn
        except Exception:
            mysql_conn.close()

    # Fallback to SQLite
    ACTIVE_DB_TYPE = 'sqlite'
    conn = sqlite3.connect(Config.SQLITE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def adapt_sql(query):
    """Adapt MySQL query with %s placeholders to SQLite ? placeholders if on SQLite."""
    if ACTIVE_DB_TYPE == 'sqlite':
        return query.replace('%s', '?')
    return query

def query_db(query, args=(), one=False):
    """Run a SELECT query and return dictionary-like records."""
    conn = get_db()
    sql = adapt_sql(query)
    try:
        if ACTIVE_DB_TYPE == 'mysql':
            with conn.cursor() as cur:
                cur.execute(sql, args)
                rv = cur.fetchall()
            conn.close()
            return (rv[0] if rv else None) if one else rv
        else:
            cur = conn.cursor()
            cur.execute(sql, args)
            rv = [dict(row) for row in cur.fetchall()]
            conn.close()
            return (rv[0] if rv else None) if one else rv
    except Exception as e:
        conn.close()
        raise e

def execute_db(query, args=()):
    """Run an INSERT, UPDATE, or DELETE query and commit."""
    conn = get_db()
    sql = adapt_sql(query)
    try:
        if ACTIVE_DB_TYPE == 'mysql':
            with conn.cursor() as cur:
                cur.execute(sql, args)
                rowcount = cur.rowcount
            conn.commit()
            conn.close()
            return rowcount
        else:
            cur = conn.cursor()
            cur.execute(sql, args)
            conn.commit()
            rowcount = cur.rowcount
            conn.close()
            return rowcount
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def execute_insert(query, args=()):
    """Run an INSERT query, commit, and return lastrowid."""
    conn = get_db()
    sql = adapt_sql(query)
    try:
        if ACTIVE_DB_TYPE == 'mysql':
            with conn.cursor() as cur:
                cur.execute(sql, args)
                last_id = cur.lastrowid
            conn.commit()
            conn.close()
            return last_id
        else:
            cur = conn.cursor()
            cur.execute(sql, args)
            conn.commit()
            last_id = cur.lastrowid
            conn.close()
            return last_id
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def init_db(force_reseed=False):
    """Initialize database tables and initial seed data if needed."""
    global ACTIVE_DB_TYPE
    conn = get_db()
    
    if ACTIVE_DB_TYPE == 'mysql':
        print("[Database] Initializing MySQL database...")
        # Check if CUSTOMERS table exists
        with conn.cursor() as cur:
            cur.execute(f"USE {Config.MYSQL_DB}")
            cur.execute("SHOW TABLES LIKE 'CUSTOMERS'")
            exists = cur.fetchone()
            if not exists or force_reseed:
                sql_path = os.path.join(os.path.dirname(__file__), 'flower_shop_db.sql')
                if os.path.exists(sql_path):
                    with open(sql_path, 'r', encoding='utf-8') as f:
                        sql_commands = f.read().split(';')
                        for cmd in sql_commands:
                            cmd_clean = cmd.strip()
                            if cmd_clean and not cmd_clean.startswith('--'):
                                cur.execute(cmd_clean)
                    conn.commit()
                    print("[Database] MySQL initialized and seeded from flower_shop_db.sql.")
        conn.close()
    else:
        # SQLite Initialization
        print("[Database] Initializing SQLite database...")
        cur = conn.cursor()
        
        # Check if CUSTOMERS table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CUSTOMERS'")
        exists = cur.fetchone()
        
        if not exists or force_reseed:
            if force_reseed:
                for tbl in ['DELIVERIES', 'PAYMENTS', 'ORDER_ITEMS', 'ORDERS', 'FLOWERS', 'SUPPLIERS', 'CATEGORIES', 'STAFF', 'CUSTOMERS']:
                    cur.execute(f"DROP TABLE IF EXISTS {tbl}")
            
            # 1. Customers Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS CUSTOMERS (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                phone TEXT,
                address TEXT
            )
            ''')

            # 2. Staff Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS STAFF (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT CHECK(role IN ('Admin', 'Staff', 'Delivery')) NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            ''')

            # 3. Categories Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS CATEGORIES (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL,
                description TEXT
            )
            ''')

            # 4. Suppliers Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS SUPPLIERS (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                address TEXT
            )
            ''')

            # 5. Flowers Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS FLOWERS (
                flower_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                supplier_id INTEGER,
                name TEXT NOT NULL,
                color TEXT,
                price REAL NOT NULL,
                stock_qty INTEGER NOT NULL DEFAULT 0,
                image_url TEXT,
                FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE SET NULL,
                FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id) ON DELETE SET NULL
            )
            ''')

            # 6. Orders Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS ORDERS (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                supplier_id INTEGER,
                order_date TEXT DEFAULT (datetime('now', 'localtime')),
                delivery_date TEXT,
                status TEXT CHECK(status IN ('Order Placed', 'Payment Confirmed', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled')) DEFAULT 'Order Placed',
                total_amount REAL NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id) ON DELETE SET NULL
            )
            ''')

            # 7. Order Items Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                flower_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
                FOREIGN KEY (flower_id) REFERENCES FLOWERS(flower_id) ON DELETE CASCADE
            )
            ''')

            # 8. Payments Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS PAYMENTS (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER UNIQUE,
                method TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT CHECK(status IN ('Pending', 'Paid', 'Failed', 'Refunded')) DEFAULT 'Pending',
                paid_on TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE
            )
            ''')

            # 9. Deliveries Table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS DELIVERIES (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER UNIQUE,
                staff_id INTEGER,
                address TEXT NOT NULL,
                status TEXT CHECK(status IN ('Assigned', 'Out for Delivery', 'Delivered')) DEFAULT 'Assigned',
                delivered_on TEXT NULL,
                FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
                FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE SET NULL
            )
            ''')

            conn.commit()
            seed_initial_data(conn)
            print("[Database] SQLite initialized and seeded successfully.")
            
        conn.close()

def seed_initial_data(conn):
    """Seed comprehensive initial data into database."""
    cur = conn.cursor()
    
    # Common password hash for 'password123'
    default_pwd_hash = generate_password_hash('password123')

    # Seed Categories
    categories = [
        (1, 'Bouquets', 'Handcrafted arrangements of fresh blossoms tied with luxury satin ribbons.'),
        (2, 'Roses', 'Classic long-stem and premium garden roses in vibrant romantic hues.'),
        (3, 'Orchids', 'Exotic tropical orchid stems symbolizing elegance, luxury, and strength.'),
        (4, 'Event Arrangements', 'Lavish centerpieces, ceremonial bouquets, and festive stage decor.'),
        (5, 'Lilies & Carnations', 'Fragrant Asiatic lilies and soft pastel carnations for thoughtful expressions.')
    ]
    cur.executemany("INSERT OR IGNORE INTO CATEGORIES (category_id, category_name, description) VALUES (?, ?, ?)", categories)

    # Seed Suppliers
    suppliers = [
        (1, 'Blossom Farms Co.', '+91 98111 22334', 'Valley Flower Estates, Ooty, Tamil Nadu - 643001'),
        (2, 'Greenhouse Flora Ltd.', '+91 98222 33445', 'Talegaon Floral Park, Pune, Maharashtra - 410507'),
        (3, 'Exotic Petals Importers', '+91 98333 44556', 'International Flower Auction Center, Bengaluru, Karnataka - 560052'),
        (4, 'Himalayan Blooms', '+91 98444 55667', 'Nursery Ridge Road, Dehradun, Uttarakhand - 248001')
    ]
    cur.executemany("INSERT OR IGNORE INTO SUPPLIERS (supplier_id, name, contact, address) VALUES (?, ?, ?, ?)", suppliers)

    # Seed Staff
    staff_members = [
        (1, 'Vikram Administrator', 'Admin', 'admin@flowershop.com', default_pwd_hash),
        (2, 'Priya Florist', 'Staff', 'florist@flowershop.com', default_pwd_hash),
        (3, 'Rahul Delivery', 'Delivery', 'delivery@flowershop.com', default_pwd_hash)
    ]
    cur.executemany("INSERT OR IGNORE INTO STAFF (staff_id, name, role, email, password) VALUES (?, ?, ?, ?, ?)", staff_members)

    # Seed Customers
    customers = [
        (1, 'Ananya Sharma', 'customer@flowershop.com', default_pwd_hash, '+91 98765 43210', '42 Blossom Hill, Green Park, New Delhi - 110016'),
        (2, 'Rohan Mehta', 'rohan@example.com', default_pwd_hash, '+91 91234 56789', '15 Coral Heights, Bandra West, Mumbai - 400050')
    ]
    cur.executemany("INSERT OR IGNORE INTO CUSTOMERS (customer_id, name, email, password, phone, address) VALUES (?, ?, ?, ?, ?, ?)", customers)

    # Seed Flowers
    flowers = [
        (1, 2, 1, 'Velvet Red Roses Bouquet', 'Red', 450.00, 25, '/static/images/flowers/red_roses.svg'),
        (2, 3, 3, 'Royal Purple Orchid Bouquet', 'Purple', 600.00, 15, '/static/images/flowers/purple_orchids.svg'),
        (3, 2, 1, 'Sunrise Yellow Dutch Roses', 'Yellow', 420.00, 18, '/static/images/flowers/yellow_roses.svg'),
        (4, 5, 2, 'Pastel Pink Carnation Bunch', 'Pink', 380.00, 30, '/static/images/flowers/pink_carnations.svg'),
        (5, 5, 4, 'Pure White Asiatic Lilies', 'White', 550.00, 12, '/static/images/flowers/white_lilies.svg'),
        (6, 4, 2, 'Grand Wedding Centerpiece', 'Mixed', 1850.00, 8, '/static/images/flowers/wedding_centerpiece.svg'),
        (7, 3, 3, 'Luxury Golden Orchids Vase', 'Yellow', 890.00, 6, '/static/images/flowers/golden_orchids.svg'),
        (8, 1, 1, 'Blush Romance Mixed Bouquet', 'Pink', 750.00, 20, '/static/images/flowers/blush_bouquet.svg'),
        (9, 1, 4, 'Spring Meadow Wildflower Bunch', 'Mixed', 490.00, 4, '/static/images/flowers/spring_wildflowers.svg'),
        (10, 4, 3, 'Crimson & Gold Celebration Hamper', 'Red', 1450.00, 3, '/static/images/flowers/celebration_hamper.svg'),
        (11, 2, 1, 'Scarlet Rose Heart Box', 'Red', 990.00, 0, '/static/images/flowers/heart_roses.svg'),
        (12, 3, 3, 'Peaceful White Orchid Pot', 'White', 720.00, 10, '/static/images/flowers/white_orchids.svg')
    ]
    cur.executemany("INSERT OR IGNORE INTO FLOWERS (flower_id, category_id, supplier_id, name, color, price, stock_qty, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", flowers)

    # Seed Orders (Order 1001 matching specification from PDF Page 14)
    orders = [
        (1001, 1, 1, '2026-11-21 10:30:00', '2026-11-22', 'Out for Delivery', 1450.00),
        (1002, 1, 2, '2026-11-22 08:15:00', '2026-11-22', 'Preparing', 430.00),
        (1003, 2, 4, '2026-11-22 09:00:00', '2026-11-23', 'Order Placed', 600.00)
    ]
    cur.executemany("INSERT OR IGNORE INTO ORDERS (order_id, customer_id, supplier_id, order_date, delivery_date, status, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)", orders)

    # Seed Order Items
    order_items = [
        (1, 1001, 1, 2, 450.00),
        (2, 1001, 2, 1, 600.00),
        (3, 1002, 4, 1, 380.00),
        (4, 1003, 5, 1, 550.00)
    ]
    cur.executemany("INSERT OR IGNORE INTO ORDER_ITEMS (item_id, order_id, flower_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)", order_items)

    # Seed Payments
    payments = [
        (1, 1001, 'UPI (Razorpay Mock)', 1450.00, 'Paid', '2026-11-21 10:32:00'),
        (2, 1002, 'Card (PayPal Mock)', 430.00, 'Paid', '2026-11-22 08:16:30'),
        (3, 1003, 'Cash on Delivery', 600.00, 'Pending', '2026-11-22 09:00:00')
    ]
    cur.executemany("INSERT OR IGNORE INTO PAYMENTS (payment_id, order_id, method, amount, status, paid_on) VALUES (?, ?, ?, ?, ?, ?)", payments)

    # Seed Deliveries
    deliveries = [
        (1, 1001, 3, '42 Blossom Hill, Green Park, New Delhi - 110016', 'Out for Delivery', None),
        (2, 1002, 3, '42 Blossom Hill, Green Park, New Delhi - 110016', 'Assigned', None),
        (3, 1003, None, '15 Coral Heights, Bandra West, Mumbai - 400050', 'Assigned', None)
    ]
    cur.executemany("INSERT OR IGNORE INTO DELIVERIES (delivery_id, order_id, staff_id, address, status, delivered_on) VALUES (?, ?, ?, ?, ?, ?)", deliveries)

    conn.commit()
