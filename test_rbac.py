"""Unit tests for Day 26: Role-Based Access Control (RBAC).

Verifies page visibility, role badge rendering, stock read-only view, and permission guards.
"""
import os
import sys
import sqlite3
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from models import User
from services import Services
from ui import theme
from ui.dashboard import Dashboard
from ui.product_frame import ProductFrame


class TestRoleBasedAccessControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
            theme.apply_theme(cls.root)
            cls.has_tk = True
        except Exception:
            cls.has_tk = False
            cls.root = None

    @classmethod
    def tearDownClass(cls):
        if cls.root is not None:
            cls.root.destroy()

    def setUp(self):
        if not self.has_tk:
            self.skipTest("Tkinter display not available")

        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)

        self.services = Services(self.conn)
        self.services.auth.ensure_default_users()

        self.admin_user = self.services.auth.authenticate("admin", "admin123")
        self.staff_user = self.services.auth.authenticate("staff", "staff123")

    def tearDown(self):
        self.conn.close()

    def test_admin_sidebar_and_page_registration(self):
        """Admin has all 5 pages: billing, products, history, reports, users."""
        dash = Dashboard(self.root, self.services, self.admin_user, on_logout=lambda: None)
        try:
            expected_pages = {"billing", "products", "history", "reports", "users"}
            self.assertEqual(set(dash.pages.keys()), expected_pages)
            self.assertEqual(set(dash.nav.keys()), expected_pages)

            # Check that products is labeled 'Products' for Admin
            self.assertEqual(dash.titles["products"][0], "Products")
            self.assertIn("Products", dash.nav["products"].label.cget("text"))

            # Check Role Badge for Admin
            badge_text = dash.role_badge.cget("text")
            self.assertIn("ADMIN", badge_text)
            self.assertEqual(dash.role_badge.cget("bg"), "#252458")
            self.assertEqual(dash.role_badge.cget("fg"), "#c7d2fe")
        finally:
            dash.destroy()

    def test_staff_sidebar_restricted(self):
        """Staff only sees billing, products (Stock), and history. Reports and Users are excluded."""
        dash = Dashboard(self.root, self.services, self.staff_user, on_logout=lambda: None)
        try:
            allowed_pages = {"billing", "products", "history"}
            self.assertEqual(set(dash.pages.keys()), allowed_pages)
            self.assertEqual(set(dash.nav.keys()), allowed_pages)

            # Reports and Users must not exist
            self.assertNotIn("reports", dash.pages)
            self.assertNotIn("users", dash.pages)
            self.assertNotIn("reports", dash.nav)
            self.assertNotIn("users", dash.nav)

            # Check Role Badge for Staff
            badge_text = dash.role_badge.cget("text")
            self.assertIn("STAFF", badge_text)
            self.assertEqual(dash.role_badge.cget("bg"), "#0b382d")
            self.assertEqual(dash.role_badge.cget("fg"), "#a7f3d0")
        finally:
            dash.destroy()

    def test_staff_sees_stock_label_instead_of_products(self):
        """Staff sees 'Stock' instead of 'Products' in the sidebar navigation and header."""
        dash = Dashboard(self.root, self.services, self.staff_user, on_logout=lambda: None)
        try:
            self.assertEqual(dash.titles["products"][0], "Stock")
            self.assertEqual(dash.titles["products"][1], "Check what is available on the shelf.")
            self.assertIn("Stock", dash.nav["products"].label.cget("text"))

            # When showing products page, title is updated to Stock
            dash.show_page("products")
            self.assertEqual(dash.title.get(), "Stock")
            self.assertEqual(dash.subtitle.get(), "Check what is available on the shelf.")
        finally:
            dash.destroy()

    def test_staff_cannot_navigate_to_admin_pages(self):
        """Invoking show_page with admin pages on a staff dashboard is blocked and returns False."""
        dash = Dashboard(self.root, self.services, self.staff_user, on_logout=lambda: None)
        try:
            # Initially on billing
            dash.show_page("billing")
            self.assertEqual(dash.current_key, "billing")

            # Try navigating to reports
            allowed = dash.show_page("reports")
            self.assertFalse(allowed)
            self.assertEqual(dash.current_key, "billing")

            # Try navigating to users
            allowed = dash.show_page("users")
            self.assertFalse(allowed)
            self.assertEqual(dash.current_key, "billing")
        finally:
            dash.destroy()

    def test_product_frame_staff_view_only(self):
        """ProductFrame for staff (can_edit=False) operates in read-only view mode."""
        frame = ProductFrame(self.root, self.services, can_edit=False)
        try:
            self.assertFalse(frame.can_edit)
            # Edit form vars should not be defined
            self.assertFalse(hasattr(frame, "vars"))

            # Guarded methods should display error and abort without crashing
            with patch("tkinter.messagebox.showerror") as mock_err:
                frame.add()
                mock_err.assert_called_once()
                self.assertIn("Permission Denied", mock_err.call_args[0][0])

            with patch("tkinter.messagebox.showerror") as mock_err:
                frame.update()
                mock_err.assert_called_once()
                self.assertIn("Permission Denied", mock_err.call_args[0][0])

            with patch("tkinter.messagebox.showerror") as mock_err:
                frame.delete()
                mock_err.assert_called_once()
                self.assertIn("Permission Denied", mock_err.call_args[0][0])
        finally:
            frame.destroy()

    def test_role_badge_color_contrast(self):
        """Verify Admin and Staff role badges have distinct, high-contrast palette colors."""
        dash_admin = Dashboard(self.root, self.services, self.admin_user, on_logout=lambda: None)
        dash_staff = Dashboard(self.root, self.services, self.staff_user, on_logout=lambda: None)
        try:
            # Backgrounds must be distinct
            self.assertNotEqual(dash_admin.role_badge.cget("bg"), dash_staff.role_badge.cget("bg"))
            # Foreground text colors must be distinct
            self.assertNotEqual(dash_admin.role_badge.cget("fg"), dash_staff.role_badge.cget("fg"))
        finally:
            dash_admin.destroy()
            dash_staff.destroy()


if __name__ == "__main__":
    unittest.main()
