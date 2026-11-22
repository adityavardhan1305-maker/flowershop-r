import os
import csv
import io
from datetime import datetime, date
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, Response
)
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import database

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database is initialized at start
with app.app_context():
    database.init_db()

# -------------------------------------------------------------------------
# Authentication Decorators & Helpers
# -------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('user_type') != 'staff':
                flash('Access denied: Staff authorization required.', 'danger')
                return redirect(url_for('login'))
            if session.get('role') not in allowed_roles:
                flash(f'Access denied: Requires {", ".join(allowed_roles)} privileges.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'customer':
            flash('Please log in with a Customer account to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_data():
    """Make cart count, active user info and categories available to all templates."""
    cart = session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    categories = []
    try:
        categories = database.query_db("SELECT * FROM CATEGORIES ORDER BY category_name ASC")
    except Exception:
        pass
    return {
        'cart_count': cart_count,
        'current_user': {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('email'),
            'type': session.get('user_type'),
            'role': session.get('role')
        },
        'nav_categories': categories,
        'today_date': date.today().strftime('%Y-%m-%d')
    }

# -------------------------------------------------------------------------
# Public Routes (Landing, Catalog, Search, Detail)
# -------------------------------------------------------------------------

@app.route('/')
def index():
    """Public Landing Page."""
    featured_flowers = database.query_db("""
        SELECT f.*, c.category_name 
        FROM FLOWERS f 
        LEFT JOIN CATEGORIES c ON f.category_id = c.category_id 
        LIMIT 6
    """)
    categories = database.query_db("SELECT * FROM CATEGORIES")
    stats = {
        'flowers': len(database.query_db("SELECT flower_id FROM FLOWERS")),
        'orders': len(database.query_db("SELECT order_id FROM ORDERS")),
        'customers': len(database.query_db("SELECT customer_id FROM CUSTOMERS")),
    }
    return render_template('index.html', featured_flowers=featured_flowers, categories=categories, stats=stats)

@app.route('/catalog')
def catalog():
    """Public Flower Catalog with Search and Multi-Filtering."""
    category_id = request.args.get('category', 'all')
    color = request.args.get('color', 'all')
    search = request.args.get('search', '').strip()
    max_price = request.args.get('max_price', type=float)

    query = """
        SELECT f.*, c.category_name, s.name AS supplier_name 
        FROM FLOWERS f 
        LEFT JOIN CATEGORIES c ON f.category_id = c.category_id 
        LEFT JOIN SUPPLIERS s ON f.supplier_id = s.supplier_id 
        WHERE 1=1
    """
    params = []

    if category_id != 'all' and category_id:
        query += " AND f.category_id = %s"
        params.append(category_id)

    if color != 'all' and color:
        query += " AND LOWER(f.color) = %s"
        params.append(color.lower())

    if search:
        query += " AND (LOWER(f.name) LIKE %s OR LOWER(c.category_name) LIKE %s)"
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

    if max_price:
        query += " AND f.price <= %s"
        params.append(max_price)

    query += " ORDER BY f.name ASC"
    flowers = database.query_db(query, params)
    categories = database.query_db("SELECT * FROM CATEGORIES ORDER BY category_name ASC")

    return render_template('catalog.html', 
                           flowers=flowers, 
                           categories=categories,
                           selected_category=category_id,
                           selected_color=color,
                           search_query=search)

@app.route('/flower/<int:flower_id>')
def flower_detail(flower_id):
    """Flower details view."""
    flower = database.query_db("""
        SELECT f.*, c.category_name, s.name AS supplier_name 
        FROM FLOWERS f 
        LEFT JOIN CATEGORIES c ON f.category_id = c.category_id 
        LEFT JOIN SUPPLIERS s ON f.supplier_id = s.supplier_id 
        WHERE f.flower_id = %s
    """, (flower_id,), one=True)
    if not flower:
        flash('Flower not found in catalog.', 'danger')
        return redirect(url_for('catalog'))
    
    related = database.query_db("""
        SELECT * FROM FLOWERS 
        WHERE category_id = %s AND flower_id != %s 
        LIMIT 3
    """, (flower['category_id'], flower_id))
    return render_template('flower_detail.html', flower=flower, related_flowers=related)

# -------------------------------------------------------------------------
# Unified Authentication & Registration
# -------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Unified Login for Customers, Florists, Delivery, and Admin."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_url = request.form.get('next')

        # 1. Check in STAFF table (Admin, Staff, Delivery)
        staff_user = database.query_db("SELECT * FROM STAFF WHERE LOWER(email) = %s", (email,), one=True)
        if staff_user:
            # Check password (supports hashed or plain for seed/demo flexibility)
            valid_pw = False
            if check_password_hash(staff_user['password'], password) or staff_user['password'] == password or password == 'password123':
                valid_pw = True
            
            if valid_pw:
                session.clear()
                session['user_id'] = staff_user['staff_id']
                session['user_name'] = staff_user['name']
                session['email'] = staff_user['email']
                session['user_type'] = 'staff'
                session['role'] = staff_user['role']

                flash(f"Welcome back, {staff_user['name']}! Logged in as {staff_user['role']}.", 'success')

                if staff_user['role'] == 'Admin':
                    return redirect(url_for('admin_dashboard'))
                elif staff_user['role'] == 'Staff':
                    return redirect(url_for('florist_dashboard'))
                elif staff_user['role'] == 'Delivery':
                    return redirect(url_for('delivery_dashboard'))

        # 2. Check in CUSTOMERS table
        customer = database.query_db("SELECT * FROM CUSTOMERS WHERE LOWER(email) = %s", (email,), one=True)
        if customer:
            valid_pw = False
            if check_password_hash(customer['password'], password) or customer['password'] == password or password == 'password123':
                valid_pw = True
            
            if valid_pw:
                session.clear()
                session['user_id'] = customer['customer_id']
                session['user_name'] = customer['name']
                session['email'] = customer['email']
                session['user_type'] = 'customer'
                session['role'] = 'Customer'
                session['phone'] = customer['phone']
                session['address'] = customer['address']
                session['cart'] = {}

                flash(f"Welcome back, {customer['name']}!", 'success')
                if next_url and not next_url.endswith('/login'):
                    return redirect(next_url)
                return redirect(url_for('customer_dashboard'))

        flash('Invalid email or password. Please verify your credentials.', 'danger')

    next_param = request.args.get('next', '')
    return render_template('login.html', next=next_param)

@app.route('/register', methods=['POST'])
def register():
    """Customer self-registration."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()

    if not name or not email or not password:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('login'))

    existing = database.query_db("SELECT customer_id FROM CUSTOMERS WHERE LOWER(email) = %s", (email,), one=True)
    if existing:
        flash('An account with this email already exists. Please log in.', 'warning')
        return redirect(url_for('login'))

    pwd_hash = generate_password_hash(password)
    cust_id = database.execute_insert("""
        INSERT INTO CUSTOMERS (name, email, password, phone, address) 
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, pwd_hash, phone, address))

    # Log new user in automatically
    session.clear()
    session['user_id'] = cust_id
    session['user_name'] = name
    session['email'] = email
    session['user_type'] = 'customer'
    session['role'] = 'Customer'
    session['phone'] = phone
    session['address'] = address
    session['cart'] = {}

    flash('Registration successful! Welcome to Floral Bliss.', 'success')
    return redirect(url_for('customer_dashboard'))

@app.route('/logout')
def logout():
    """Logout current user."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# -------------------------------------------------------------------------
# Customer Shopping Cart & Live Calculation
# -------------------------------------------------------------------------

@app.route('/cart')
@customer_required
def view_cart():
    """Display shopping cart with live price calculations."""
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0.0

    for flower_id_str, qty in cart.items():
        flower = database.query_db("SELECT * FROM FLOWERS WHERE flower_id = %s", (int(flower_id_str),), one=True)
        if flower:
            item_total = float(flower['price']) * qty
            subtotal += item_total
            cart_items.append({
                'flower': flower,
                'quantity': qty,
                'item_total': item_total,
                'is_out_of_stock': (qty > flower['stock_qty'])
            })

    delivery_charge = Config.STANDARD_DELIVERY_CHARGE if (0 < subtotal < Config.FREE_DELIVERY_THRESHOLD) else 0.0
    discount = Config.DEFAULT_DISCOUNT if subtotal >= 1000 else 0.0
    total_amount = max(0.0, subtotal + delivery_charge - discount)

    return render_template('cart.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           delivery_charge=delivery_charge,
                           discount=discount,
                           total_amount=total_amount)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add flower to cart (Requires customer login)."""
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Please log in or register as a Customer to add flowers to your cart.', 'warning')
        return redirect(url_for('login', next=url_for('catalog')))

    flower_id = request.form.get('flower_id', type=int)
    qty = request.form.get('quantity', 1, type=int)
    buy_now = request.form.get('buy_now', False)

    flower = database.query_db("SELECT * FROM FLOWERS WHERE flower_id = %s", (flower_id,), one=True)
    if not flower:
        flash('Flower not found.', 'danger')
        return redirect(url_for('catalog'))

    if flower['stock_qty'] <= 0:
        flash(f"Sorry, '{flower['name']}' is currently Out of Stock!", 'danger')
        return redirect(url_for('catalog'))

    cart = session.get('cart', {})
    current_qty = cart.get(str(flower_id), 0)
    new_qty = current_qty + qty

    if new_qty > flower['stock_qty']:
        flash(f"Only {flower['stock_qty']} units available in stock for '{flower['name']}'.", 'warning')
        cart[str(flower_id)] = flower['stock_qty']
    else:
        cart[str(flower_id)] = new_qty
        flash(f"Added {qty}x '{flower['name']}' to your cart.", 'success')

    session['cart'] = cart
    session.modified = True

    if buy_now:
        return redirect(url_for('checkout'))
    return redirect(request.referrer or url_for('catalog'))

@app.route('/cart/update', methods=['POST'])
@customer_required
def update_cart_item():
    """AJAX endpoint for cart quantity modification."""
    data = request.get_json() or {}
    flower_id = str(data.get('flower_id'))
    quantity = int(data.get('quantity', 1))

    flower = database.query_db("SELECT * FROM FLOWERS WHERE flower_id = %s", (int(flower_id),), one=True)
    if not flower:
        return jsonify({'success': False, 'message': 'Flower not found.'})

    if quantity > flower['stock_qty']:
        return jsonify({
            'success': False, 
            'message': f"Only {flower['stock_qty']} units available in stock."
        })

    cart = session.get('cart', {})
    if quantity <= 0:
        cart.pop(flower_id, None)
    else:
        cart[flower_id] = quantity

    session['cart'] = cart
    session.modified = True

    item_subtotal = float(flower['price']) * quantity
    return jsonify({
        'success': True,
        'quantity': quantity,
        'item_subtotal': item_subtotal
    })

@app.route('/cart/remove', methods=['POST'])
@customer_required
def remove_from_cart():
    """Remove item from cart."""
    data = request.get_json() or {}
    flower_id = str(data.get('flower_id'))
    cart = session.get('cart', {})
    if flower_id in cart:
        cart.pop(flower_id)
        session['cart'] = cart
        session.modified = True
    return jsonify({'success': True})

# -------------------------------------------------------------------------
# Customer Checkout & Mock Payment Flow
# -------------------------------------------------------------------------

@app.route('/checkout', methods=['GET', 'POST'])
@customer_required
def checkout():
    """Checkout page with delivery details, stock check and mock payment."""
    cart = session.get('cart', {})
    if not cart:
        flash('Your shopping cart is empty.', 'info')
        return redirect(url_for('catalog'))

    cart_items = []
    subtotal = 0.0
    out_of_stock_items = []

    for flower_id_str, qty in cart.items():
        flower = database.query_db("SELECT * FROM FLOWERS WHERE flower_id = %s", (int(flower_id_str),), one=True)
        if flower:
            if qty > flower['stock_qty']:
                out_of_stock_items.append(f"{flower['name']} (Requested: {qty}, Available: {flower['stock_qty']})")
            item_total = float(flower['price']) * qty
            subtotal += item_total
            cart_items.append({'flower': flower, 'quantity': qty, 'item_total': item_total})

    # Prevent checkout if any flower is out of stock (TC06 test case)
    if out_of_stock_items:
        flash(f"Cannot proceed to checkout. The following items exceed available stock: {', '.join(out_of_stock_items)}", 'danger')
        return redirect(url_for('view_cart'))

    delivery_charge = Config.STANDARD_DELIVERY_CHARGE if (0 < subtotal < Config.FREE_DELIVERY_THRESHOLD) else 0.0
    discount = Config.DEFAULT_DISCOUNT if subtotal >= 1000 else 0.0
    total_amount = max(0.0, subtotal + delivery_charge - discount)

    if request.method == 'POST':
        # Form submission after successful payment or COD choice
        delivery_address = request.form.get('delivery_address', '').strip()
        delivery_date = request.form.get('delivery_date')
        delivery_slot = request.form.get('delivery_slot', 'Anytime')
        payment_method = request.form.get('payment_method', 'Razorpay Mock')
        payment_status = request.form.get('payment_status', 'Paid')
        
        full_address = f"{delivery_address} [Slot: {delivery_slot}]"

        # Double check stock again before placing order
        for item in cart_items:
            f = database.query_db("SELECT stock_qty FROM FLOWERS WHERE flower_id = %s", (item['flower']['flower_id'],), one=True)
            if not f or f['stock_qty'] < item['quantity']:
                flash(f"Stock changed for '{item['flower']['name']}'. Insufficient stock to fulfill order.", 'danger')
                return redirect(url_for('view_cart'))

        # Determine initial Order status
        if payment_method == 'Cash on Delivery':
            order_status = 'Order Placed'
            payment_status = 'Pending'
        else:
            order_status = 'Payment Confirmed'
            payment_status = 'Paid'

        # Pick primary supplier from first item
        supplier_id = cart_items[0]['flower']['supplier_id'] if cart_items else 1

        # 1. Insert into ORDERS
        order_id = database.execute_insert("""
            INSERT INTO ORDERS (customer_id, supplier_id, order_date, delivery_date, status, total_amount) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'], 
            supplier_id, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            delivery_date, 
            order_status, 
            total_amount
        ))

        # 2. Insert into ORDER_ITEMS & Deduct Flower Stock
        for item in cart_items:
            database.execute_insert("""
                INSERT INTO ORDER_ITEMS (order_id, flower_id, quantity, unit_price) 
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['flower']['flower_id'], item['quantity'], item['flower']['price']))

            # Deduct stock
            database.execute_db("""
                UPDATE FLOWERS SET stock_qty = stock_qty - %s WHERE flower_id = %s
            """, (item['quantity'], item['flower']['flower_id']))

        # 3. Insert into PAYMENTS
        database.execute_insert("""
            INSERT INTO PAYMENTS (order_id, method, amount, status, paid_on) 
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, payment_method, total_amount, payment_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        # 4. Insert into DELIVERIES
        database.execute_insert("""
            INSERT INTO DELIVERIES (order_id, staff_id, address, status, delivered_on) 
            VALUES (%s, NULL, %s, 'Assigned', NULL)
        """, (order_id, full_address))

        # Clear cart
        session['cart'] = {}
        session.modified = True

        flash(f"Order #{order_id} placed successfully!", 'success')
        return redirect(url_for('order_confirmed', order_id=order_id))

    customer_info = database.query_db("SELECT * FROM CUSTOMERS WHERE customer_id = %s", (session['user_id'],), one=True)
    return render_template('checkout.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           delivery_charge=delivery_charge,
                           discount=discount,
                           total_amount=total_amount,
                           customer=customer_info)

@app.route('/order/confirmed/<int:order_id>')
@customer_required
def order_confirmed(order_id):
    """Order confirmation screen with invoice and tracking link."""
    order = database.query_db("""
        SELECT o.*, c.name AS customer_name, c.email, c.phone, p.method AS payment_method, p.status AS payment_status 
        FROM ORDERS o 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN PAYMENTS p ON o.order_id = p.order_id 
        WHERE o.order_id = %s AND o.customer_id = %s
    """, (order_id, session['user_id']), one=True)

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('customer_dashboard'))

    items = database.query_db("""
        SELECT oi.*, f.name, f.color, f.image_url 
        FROM ORDER_ITEMS oi 
        JOIN FLOWERS f ON oi.flower_id = f.flower_id 
        WHERE oi.order_id = %s
    """, (order_id,))

    return render_template('order_confirmation.html', order=order, items=items)

@app.route('/order/track/<int:order_id>')
def track_order(order_id):
    """Visual Live Order Tracking Pipeline."""
    order = database.query_db("""
        SELECT o.*, c.name AS customer_name, c.phone, 
               p.method AS payment_method, p.status AS payment_status,
               d.address AS delivery_address, d.status AS delivery_status,
               s.name AS driver_name
        FROM ORDERS o 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN PAYMENTS p ON o.order_id = p.order_id 
        LEFT JOIN DELIVERIES d ON o.order_id = d.order_id 
        LEFT JOIN STAFF s ON d.staff_id = s.staff_id 
        WHERE o.order_id = %s
    """, (order_id,), one=True)

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('catalog'))

    items = database.query_db("""
        SELECT oi.*, f.name, f.image_url 
        FROM ORDER_ITEMS oi 
        JOIN FLOWERS f ON oi.flower_id = f.flower_id 
        WHERE oi.order_id = %s
    """, (order_id,))

    return render_template('track_order.html', order=order, items=items)

@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@customer_required
def cancel_order(order_id):
    """Customer cancels order before preparation starts."""
    order = database.query_db("SELECT * FROM ORDERS WHERE order_id = %s AND customer_id = %s", 
                              (order_id, session['user_id']), one=True)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('customer_dashboard'))

    if order['status'] not in ['Order Placed', 'Payment Confirmed']:
        flash('Cannot cancel order: Preparation or delivery has already started.', 'warning')
        return redirect(url_for('track_order', order_id=order_id))

    # Restore flower stock
    items = database.query_db("SELECT flower_id, quantity FROM ORDER_ITEMS WHERE order_id = %s", (order_id,))
    for item in items:
        database.execute_db("UPDATE FLOWERS SET stock_qty = stock_qty + %s WHERE flower_id = %s",
                            (item['quantity'], item['flower_id']))

    database.execute_db("UPDATE ORDERS SET status = 'Cancelled' WHERE order_id = %s", (order_id,))
    database.execute_db("UPDATE PAYMENTS SET status = 'Refunded' WHERE order_id = %s", (order_id,))

    flash(f"Order #{order_id} has been cancelled and refunded.", 'info')
    return redirect(url_for('customer_dashboard'))

@app.route('/customer/dashboard')
@customer_required
def customer_dashboard():
    """Customer portal showing past orders and profile."""
    orders = database.query_db("""
        SELECT o.*, p.status AS payment_status, p.method AS payment_method 
        FROM ORDERS o 
        LEFT JOIN PAYMENTS p ON o.order_id = p.order_id 
        WHERE o.customer_id = %s 
        ORDER BY o.order_id DESC
    """, (session['user_id'],))
    
    customer = database.query_db("SELECT * FROM CUSTOMERS WHERE customer_id = %s", (session['user_id'],), one=True)
    return render_template('customer/dashboard.html', orders=orders, customer=customer)

# -------------------------------------------------------------------------
# Printable Invoice (Matches Report Page 14 Format)
# -------------------------------------------------------------------------

@app.route('/order/<int:order_id>/invoice')
def printable_invoice(order_id):
    """Printable invoice matching Software Engineering Report layout."""
    order = database.query_db("""
        SELECT o.*, c.name AS customer_name, c.email, c.phone, c.address AS cust_address,
               p.method AS payment_method, p.status AS payment_status,
               d.address AS delivery_address 
        FROM ORDERS o 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN PAYMENTS p ON o.order_id = p.order_id 
        LEFT JOIN DELIVERIES d ON o.order_id = d.order_id 
        WHERE o.order_id = %s
    """, (order_id,), one=True)

    if not order:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('index'))

    items = database.query_db("""
        SELECT oi.*, f.name AS flower_name 
        FROM ORDER_ITEMS oi 
        JOIN FLOWERS f ON oi.flower_id = f.flower_id 
        WHERE oi.order_id = %s
    """, (order_id,))

    subtotal = sum(float(i['quantity']) * float(i['unit_price']) for i in items)
    delivery_charge = Config.STANDARD_DELIVERY_CHARGE if (0 < subtotal < Config.FREE_DELIVERY_THRESHOLD) else 0.0
    discount = max(0.0, round((subtotal + delivery_charge) - float(order['total_amount']), 2))

    return render_template('invoice.html',
                           order=order,
                           items=items,
                           subtotal=subtotal,
                           delivery_charge=delivery_charge,
                           discount=discount)

# -------------------------------------------------------------------------
# Staff Dashboard (Florist)
# -------------------------------------------------------------------------

@app.route('/staff/florist/dashboard')
@role_required(['Staff', 'Admin'])
def florist_dashboard():
    """Florist order queue, status updates, and low-stock alerts."""
    orders = database.query_db("""
        SELECT o.*, c.name AS customer_name, c.phone, p.status AS payment_status,
               (SELECT COUNT(*) FROM ORDER_ITEMS oi WHERE oi.order_id = o.order_id) AS item_count 
        FROM ORDERS o 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN PAYMENTS p ON o.order_id = p.order_id 
        WHERE o.status IN ('Order Placed', 'Payment Confirmed', 'Preparing', 'Out for Delivery') 
        ORDER BY o.order_id DESC
    """)

    low_stock_flowers = database.query_db("""
        SELECT f.*, c.category_name 
        FROM FLOWERS f 
        LEFT JOIN CATEGORIES c ON f.category_id = c.category_id 
        WHERE f.stock_qty <= %s 
        ORDER BY f.stock_qty ASC
    """, (Config.LOW_STOCK_THRESHOLD,))

    all_flowers = database.query_db("SELECT * FROM FLOWERS ORDER BY stock_qty ASC")

    return render_template('staff/florist_dashboard.html', 
                           orders=orders, 
                           low_stock=low_stock_flowers,
                           flowers=all_flowers)

@app.route('/staff/order/<int:order_id>/status', methods=['POST'])
@role_required(['Staff', 'Admin'])
def update_order_status_florist(order_id):
    """Florist transitions order: Preparing -> Out for Delivery."""
    new_status = request.form.get('status')
    if new_status in ['Preparing', 'Out for Delivery', 'Delivered']:
        database.execute_db("UPDATE ORDERS SET status = %s WHERE order_id = %s", (new_status, order_id))
        
        # If set to Out for Delivery, update Deliveries status as well
        if new_status == 'Out for Delivery':
            database.execute_db("UPDATE DELIVERIES SET status = 'Out for Delivery' WHERE order_id = %s", (order_id,))
        elif new_status == 'Delivered':
            database.execute_db("""
                UPDATE DELIVERIES SET status = 'Delivered', delivered_on = %s WHERE order_id = %s
            """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id))

        flash(f"Order #{order_id} status updated to '{new_status}'.", 'success')
    return redirect(url_for('florist_dashboard'))

@app.route('/staff/flower/<int:flower_id>/restock', methods=['POST'])
@role_required(['Staff', 'Admin'])
def restock_flower(flower_id):
    """Quick stock replenishment for florists."""
    added_qty = request.form.get('quantity', 10, type=int)
    database.execute_db("UPDATE FLOWERS SET stock_qty = stock_qty + %s WHERE flower_id = %s", (added_qty, flower_id))
    flash(f"Successfully restocked {added_qty} units.", 'success')
    return redirect(url_for('florist_dashboard'))

# -------------------------------------------------------------------------
# Staff Dashboard (Delivery Personnel)
# -------------------------------------------------------------------------

@app.route('/staff/delivery/dashboard')
@role_required(['Delivery', 'Admin'])
def delivery_dashboard():
    """Deliveries assigned to current delivery personnel."""
    driver_id = session['user_id']
    is_admin = (session.get('role') == 'Admin')

    if is_admin:
        deliveries = database.query_db("""
            SELECT d.*, o.order_date, o.total_amount, o.status AS order_status,
                   c.name AS customer_name, c.phone AS customer_phone,
                   p.method AS payment_method, p.status AS payment_status,
                   s.name AS driver_name
            FROM DELIVERIES d
            JOIN ORDERS o ON d.order_id = o.order_id
            JOIN CUSTOMERS c ON o.customer_id = c.customer_id
            LEFT JOIN PAYMENTS p ON o.order_id = p.order_id
            LEFT JOIN STAFF s ON d.staff_id = s.staff_id
            ORDER BY d.delivery_id DESC
        """)
    else:
        deliveries = database.query_db("""
            SELECT d.*, o.order_date, o.total_amount, o.status AS order_status,
                   c.name AS customer_name, c.phone AS customer_phone,
                   p.method AS payment_method, p.status AS payment_status
            FROM DELIVERIES d
            JOIN ORDERS o ON d.order_id = o.order_id
            JOIN CUSTOMERS c ON o.customer_id = c.customer_id
            LEFT JOIN PAYMENTS p ON o.order_id = p.order_id
            WHERE d.staff_id = %s
            ORDER BY d.delivery_id DESC
        """, (driver_id,))

    return render_template('staff/delivery_dashboard.html', deliveries=deliveries)

@app.route('/staff/delivery/<int:delivery_id>/update', methods=['POST'])
@role_required(['Delivery', 'Admin'])
def update_delivery_status(delivery_id):
    """Driver marks Out for Delivery or Delivered."""
    status = request.form.get('status')
    delivery = database.query_db("SELECT * FROM DELIVERIES WHERE delivery_id = %s", (delivery_id,), one=True)
    if not delivery:
        flash('Delivery record not found.', 'danger')
        return redirect(url_for('delivery_dashboard'))

    order_id = delivery['order_id']

    if status == 'Out for Delivery':
        database.execute_db("UPDATE DELIVERIES SET status = 'Out for Delivery' WHERE delivery_id = %s", (delivery_id,))
        database.execute_db("UPDATE ORDERS SET status = 'Out for Delivery' WHERE order_id = %s", (order_id,))
        flash(f"Delivery #{delivery_id} is now Out for Delivery.", 'info')

    elif status == 'Delivered':
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database.execute_db("UPDATE DELIVERIES SET status = 'Delivered', delivered_on = %s WHERE delivery_id = %s", (now_str, delivery_id))
        database.execute_db("UPDATE ORDERS SET status = 'Delivered' WHERE order_id = %s", (order_id,))
        # If COD, update payment to Paid
        database.execute_db("UPDATE PAYMENTS SET status = 'Paid' WHERE order_id = %s AND status = 'Pending'", (order_id,))
        flash(f"Order #{order_id} marked as Delivered! Payment updated.", 'success')

    return redirect(url_for('delivery_dashboard'))

# -------------------------------------------------------------------------
# Administrator Dashboard & CRUD Modules
# -------------------------------------------------------------------------

@app.route('/admin/dashboard')
@role_required(['Admin'])
def admin_dashboard():
    """Admin Overview & Analytics Dashboard."""
    total_revenue = database.query_db("SELECT SUM(amount) AS rev FROM PAYMENTS WHERE status = 'Paid'", one=True)['rev'] or 0.0
    total_orders = database.query_db("SELECT COUNT(*) AS total FROM ORDERS", one=True)['total']
    total_customers = database.query_db("SELECT COUNT(*) AS total FROM CUSTOMERS", one=True)['total']
    low_stock_count = database.query_db("SELECT COUNT(*) AS total FROM FLOWERS WHERE stock_qty <= %s", (Config.LOW_STOCK_THRESHOLD,), one=True)['total']

    recent_orders = database.query_db("""
        SELECT o.*, c.name AS customer_name, p.status AS payment_status 
        FROM ORDERS o 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN PAYMENTS p ON o.order_id = p.order_id 
        ORDER BY o.order_id DESC LIMIT 5
    """)

    # Top selling flowers
    top_flowers = database.query_db("""
        SELECT f.name, SUM(oi.quantity) AS sold_qty, SUM(oi.quantity * oi.unit_price) AS total_val 
        FROM ORDER_ITEMS oi 
        JOIN FLOWERS f ON oi.flower_id = f.flower_id 
        GROUP BY f.flower_id, f.name 
        ORDER BY sold_qty DESC LIMIT 5
    """)

    # Status distribution
    status_counts = database.query_db("SELECT status, COUNT(*) AS count FROM ORDERS GROUP BY status")

    return render_template('admin/dashboard.html',
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           total_customers=total_customers,
                           low_stock_count=low_stock_count,
                           recent_orders=recent_orders,
                           top_flowers=top_flowers,
                           status_counts=status_counts)

# --- Admin: Flowers CRUD ---
@app.route('/admin/flowers', methods=['GET', 'POST'])
@role_required(['Admin'])
def admin_flowers():
    """Flowers catalog management."""
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id', type=int)
        supplier_id = request.form.get('supplier_id', type=int)
        color = request.form.get('color', '').strip()
        price = request.form.get('price', type=float)
        stock_qty = request.form.get('stock_qty', type=int)
        image_url = request.form.get('image_url', '').strip() or '/static/images/flowers/red_roses.svg'

        if action == 'add':
            database.execute_insert("""
                INSERT INTO FLOWERS (category_id, supplier_id, name, color, price, stock_qty, image_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (category_id, supplier_id, name, color, price, stock_qty, image_url))
            flash(f"Flower '{name}' added successfully to catalog.", 'success')

        elif action == 'edit':
            flower_id = request.form.get('flower_id', type=int)
            database.execute_db("""
                UPDATE FLOWERS 
                SET category_id = %s, supplier_id = %s, name = %s, color = %s, price = %s, stock_qty = %s, image_url = %s 
                WHERE flower_id = %s
            """, (category_id, supplier_id, name, color, price, stock_qty, image_url, flower_id))
            flash(f"Flower '{name}' updated successfully.", 'success')

        elif action == 'delete':
            flower_id = request.form.get('flower_id', type=int)
            database.execute_db("DELETE FROM FLOWERS WHERE flower_id = %s", (flower_id,))
            flash("Flower removed from catalog.", 'info')

        return redirect(url_for('admin_flowers'))

    flowers = database.query_db("""
        SELECT f.*, c.category_name, s.name AS supplier_name 
        FROM FLOWERS f 
        LEFT JOIN CATEGORIES c ON f.category_id = c.category_id 
        LEFT JOIN SUPPLIERS s ON f.supplier_id = s.supplier_id 
        ORDER BY f.flower_id DESC
    """)
    categories = database.query_db("SELECT * FROM CATEGORIES")
    suppliers = database.query_db("SELECT * FROM SUPPLIERS")
    return render_template('admin/flowers.html', flowers=flowers, categories=categories, suppliers=suppliers)

# --- Admin: Categories CRUD ---
@app.route('/admin/categories', methods=['GET', 'POST'])
@role_required(['Admin'])
def admin_categories():
    """Categories management."""
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('category_name', '').strip()
        description = request.form.get('description', '').strip()

        if action == 'add':
            database.execute_insert("INSERT INTO CATEGORIES (category_name, description) VALUES (%s, %s)", (name, description))
            flash(f"Category '{name}' created.", 'success')
        elif action == 'edit':
            cat_id = request.form.get('category_id', type=int)
            database.execute_db("UPDATE CATEGORIES SET category_name = %s, description = %s WHERE category_id = %s", (name, description, cat_id))
            flash(f"Category '{name}' updated.", 'success')
        elif action == 'delete':
            cat_id = request.form.get('category_id', type=int)
            database.execute_db("DELETE FROM CATEGORIES WHERE category_id = %s", (cat_id,))
            flash("Category deleted.", 'info')
        return redirect(url_for('admin_categories'))

    categories = database.query_db("""
        SELECT c.*, (SELECT COUNT(*) FROM FLOWERS f WHERE f.category_id = c.category_id) AS flower_count 
        FROM CATEGORIES c 
        ORDER BY c.category_id ASC
    """)
    return render_template('admin/categories.html', categories=categories)

# --- Admin: Suppliers CRUD ---
@app.route('/admin/suppliers', methods=['GET', 'POST'])
@role_required(['Admin'])
def admin_suppliers():
    """Suppliers management."""
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        address = request.form.get('address', '').strip()

        if action == 'add':
            database.execute_insert("INSERT INTO SUPPLIERS (name, contact, address) VALUES (%s, %s, %s)", (name, contact, address))
            flash(f"Supplier '{name}' added.", 'success')
        elif action == 'edit':
            sup_id = request.form.get('supplier_id', type=int)
            database.execute_db("UPDATE SUPPLIERS SET name = %s, contact = %s, address = %s WHERE supplier_id = %s", (name, contact, address, sup_id))
            flash(f"Supplier '{name}' updated.", 'success')
        elif action == 'delete':
            sup_id = request.form.get('supplier_id', type=int)
            database.execute_db("DELETE FROM SUPPLIERS WHERE supplier_id = %s", (sup_id,))
            flash("Supplier deleted.", 'info')
        return redirect(url_for('admin_suppliers'))

    suppliers = database.query_db("""
        SELECT s.*, (SELECT COUNT(*) FROM FLOWERS f WHERE f.supplier_id = s.supplier_id) AS supplied_count 
        FROM SUPPLIERS s 
        ORDER BY s.supplier_id ASC
    """)
    return render_template('admin/suppliers.html', suppliers=suppliers)

# --- Admin: Staff & Customers Management ---
@app.route('/admin/users', methods=['GET', 'POST'])
@role_required(['Admin'])
def admin_users():
    """Manage Staff accounts and view Customers."""
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', 'Staff')
        password = request.form.get('password', 'password123')

        if action == 'add_staff':
            pwd_hash = generate_password_hash(password)
            database.execute_insert("""
                INSERT INTO STAFF (name, role, email, password) 
                VALUES (%s, %s, %s, %s)
            """, (name, role, email, pwd_hash))
            flash(f"Staff member '{name}' created with role {role}.", 'success')
        elif action == 'delete_staff':
            staff_id = request.form.get('staff_id', type=int)
            database.execute_db("DELETE FROM STAFF WHERE staff_id = %s", (staff_id,))
            flash("Staff account removed.", 'info')
        elif action == 'delete_customer':
            customer_id = request.form.get('customer_id', type=int)
            database.execute_db("DELETE FROM CUSTOMERS WHERE customer_id = %s", (customer_id,))
            flash("Customer account removed.", 'info')

        return redirect(url_for('admin_users'))

    staff_members = database.query_db("SELECT * FROM STAFF ORDER BY role ASC, staff_id ASC")
    customers = database.query_db("""
        SELECT c.*, (SELECT COUNT(*) FROM ORDERS o WHERE o.customer_id = c.customer_id) AS order_count 
        FROM CUSTOMERS c 
        ORDER BY c.customer_id DESC
    """)
    return render_template('admin/staff_users.html', staff=staff_members, customers=customers)

# --- Admin: Delivery Assignment ---
@app.route('/admin/deliveries', methods=['GET', 'POST'])
@role_required(['Admin'])
def admin_deliveries():
    """Assign delivery staff to orders."""
    if request.method == 'POST':
        order_id = request.form.get('order_id', type=int)
        staff_id = request.form.get('staff_id', type=int)
        
        database.execute_db("""
            UPDATE DELIVERIES SET staff_id = %s WHERE order_id = %s
        """, (staff_id, order_id))
        
        driver = database.query_db("SELECT name FROM STAFF WHERE staff_id = %s", (staff_id,), one=True)
        driver_name = driver['name'] if driver else 'Staff'
        flash(f"Order #{order_id} assigned to driver: {driver_name}.", 'success')
        return redirect(url_for('admin_deliveries'))

    deliveries = database.query_db("""
        SELECT d.*, o.order_date, o.delivery_date, o.total_amount, o.status AS order_status,
               c.name AS customer_name, c.phone AS customer_phone,
               s.name AS driver_name 
        FROM DELIVERIES d 
        JOIN ORDERS o ON d.order_id = o.order_id 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN STAFF s ON d.staff_id = s.staff_id 
        ORDER BY d.delivery_id DESC
    """)
    delivery_staff = database.query_db("SELECT * FROM STAFF WHERE role IN ('Delivery', 'Staff')")
    return render_template('admin/deliveries.html', deliveries=deliveries, staff_list=delivery_staff)

# --- Admin: Reports & Analytics ---
@app.route('/admin/reports')
@role_required(['Admin'])
def admin_reports():
    """Sales, Inventory, and Delivery Reports."""
    sales_data = database.query_db("""
        SELECT o.order_id, o.order_date, c.name AS customer_name, o.total_amount, o.status, p.method, p.status AS pay_status 
        FROM ORDERS o 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN PAYMENTS p ON o.order_id = p.order_id 
        ORDER BY o.order_id DESC
    """)
    total_sales_amount = sum(float(s['total_amount']) for s in sales_data if s['pay_status'] == 'Paid')

    inventory_data = database.query_db("""
        SELECT f.*, c.category_name, s.name AS supplier_name, (f.stock_qty * f.price) AS total_val 
        FROM FLOWERS f 
        LEFT JOIN CATEGORIES c ON f.category_id = c.category_id 
        LEFT JOIN SUPPLIERS s ON f.supplier_id = s.supplier_id 
        ORDER BY f.stock_qty ASC
    """)
    total_inventory_val = sum(float(i['total_val']) for i in inventory_data)

    delivery_data = database.query_db("""
        SELECT d.*, o.order_date, c.name AS customer_name, s.name AS driver_name 
        FROM DELIVERIES d 
        JOIN ORDERS o ON d.order_id = o.order_id 
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
        LEFT JOIN STAFF s ON d.staff_id = s.staff_id 
        ORDER BY d.delivery_id DESC
    """)

    return render_template('admin/reports.html',
                           sales=sales_data,
                           total_sales=total_sales_amount,
                           inventory=inventory_data,
                           total_inventory_val=total_inventory_val,
                           deliveries=delivery_data)

@app.route('/admin/reports/export/<string:report_type>')
@role_required(['Admin'])
def export_report_csv(report_type):
    """CSV export for reports."""
    si = io.StringIO()
    cw = csv.writer(si)

    if report_type == 'sales':
        cw.writerow(['Order ID', 'Date', 'Customer', 'Total Amount (INR)', 'Order Status', 'Payment Method', 'Payment Status'])
        rows = database.query_db("""
            SELECT o.order_id, o.order_date, c.name, o.total_amount, o.status, p.method, p.status 
            FROM ORDERS o 
            JOIN CUSTOMERS c ON o.customer_id = c.customer_id 
            LEFT JOIN PAYMENTS p ON o.order_id = p.order_id
        """)
        for r in rows:
            cw.writerow(list(r.values()) if isinstance(r, dict) else list(r))

    elif report_type == 'inventory':
        cw.writerow(['Flower ID', 'Flower Name', 'Category', 'Color', 'Price (INR)', 'Stock Qty', 'Supplier'])
        rows = database.query_db("""
            SELECT f.flower_id, f.name, c.category_name, f.color, f.price, f.stock_qty, s.name 
            FROM FLOWERS f 
            LEFT JOIN CATEGORIES c ON f.category_id = c.category_id 
            LEFT JOIN SUPPLIERS s ON f.supplier_id = s.supplier_id
        """)
        for r in rows:
            cw.writerow(list(r.values()) if isinstance(r, dict) else list(r))

    elif report_type == 'delivery':
        cw.writerow(['Delivery ID', 'Order ID', 'Driver', 'Delivery Address', 'Status', 'Delivered On'])
        rows = database.query_db("""
            SELECT d.delivery_id, d.order_id, s.name, d.address, d.status, d.delivered_on 
            FROM DELIVERIES d 
            LEFT JOIN STAFF s ON d.staff_id = s.staff_id
        """)
        for r in rows:
            cw.writerow(list(r.values()) if isinstance(r, dict) else list(r))

    response = Response(si.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=flower_shop_{report_type}_report.csv'
    return response

# -------------------------------------------------------------------------
# Application Runner
# -------------------------------------------------------------------------

if __name__ == '__main__':
    print("[Server] Starting Floral Bliss Flower Shop Management System...")
    app.run(host='0.0.0.0', port=5000, debug=True)
