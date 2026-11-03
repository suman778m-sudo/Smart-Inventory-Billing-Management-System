"""Unit tests for Core Services: AuthService, InventoryService, BillingService, ReportService.

Run with:
    python -m unittest tests/test_services.py
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import db
from models import CartItem
from services.auth_service import AuthService
from services.billing_service import BillingService
from services.inventory_service import InventoryService
from services.invoice_service import generate_invoice
from services.report_service import ReportService


class BaseServiceTestCase(unittest.TestCase):
    """Base test fixture providing in-memory database and initialized service layer."""

    def setUp(self):
        self.conn = db.get_connection(":memory:")
        db.init_db(self.conn)
        self.auth = AuthService(self.conn)
        self.auth.ensure_default_users()
        self.inv = InventoryService(self.conn)
        self.bill = BillingService(self.conn)
        self.rep = ReportService(self.conn)
        self.admin = self.auth.authenticate("admin", "admin123")
        self.staff = self.auth.authenticate("staff", "staff123")

    def tearDown(self):
        self.conn.close()

    def make_cart(self, pid, qty):
        """Helper to create a CartItem from an existing product ID."""
        p = self.inv.get_product(pid)
        return [CartItem(p.id, p.name, p.price, qty)]


class TestAuthService(BaseServiceTestCase):
    """Tests for AuthService: login success, login failure, duplicate user, password hashing."""

    def test_login_success(self):
        """Verify successful authentication returns valid User with correct role."""
        admin_user = self.auth.authenticate("admin", "admin123")
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user.username, "admin")
        self.assertEqual(admin_user.role, "Admin")
        self.assertTrue(admin_user.is_admin)

        staff_user = self.auth.authenticate("staff", "staff123")
        self.assertIsNotNone(staff_user)
        self.assertEqual(staff_user.username, "staff")
        self.assertEqual(staff_user.role, "Staff")
        self.assertFalse(staff_user.is_admin)

        # Case-insensitive username login
        upper_admin = self.auth.authenticate("ADMIN", "admin123")
        self.assertIsNotNone(upper_admin)
        self.assertEqual(upper_admin.username, "admin")

    def test_login_failure(self):
        """Verify authentication failure for invalid passwords and non-existent users."""
        self.assertIsNone(self.auth.authenticate("admin", "wrongpassword"))
        self.assertIsNone(self.auth.authenticate("admin", ""))
        self.assertIsNone(self.auth.authenticate("nonexistent_user", "admin123"))

    def test_duplicate_user(self):
        """Verify creating a user with an existing username raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.auth.create_user("admin", "newpassword123", "Staff")
        self.assertIn("already exists", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            self.auth.create_user("ADMIN", "newpassword123", "Staff")
        self.assertIn("already exists", str(ctx.exception).lower())

    def test_password_is_hashed_with_bcrypt(self):
        """Verify plaintext passwords are never stored directly in the database."""
        row = self.conn.execute("SELECT password_hash FROM users WHERE username='admin'").fetchone()
        stored_hash = row[0]
        self.assertNotIn(b"admin123", stored_hash)
        self.assertTrue(stored_hash.startswith(b"$2b$") or stored_hash.startswith(b"$2a$"))

    def test_create_user_validation(self):
        """Verify password length and role validation during user creation."""
        with self.assertRaises(ValueError):
            self.auth.create_user("shorty", "123", "Staff")  # Password < 6 chars
        with self.assertRaises(ValueError):
            self.auth.create_user("manager", "validpass123", "Manager")  # Invalid role

    def test_cannot_delete_last_admin(self):
        """Verify system safeguard against deleting the sole administrator."""
        with self.assertRaises(ValueError):
            self.auth.delete_user(self.admin.id)


class TestInventoryService(BaseServiceTestCase):
    """Tests for InventoryService: add, update, delete, search, and low-stock detection."""

    def test_add_update_delete_product(self):
        """Verify complete product CRUD lifecycle."""
        pid = self.inv.add_product("Wireless Mouse", "Electronics", 450.0, 50, 10)
        p = self.inv.get_product(pid)
        self.assertIsNotNone(p)
        self.assertEqual(p.name, "Wireless Mouse")
        self.assertEqual(p.category, "Electronics")
        self.assertEqual(p.price, 450.0)
        self.assertEqual(p.quantity, 50)
        self.assertEqual(p.low_stock_threshold, 10)

        # Update product
        self.inv.update_product(pid, "Wireless Mouse Pro", "Electronics", 499.0, 45, 12)
        updated = self.inv.get_product(pid)
        self.assertEqual(updated.name, "Wireless Mouse Pro")
        self.assertEqual(updated.price, 499.0)
        self.assertEqual(updated.quantity, 45)
        self.assertEqual(updated.low_stock_threshold, 12)

        # Delete product
        res = self.inv.delete_product(pid)
        self.assertEqual(res, "deleted")
        self.assertIsNone(self.inv.get_product(pid))

    def test_low_stock_detection(self):
        """Verify low-stock threshold queries identify depleted items."""
        p1 = self.inv.add_product("Pen", "Stationery", 10.0, 3, 5)        # 3 <= 5 -> LOW
        p2 = self.inv.add_product("Notebook", "Stationery", 40.0, 100, 5)   # 100 > 5 -> OK
        p3 = self.inv.add_product("Eraser", "Stationery", 5.0, 5, 5)        # 5 <= 5 -> LOW

        low_products = self.inv.low_stock_products()
        low_ids = [p.id for p in low_products]
        self.assertIn(p1, low_ids)
        self.assertIn(p3, low_ids)
        self.assertNotIn(p2, low_ids)

    def test_validation_rules(self):
        """Verify input validation for names, negative numbers, and non-numeric inputs."""
        invalid_cases = [
            ("", "Electronics", 100.0, 10, 5),     # empty name
            ("A", "Electronics", -10.0, 10, 5),    # negative price
            ("A", "Electronics", 100.0, -5, 5),    # negative stock
            ("A", "Electronics", "abc", 10, 5),    # invalid price format
            ("A", "Electronics", 100.0, 10.5, 5),  # non-integer stock
        ]
        for args in invalid_cases:
            with self.assertRaises(ValueError):
                self.inv.add_product(*args)

    def test_duplicate_product_name_prevented(self):
        """Verify duplicate product names (case-insensitive) are rejected."""
        self.inv.add_product("Gaming Keyboard", "Electronics", 1500.0, 10, 2)
        with self.assertRaises(ValueError) as ctx:
            self.inv.add_product("gaming keyboard", "Electronics", 1600.0, 5, 2)
        self.assertIn("already exists", str(ctx.exception).lower())


class TestBillingService(BaseServiceTestCase):
    """Tests for BillingService: create sale, deduct stock, oversell guard, and transaction integrity."""

    def test_create_sale_and_deduct_stock(self):
        """Verify creating a sale correctly deducts inventory stock and records transaction."""
        pid = self.inv.add_product("Ball Pen", "Stationery", 10.0, 30, 5)
        cart = self.make_cart(pid, 5)

        sid = self.bill.create_sale(self.admin.id, "Amit Sharma", cart)
        self.assertIsInstance(sid, int)

        # Check stock deduction: 30 - 5 = 25
        p = self.inv.get_product(pid)
        self.assertEqual(p.quantity, 25)

        # Check sale record
        sale = self.bill.get_sale(sid)
        expected_subtotal = 50.0
        expected_tax = round(50.0 * config.TAX_PERCENT / 100.0, 2)
        expected_total = round(expected_subtotal + expected_tax, 2)

        self.assertEqual(sale["customer"], "Amit Sharma")
        self.assertEqual(sale["cashier"], "admin")
        self.assertEqual(sale["subtotal"], expected_subtotal)
        self.assertEqual(sale["tax"], expected_tax)
        self.assertEqual(sale["total"], expected_total)
        self.assertEqual(len(sale["items"]), 1)
        self.assertEqual(sale["items"][0]["name"], "Ball Pen")
        self.assertEqual(sale["items"][0]["qty"], 5)
        self.assertEqual(sale["items"][0]["amount"], 50.0)

    def test_oversell_guard_blocks_and_rolls_back(self):
        """Verify purchasing beyond available stock raises ValueError and rolls back the sale."""
        p_ok = self.inv.add_product("Item A", "General", 20.0, 10, 2)
        p_short = self.inv.add_product("Item B", "General", 50.0, 2, 1)

        cart = self.make_cart(p_ok, 2) + self.make_cart(p_short, 5)  # Item B only has 2

        with self.assertRaises(ValueError) as ctx:
            self.bill.create_sale(self.admin.id, "Customer", cart)
        self.assertIn("insufficient stock", str(ctx.exception).lower())

        # Verify atomic rollback: neither stock was changed
        self.assertEqual(self.inv.get_product(p_ok).quantity, 10)
        self.assertEqual(self.inv.get_product(p_short).quantity, 2)

        # No sale row created in database
        sales_count = self.conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        self.assertEqual(sales_count, 0)

    def test_duplicate_cart_lines_merged_for_oversell_check(self):
        """Verify multiple lines of the same item in a cart are aggregated against available stock."""
        pid = self.inv.add_product("Limited Item", "General", 100.0, 5, 1)
        cart = self.make_cart(pid, 3) + self.make_cart(pid, 3)  # Total 6 > 5

        with self.assertRaises(ValueError):
            self.bill.create_sale(self.admin.id, "", cart)
        self.assertEqual(self.inv.get_product(pid).quantity, 5)

    def test_empty_cart_checkout_prevented(self):
        """Verify checkout attempt with an empty cart raises ValueError."""
        with self.assertRaises(ValueError):
            self.bill.create_sale(self.admin.id, "Customer", [])

    def test_sold_product_soft_deactivation(self):
        """Verify deleting a sold product deactivates it without breaking past invoice references."""
        pid = self.inv.add_product("Historical Item", "General", 80.0, 10, 1)
        sid = self.bill.create_sale(self.admin.id, "Customer", self.make_cart(pid, 2))

        status = self.inv.delete_product(pid)
        self.assertEqual(status, "deactivated")
        self.assertIsNone(self.inv.get_product(pid))

        # Sale record and historical item details remain intact
        sale = self.bill.get_sale(sid)
        self.assertEqual(sale["items"][0]["name"], "Historical Item")


class TestReportService(BaseServiceTestCase):
    """Tests for ReportService: today summary totals, periodic reporting, and CSV export."""

    def test_today_summary_returns_correct_totals(self):
        """Verify today_summary correctly computes bill count and cumulative revenue."""
        p1 = self.inv.add_product("Coffee", "Beverage", 150.0, 50, 5)
        p2 = self.inv.add_product("Tea", "Beverage", 50.0, 50, 5)

        # Initial summary with 0 sales
        bills, total = self.rep.today_summary()
        self.assertEqual(bills, 0)
        self.assertEqual(total, 0.0)

        # Sale 1: 1 Coffee (150) + Tax (5% = 7.50) = 157.50
        self.bill.create_sale(self.admin.id, "Cust 1", self.make_cart(p1, 1))

        # Sale 2: 2 Tea (100) + Tax (5% = 5.00) = 105.00
        self.bill.create_sale(self.admin.id, "Cust 2", self.make_cart(p2, 2))

        bills, total = self.rep.today_summary()
        self.assertEqual(bills, 2)
        self.assertAlmostEqual(total, 262.50, places=2)

    def test_periodic_sales_report(self):
        """Verify sales report aggregates correctly for Day, Week, and Month periods."""
        p = self.inv.add_product("Book", "Education", 200.0, 20, 2)
        self.bill.create_sale(self.admin.id, "", self.make_cart(p, 1))

        for period in ("Day", "Week", "Month"):
            rows = self.rep.sales_report(period)
            self.assertEqual(len(rows), 1)
            label, bills, items, sub, tax, total = rows[0]
            self.assertEqual(bills, 1)
            self.assertEqual(items, 1)
            self.assertEqual(sub, 200.0)
            self.assertAlmostEqual(total, sub + tax, places=2)

    def test_top_products_ranking(self):
        """Verify top_products ranks items by quantity sold."""
        p_pop = self.inv.add_product("Popular Pen", "Stationery", 10.0, 100, 5)
        p_rare = self.inv.add_product("Rare Pen", "Stationery", 50.0, 100, 5)

        self.bill.create_sale(self.admin.id, "", self.make_cart(p_pop, 10))
        self.bill.create_sale(self.admin.id, "", self.make_cart(p_rare, 2))

        top = self.rep.top_products(limit=5)
        self.assertEqual(top[0][0], "Popular Pen")
        self.assertEqual(top[0][1], 10)
        self.assertEqual(top[1][0], "Rare Pen")
        self.assertEqual(top[1][1], 2)

    def test_csv_export(self):
        """Verify CSV export writes formatted table rows to file."""
        report_data = [("2026-11-03", 2, 5, 500.0, 25.0, 525.0)]
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "test_report.csv")
            out_file = ReportService.export_csv(report_data, "Day", csv_path)
            self.assertTrue(os.path.exists(out_file))
            with open(out_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Day,Bills,Items sold,Subtotal", content)
                self.assertIn("2026-11-03", content)
                self.assertIn("525.0", content)


if __name__ == "__main__":
    unittest.main()
