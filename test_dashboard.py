"""Unit tests for Dashboard UI layout and navigation."""
import os
import sys
import sqlite3
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from services import Services
from ui import theme
from ui.dashboard import Dashboard, NavItem


class TestDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
            theme.apply_theme(cls.root)
        except Exception:
            cls.root = None

    @classmethod
    def tearDownClass(cls):
        if cls.root is not None:
            cls.root.destroy()

    def setUp(self):
        if self.root is None:
            self.skipTest("Tkinter display not available")
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)
        self.services = Services(self.conn)
        self.services.auth.ensure_default_users()

        # Add sample product (normal stock)
        self.services.inventory.add_product("Pen", "Stationery", 10.0, 50, 5)

        self.admin = self.services.auth.authenticate("admin", "admin123")
        self.staff = self.services.auth.authenticate("staff", "staff123")

    def tearDown(self):
        self.conn.close()

    @patch("tkinter.messagebox.showwarning")
    def test_admin_dashboard_pages_and_kpis(self, mock_warn):
        logout_called = False

        def on_logout():
            nonlocal logout_called
            logout_called = True

        dash = Dashboard(self.root, self.services, self.admin, on_logout)
        dash.pack()

        # Admin must have all 5 pages
        self.assertIn("billing", dash.pages)
        self.assertIn("products", dash.pages)
        self.assertIn("history", dash.pages)
        self.assertIn("reports", dash.pages)
        self.assertIn("users", dash.pages)

        # Current page starts at billing
        self.assertEqual(dash.current_key, "billing")

        # Test page navigation
        dash.show_page("products")
        self.assertEqual(dash.current_key, "products")
        self.assertEqual(dash.title.get(), "Products")

        # Test KPI values
        dash.refresh_kpis()
        self.assertEqual(dash.kpi_products.value.cget("text"), "1")
        self.assertEqual(dash.kpi_low.value.cget("text"), "0")

        dash.destroy()

    @patch("tkinter.messagebox.showwarning")
    def test_staff_dashboard_restricted_pages(self, mock_warn):
        dash = Dashboard(self.root, self.services, self.staff, lambda: None)
        dash.pack()

        # Staff must only have 3 pages (no reports, no users)
        self.assertIn("billing", dash.pages)
        self.assertIn("products", dash.pages)
        self.assertIn("history", dash.pages)
        self.assertNotIn("reports", dash.pages)
        self.assertNotIn("users", dash.pages)

        # For staff, products tab is named "Stock"
        dash.show_page("products")
        self.assertEqual(dash.title.get(), "Stock")

        dash.destroy()

    def test_nav_item_states(self):
        clicked = False

        def on_click():
            nonlocal clicked
            clicked = True

        nav = NavItem(self.root, "📦", "Products", on_click)
        self.assertFalse(nav.active)

        nav.set_active(True)
        self.assertTrue(nav.active)
        self.assertEqual(nav.cget("bg"), NavItem.ACTIVE_BG)

        nav.set_active(False)
        self.assertFalse(nav.active)
        self.assertEqual(nav.cget("bg"), theme.SIDEBAR)

        nav.destroy()


if __name__ == "__main__":
    unittest.main()
