-- ====================================================================
-- Flower Shop Management System - MySQL Database Schema & Seed Data
-- ====================================================================

CREATE DATABASE IF NOT EXISTS flower_shop_db;
USE flower_shop_db;

-- Drop tables in reverse order of foreign key dependencies if re-running
DROP TABLE IF EXISTS DELIVERIES;
DROP TABLE IF EXISTS PAYMENTS;
DROP TABLE IF EXISTS ORDER_ITEMS;
DROP TABLE IF EXISTS ORDERS;
DROP TABLE IF EXISTS FLOWERS;
DROP TABLE IF EXISTS SUPPLIERS;
DROP TABLE IF EXISTS CATEGORIES;
DROP TABLE IF EXISTS STAFF;
DROP TABLE IF EXISTS CUSTOMERS;

-- 1. Customers Table
CREATE TABLE CUSTOMERS (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT
);

-- 2. Staff Table (Includes Admin, Florist/Staff, and Delivery Person)
CREATE TABLE STAFF (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Staff', 'Delivery') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- 3. Categories Table
CREATE TABLE CATEGORIES (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 4. Suppliers Table
CREATE TABLE SUPPLIERS (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50),
    address TEXT
);

-- 5. Flowers Table
CREATE TABLE FLOWERS (
    flower_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    supplier_id INT,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    stock_qty INT NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id) ON DELETE SET NULL
);

-- 6. Orders Table
CREATE TABLE ORDERS (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    supplier_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_date DATE,
    status ENUM('Order Placed', 'Payment Confirmed', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled') DEFAULT 'Order Placed',
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id) ON DELETE SET NULL
);

-- 7. Order Items Table
CREATE TABLE ORDER_ITEMS (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    flower_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    FOREIGN KEY (flower_id) REFERENCES FLOWERS(flower_id) ON DELETE CASCADE
);

-- 8. Payments Table
CREATE TABLE PAYMENTS (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNIQUE,
    method VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('Pending', 'Paid', 'Failed', 'Refunded') DEFAULT 'Pending',
    paid_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE
);

-- 9. Deliveries Table
CREATE TABLE DELIVERIES (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNIQUE,
    staff_id INT,
    address TEXT NOT NULL,
    status ENUM('Assigned', 'Out for Delivery', 'Delivered') DEFAULT 'Assigned',
    delivered_on DATETIME NULL,
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE SET NULL
);

-- ====================================================================
-- SEED DATA
-- ====================================================================

-- Seed Categories
INSERT INTO CATEGORIES (category_id, category_name, description) VALUES
(1, 'Bouquets', 'Handcrafted arrangements of fresh blossoms tied with luxury satin ribbons.'),
(2, 'Roses', 'Classic long-stem and premium garden roses in vibrant romantic hues.'),
(3, 'Orchids', 'Exotic tropical orchid stems symbolizing elegance, luxury, and strength.'),
(4, 'Event Arrangements', 'Lavish centerpieces, ceremonial bouquets, and festive stage decor.'),
(5, 'Lilies & Carnations', 'Fragrant Asiatic lilies and soft pastel carnations for thoughtful expressions.');

-- Seed Suppliers
INSERT INTO SUPPLIERS (supplier_id, name, contact, address) VALUES
(1, 'Blossom Farms Co.', '+91 98111 22334', 'Valley Flower Estates, Ooty, Tamil Nadu - 643001'),
(2, 'Greenhouse Flora Ltd.', '+91 98222 33445', 'Talegaon Floral Park, Pune, Maharashtra - 410507'),
(3, 'Exotic Petals Importers', '+91 98333 44556', 'International Flower Auction Center, Bengaluru, Karnataka - 560052'),
(4, 'Himalayan Blooms', '+91 98444 55667', 'Nursery Ridge Road, Dehradun, Uttarakhand - 248001');

-- Seed Staff Accounts (Pass: pbkdf2:sha256 or password123 supported by app)
-- Passwords below are pre-computed pbkdf2:sha256 hashes for 'password123'
INSERT INTO STAFF (staff_id, name, role, email, password) VALUES
(1, 'Vikram Administrator', 'Admin', 'admin@flowershop.com', 'scrypt:32768:8:1$E6g7y640qO2fD0l6$379527ec683b54ea511c91ce6b4c1fc74b97d26ea334d744b79b90c1fcead15d9da63914a1e9447e1fa122a28185c79e6f66299b9cfd41a7d189bb5322fdc66b'),
(2, 'Priya Florist', 'Staff', 'florist@flowershop.com', 'scrypt:32768:8:1$E6g7y640qO2fD0l6$379527ec683b54ea511c91ce6b4c1fc74b97d26ea334d744b79b90c1fcead15d9da63914a1e9447e1fa122a28185c79e6f66299b9cfd41a7d189bb5322fdc66b'),
(3, 'Rahul Delivery', 'Delivery', 'delivery@flowershop.com', 'scrypt:32768:8:1$E6g7y640qO2fD0l6$379527ec683b54ea511c91ce6b4c1fc74b97d26ea334d744b79b90c1fcead15d9da63914a1e9447e1fa122a28185c79e6f66299b9cfd41a7d189bb5322fdc66b');

-- Seed Customers
INSERT INTO CUSTOMERS (customer_id, name, email, password, phone, address) VALUES
(1, 'Ananya Sharma', 'customer@flowershop.com', 'scrypt:32768:8:1$E6g7y640qO2fD0l6$379527ec683b54ea511c91ce6b4c1fc74b97d26ea334d744b79b90c1fcead15d9da63914a1e9447e1fa122a28185c79e6f66299b9cfd41a7d189bb5322fdc66b', '+91 98765 43210', '42 Blossom Hill, Green Park, New Delhi - 110016'),
(2, 'Rohan Mehta', 'rohan@example.com', 'scrypt:32768:8:1$E6g7y640qO2fD0l6$379527ec683b54ea511c91ce6b4c1fc74b97d26ea334d744b79b90c1fcead15d9da63914a1e9447e1fa122a28185c79e6f66299b9cfd41a7d189bb5322fdc66b', '+91 91234 56789', '15 Coral Heights, Bandra West, Mumbai - 400050');

-- Seed Flowers
INSERT INTO FLOWERS (flower_id, category_id, supplier_id, name, color, price, stock_qty, image_url) VALUES
(1, 2, 1, 'Velvet Red Roses Bouquet', 'Red', 450.00, 25, '/static/images/flowers/red_roses.jpg'),
(2, 3, 3, 'Royal Purple Orchid Bouquet', 'Purple', 600.00, 15, '/static/images/flowers/purple_orchids.jpg'),
(3, 2, 1, 'Sunrise Yellow Dutch Roses', 'Yellow', 420.00, 18, '/static/images/flowers/yellow_roses.jpg'),
(4, 5, 2, 'Pastel Pink Carnation Bunch', 'Pink', 380.00, 30, '/static/images/flowers/pink_carnations.jpg'),
(5, 5, 4, 'Pure White Asiatic Lilies', 'White', 550.00, 12, '/static/images/flowers/white_lilies.jpg'),
(6, 4, 2, 'Grand Wedding Centerpiece', 'Mixed', 1850.00, 8, '/static/images/flowers/wedding_centerpiece.jpg'),
(7, 3, 3, 'Luxury Golden Orchids Vase', 'Yellow', 890.00, 6, '/static/images/flowers/golden_orchids.jpg'),
(8, 1, 1, 'Blush Romance Mixed Bouquet', 'Pink', 750.00, 20, '/static/images/flowers/blush_bouquet.jpg'),
(9, 1, 4, 'Spring Meadow Wildflower Bunch', 'Mixed', 490.00, 4, '/static/images/flowers/spring_wildflowers.jpg'),
(10, 4, 3, 'Crimson & Gold Celebration Hamper', 'Red', 1450.00, 3, '/static/images/flowers/celebration_hamper.jpg'),
(11, 2, 1, 'Scarlet Rose Heart Box', 'Red', 990.00, 0, '/static/images/flowers/heart_roses.jpg'),
(12, 3, 3, 'Peaceful White Orchid Pot', 'White', 720.00, 10, '/static/images/flowers/white_orchids.jpg');

-- Seed Orders (Order 1001 matches report page 14 specification)
INSERT INTO ORDERS (order_id, customer_id, supplier_id, order_date, delivery_date, status, total_amount) VALUES
(1001, 1, 1, '2026-11-21 10:30:00', '2026-11-22', 'Out for Delivery', 1450.00),
(1002, 1, 2, '2026-11-22 08:15:00', '2026-11-22', 'Preparing', 430.00),
(1003, 2, 4, '2026-11-22 09:00:00', '2026-11-23', 'Order Placed', 600.00);

-- Seed Order Items
-- Order 1001: 2 x Red Roses @ 450 = 900; 1 x Orchid Bouquet @ 600 = 600. Subtotal: 1500 + Delivery 50 - Discount 100 = 1450
INSERT INTO ORDER_ITEMS (item_id, order_id, flower_id, quantity, unit_price) VALUES
(1, 1001, 1, 2, 450.00),
(2, 1001, 2, 1, 600.00),
(3, 1002, 4, 1, 380.00),
(4, 1003, 5, 1, 550.00);

-- Seed Payments
INSERT INTO PAYMENTS (payment_id, order_id, method, amount, status, paid_on) VALUES
(1, 1001, 'UPI (Razorpay Mock)', 1450.00, 'Paid', '2026-11-21 10:32:00'),
(2, 1002, 'Card (PayPal Mock)', 430.00, 'Paid', '2026-11-22 08:16:30'),
(3, 1003, 'Cash on Delivery', 600.00, 'Pending', '2026-11-22 09:00:00');

-- Seed Deliveries
INSERT INTO DELIVERIES (delivery_id, order_id, staff_id, address, status, delivered_on) VALUES
(1, 1001, 3, '42 Blossom Hill, Green Park, New Delhi - 110016', 'Out for Delivery', NULL),
(2, 1002, 3, '42 Blossom Hill, Green Park, New Delhi - 110016', 'Assigned', NULL),
(3, 1003, NULL, '15 Coral Heights, Bandra West, Mumbai - 400050', 'Assigned', NULL);
