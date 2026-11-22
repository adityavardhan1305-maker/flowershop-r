# 🌸 Floral Bliss - Flower Shop Management System

A complete, responsive, and easy-to-use **Flower Shop Management System** web application built with **Python (Flask)**, **HTML5/CSS3/JavaScript**, **Bootstrap 5**, and **MySQL** (with seamless SQLite fallback for zero-configuration testing).

---

## 🌟 Key Features

1. **Public Catalog & Landing Page (No Login Required)**
   - Explore landing hero section, browse all flowers, and filter by Category, Color, and Price.
   - Real-time search by flower name and category.
   - Clicking "Add to Cart" or "Buy Now" redirects to login/signup.

2. **Unified Login with 1-Click Demo Accounts**
   - Clickable demo buttons right on the login screen to auto-fill credentials:
     - **Administrator**: `admin@flowershop.com` / `password123`
     - **Florist / Staff**: `florist@flowershop.com` / `password123`
     - **Delivery Person**: `delivery@flowershop.com` / `password123`
     - **Customer**: `customer@flowershop.com` / `password123`
   - Customer self-registration tab.
   - Intelligent role-based redirection to customized dashboards.

3. **Customer Cart & Live Checkout**
   - Live price calculation formula: `Total Amount = Σ(Unit Price × Quantity) + Delivery Charge − Discount`.
   - Out of stock prevention: Prevents checkout if requested quantity exceeds available inventory.
   - Delivery details: address, delivery date, and time slot selection.
   - Interactive **Mock Payment Gateway Modal** simulating Razorpay and PayPal (UPI, Cards, NetBanking) with **Simulate Success (TC07)** and **Simulate Failure (TC08)** sandbox options.
   - Cash on Delivery (COD) support.
   - Real-time visual status pipeline tracker: `Order Placed` &rarr; `Payment Confirmed` &rarr; `Preparing` &rarr; `Out for Delivery` &rarr; `Delivered`.
   - Customer order cancellation before preparation begins.

4. **Florist / Staff Console**
   - Live incoming orders queue with 1-click status transitions (`Preparing`, `Ready / Out for Delivery`).
   - Printable Customer Invoice matching the exact Software Engineering Report format.
   - Real-time Low-Stock Alerts for items with stock &le; 5 units.
   - Quick restock tool to replenish flower counts.

5. **Delivery Staff Console**
   - View assigned orders with customer name, phone (click-to-call), address, and payment status.
   - Status updates: `Start Delivery` &rarr; `Mark Delivered` (records delivery timestamp and clears COD payment).

6. **Administrator Dashboard**
   - Summary analytics cards: Net Revenue, Total Orders, Low-Stock Warnings, Customer Count.
   - Visual charts (Chart.js): Top Selling Flowers and Order Status breakdown.
   - Full CRUD management for **Flowers**, **Categories**, **Suppliers**, **Staff Accounts**, and **Customers**.
   - Logistics module to assign delivery staff to orders.
   - Comprehensive **Sales**, **Inventory**, and **Delivery** reports with CSV export.

---

## 🛠️ Database Setup (MySQL)

The complete SQL setup script and pre-seeded data are contained in [`flower_shop_db.sql`](flower_shop_db.sql).

To import into MySQL:
```bash
mysql -u root -p < flower_shop_db.sql
```

The application automatically checks for an active MySQL service on `localhost:3306`. If MySQL is not running, it automatically uses the included SQLite engine (`flower_shop.db`) with the exact same tables, constraints, and seed records!

---

## 🚀 Running the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser:
   ```
   http://localhost:5000
   ```
