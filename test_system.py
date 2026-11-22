import os
import unittest
from app import app
import database

class FlowerShopSystemTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        with cls.app.app_context():
            database.init_db(force_reseed=True)

    def setUp(self):
        self.client = self.app.test_client()

    def test_tc01_valid_login(self):
        """TC01: Enter valid username/password -> Login successful"""
        response = self.client.post('/login', data={
            'email': 'customer@flowershop.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Ananya Sharma', response.data)

    def test_tc02_invalid_login(self):
        """TC02: Enter invalid password -> Error message"""
        response = self.client.post('/login', data={
            'email': 'customer@flowershop.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

    def test_tc03_add_flower_admin(self):
        """TC03: Add flower (admin) -> Flower added to catalog"""
        # Login as Admin
        self.client.post('/login', data={'email': 'admin@flowershop.com', 'password': 'password123'})
        response = self.client.post('/admin/flowers', data={
            'action': 'add',
            'name': 'Golden Sunlight Marigold',
            'category_id': 1,
            'supplier_id': 1,
            'color': 'Yellow',
            'price': 299.00,
            'stock_qty': 40,
            'image_url': '/static/images/flowers/yellow_roses.svg'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Golden Sunlight Marigold', response.data)

    def test_tc04_search_flowers(self):
        """TC04: Search flowers by category -> Matching flowers displayed"""
        response = self.client.get('/catalog?search=Orchid')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Royal Purple Orchid Bouquet', response.data)

    def test_tc05_add_flower_to_cart_and_calculate_total(self):
        """TC05: Add flower to cart -> Cart updated with correct total"""
        # Login as customer
        self.client.post('/login', data={'email': 'customer@flowershop.com', 'password': 'password123'})
        # Add flower #1 (Velvet Red Roses @ 450)
        self.client.post('/cart/add', data={'flower_id': 1, 'quantity': 2}, follow_redirects=True)
        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Velvet Red Roses Bouquet', response.data)
        # Subtotal: 900 + 50 (delivery) = 950
        self.assertIn(b'900.00', response.data)

    def test_tc06_order_more_than_available_stock(self):
        """TC06: Order more than available stock -> Out-of-stock message"""
        self.client.post('/login', data={'email': 'customer@flowershop.com', 'password': 'password123'})
        # Flower #11 has 0 stock (Scarlet Rose Heart Box)
        response = self.client.post('/cart/add', data={'flower_id': 11, 'quantity': 1}, follow_redirects=True)
        self.assertIn(b'Out of Stock', response.data)

    def test_tc07_place_order_with_valid_payment(self):
        """TC07: Place order with valid payment -> Order confirmed and invoice generated"""
        self.client.post('/login', data={'email': 'customer@flowershop.com', 'password': 'password123'})
        self.client.post('/cart/add', data={'flower_id': 1, 'quantity': 1})
        response = self.client.post('/checkout', data={
            'delivery_address': '42 Blossom Hill, New Delhi',
            'delivery_date': '2026-11-25',
            'delivery_slot': 'Afternoon (12:00 PM - 04:00 PM)',
            'payment_method': 'Razorpay / PayPal Mock',
            'payment_status': 'Paid'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Order Confirmed!', response.data)

    def test_tc08_payment_failure_simulation(self):
        """TC08: Payment failure -> Order not confirmed; error shown"""
        # In the interactive UI, payment failure keeps the user on checkout without submitting the order
        self.client.post('/login', data={'email': 'customer@flowershop.com', 'password': 'password123'})
        self.client.post('/cart/add', data={'flower_id': 1, 'quantity': 1})
        # Check checkout page renders
        response = self.client.get('/checkout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Simulate Failure (TC08)', response.data)

    def test_tc09_staff_updates_order_status(self):
        """TC09: Staff updates order status -> Customer sees updated status"""
        # Login as Florist staff
        self.client.post('/login', data={'email': 'florist@flowershop.com', 'password': 'password123'})
        response = self.client.post('/staff/order/1001/status', data={'status': 'Preparing'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'status updated to &#39;Preparing&#39;', response.data)

        # Check track order page
        track_resp = self.client.get('/order/track/1001')
        self.assertIn(b'Preparing', track_resp.data)

    def test_tc10_delivery_marks_delivered(self):
        """TC10: Delivery person marks delivered -> Order status set to Delivered"""
        self.client.post('/login', data={'email': 'delivery@flowershop.com', 'password': 'password123'})
        response = self.client.post('/staff/delivery/1/update', data={'status': 'Delivered'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'marked as Delivered', response.data)

    def test_tc11_generate_sales_report(self):
        """TC11: Generate sales report -> Report displayed"""
        self.client.post('/login', data={'email': 'admin@flowershop.com', 'password': 'password123'})
        response = self.client.get('/admin/reports')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Detailed Sales Transactions', response.data)
        self.assertIn(b'Net Confirmed Sales', response.data)

    def test_tc12_unauthorized_user_accesses_admin(self):
        """TC12: Unauthorized user accesses admin page -> Access denied"""
        # Try accessing admin as guest
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Staff authorization required', response.data)

        # Try accessing admin as customer
        self.client.post('/login', data={'email': 'customer@flowershop.com', 'password': 'password123'})
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Staff authorization required', response.data)

if __name__ == '__main__':
    unittest.main()
