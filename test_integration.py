"""End-to-End Integration Tests for Smart Inventory & Billing Management System.

Covers full lifecycle user flows across Admin and Staff roles:
1. Admin End-to-End: Login -> Dashboard -> Billing -> Products (CRUD) -> History -> Reports -> Users -> Logout.
2. Staff End-to-End: Login -> Dashboard (restricted) -> Billing -> Products (View-only) -> History -> Logout.
3. System Synchronization: Billing sale -> stock reduction -> low-stock banner trigger -> KPI update.
"""
import os
import sys
import sqlite3
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from main import App
from services import Services
from ui.dashboard import Dashboard
from ui.login_window import LoginFrame
from ui.billing_frame import BillingFrame
from ui.product_frame import ProductFrame
from ui.history_frame import HistoryFrame
from ui.report_frame import ReportFrame
from ui.users_frame import UsersFrame


class TestEndToEndIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root_test = tk.Tk()
            cls.root_test.withdraw()
            cls.has_tk = True
            cls.root_test.destroy()
        except Exception:
            cls.has_tk = False

    def setUp(self):
        if not self.has_tk:
            self.skipTest("Tkinter display not available")

        # In-memory database with foreign keys enabled
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)

        # Ensure seed users (admin / staff)
        self.services = Services(self.conn)
        self.services.auth.ensure_default_users()

        # Seed initial catalog
        self.p_notebook = self.services.inventory.add_product(
            "Executive Notebook", "Stationery", 120.0, 50, 10
        )
        self.p_pen = self.services.inventory.add_product(
            "Fountain Pen", "Stationery", 250.0, 15, 5
        )
        self.p_coffee = self.services.inventory.add_product(
            "Instant Coffee 100g", "Grocery", 180.0, 8, 10  # already low stock
        )

        # Initialize the Application
        self.app = App(self.conn)
        self.app.withdraw()

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass
        self.conn.close()

    def test_admin_end_to_end_flow(self):
        """Admin Login -> Full Dashboard Navigation -> Billing -> Product CRUD -> Reports -> Users -> Logout."""
        # 1. Start at Login Frame
        self.assertIsInstance(self.app.current, LoginFrame)
        login = self.app.current

        # 2. Perform Admin Login
        login.username.set("admin")
        login.password.set("admin123")
        login.login()

        # Verify transition to Dashboard
        self.assertIsInstance(self.app.current, Dashboard)
        dash = self.app.current
        self.assertEqual(dash.user.username, "admin")
        self.assertTrue(dash.user.is_admin)

        # Verify all 5 admin pages registered in page stack
        expected_pages = {"billing", "products", "history", "reports", "users"}
        self.assertEqual(set(dash.pages.keys()), expected_pages)

        # Verify KPI Cards loaded correctly
        # Coffee is 8 (threshold 10) -> exactly 1 product is low stock
        stat_low = dash.kpi_low.value.cget("text")
        self.assertEqual(stat_low, "1")

        stat_products = dash.kpi_products.value.cget("text")
        self.assertEqual(stat_products, "3")

        # 3. Flow into Billing Frame & execute sale
        dash.show_page("billing")
        billing = dash.pages["billing"]
        self.assertIsInstance(billing, BillingFrame)

        # Select Notebook (p_notebook) and add 2 units
        billing.products.selection_set(str(self.p_notebook))
        billing.qty.set("2")
        billing.add_to_cart()

        # Add customer name and checkout with mocked PDF & dialog
        billing.customer.set("Rajiv Menon")
        with patch("services.invoice_service.generate_invoice", return_value="dummy_inv.pdf"), \
             patch("tkinter.messagebox.askyesno", return_value=False):
            billing.checkout()

        # Verify stock decreased: 50 - 2 = 48
        p_updated = self.services.inventory.get_product(self.p_notebook)
        self.assertEqual(p_updated.quantity, 48)

        # 4. Flow into Products Frame (Admin mode: can edit)
        dash.show_page("products")
        prod_frame = dash.pages["products"]
        self.assertIsInstance(prod_frame, ProductFrame)
        self.assertTrue(prod_frame.can_edit)

        # Admin adds a 4th product
        prod_frame.vars["name"].set("Sticky Notes")
        prod_frame.vars["category"].set("Stationery")
        prod_frame.vars["price"].set("40.0")
        prod_frame.vars["qty"].set("100")
        prod_frame.vars["threshold"].set("15")
        prod_frame.add()

        # Verify 4 products exist now
        self.assertEqual(len(self.services.inventory.list_products()), 4)

        # 5. Flow into History Frame
        dash.show_page("history")
        hist_frame = dash.pages["history"]
        self.assertIsInstance(hist_frame, HistoryFrame)

        # Check recent sale appears
        history_rows = hist_frame.tree.get_children()
        self.assertEqual(len(history_rows), 1)
        latest_val = hist_frame.tree.item(history_rows[0])["values"]
        self.assertEqual(latest_val[2], "Rajiv Menon")
        self.assertEqual(latest_val[4], "admin")

        # 6. Flow into Reports Frame
        dash.show_page("reports")
        rep_frame = dash.pages["reports"]
        self.assertIsInstance(rep_frame, ReportFrame)
        rep_rows = rep_frame.tree.get_children()
        self.assertGreater(len(rep_rows), 0)

        # 7. Flow into Users Frame
        dash.show_page("users")
        users_frame = dash.pages["users"]
        self.assertIsInstance(users_frame, UsersFrame)

        # Create new staff user
        users_frame.username.set("intern_rohit")
        users_frame.password.set("rohitPass2026")
        users_frame.role.set("Staff")
        users_frame.add()

        new_auth = self.services.auth.authenticate("intern_rohit", "rohitPass2026")
        self.assertIsNotNone(new_auth)
        self.assertEqual(new_auth.role, "Staff")

        # 8. Admin Logout
        self.app.show_login()
        self.assertIsInstance(self.app.current, LoginFrame)

    def test_staff_end_to_end_flow(self):
        """Staff Login -> Restricted Dashboard -> Billing -> Stock View (No Edit) -> History -> Logout."""
        login = self.app.current
        login.username.set("staff")
        login.password.set("staff123")
        login.login()

        self.assertIsInstance(self.app.current, Dashboard)
        dash = self.app.current
        self.assertEqual(dash.user.username, "staff")
        self.assertFalse(dash.user.is_admin)

        # Verify role filtering: Reports and Users management are completely excluded
        expected_pages = {"billing", "products", "history"}
        self.assertEqual(set(dash.pages.keys()), expected_pages)
        self.assertNotIn("reports", dash.pages)
        self.assertNotIn("users", dash.pages)

        # Staff navigates to Stock/Products view (Read-only mode)
        dash.show_page("products")
        prod_frame = dash.pages["products"]
        self.assertIsInstance(prod_frame, ProductFrame)
        self.assertFalse(prod_frame.can_edit)
        self.assertFalse(hasattr(prod_frame, "vars"))

        # Staff completes a transaction
        dash.show_page("billing")
        billing = dash.pages["billing"]
        billing.products.selection_set(str(self.p_pen))
        billing.qty.set("1")
        billing.add_to_cart()

        with patch("services.invoice_service.generate_invoice", return_value="dummy_inv2.pdf"), \
             patch("tkinter.messagebox.askyesno", return_value=False):
            billing.checkout()

        # Check in history
        dash.show_page("history")
        hist = dash.pages["history"]
        hist_rows = hist.tree.get_children()
        self.assertEqual(len(hist_rows), 1)
        cashier_name = hist.tree.item(hist_rows[0])["values"][4]
        self.assertEqual(cashier_name, "staff")

        # Staff Logout
        self.app.show_login()
        self.assertIsInstance(self.app.current, LoginFrame)

    def test_low_stock_detection_and_banner_trigger(self):
        """Verify dynamic low-stock detection triggers low-stock alert banner upon checkout."""
        login = self.app.current
        login.username.set("admin")
        login.password.set("admin123")
        login.login()
        dash = self.app.current

        # Initially p_pen has qty=15, threshold=5 (healthy)
        # Sell 12 pens -> 3 left (drops below threshold 5 -> becomes LOW STOCK)
        dash.show_page("billing")
        billing = dash.pages["billing"]
        billing.products.selection_set(str(self.p_pen))
        billing.qty.set("12")
        billing.add_to_cart()

        with patch("services.invoice_service.generate_invoice", return_value="dummy.pdf"), \
             patch("tkinter.messagebox.askyesno", return_value=False), \
             patch("tkinter.messagebox.showwarning"):
            billing.checkout()

        # Re-check low stock count on dashboard: was 1 (coffee), now 2 (coffee + pen)
        dash.refresh_kpis()
        stat_low = dash.kpi_low.value.cget("text")
        self.assertEqual(stat_low, "2")

        # Banner should be updated with both item names
        banner_text = dash.banner_label.cget("text")
        self.assertIn("Fountain Pen", banner_text)
        self.assertIn("Instant Coffee 100g", banner_text)


if __name__ == "__main__":
    unittest.main()
