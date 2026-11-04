"""Unit tests for Day 28: Edge Cases and Bug Fixes.

Covers:
1. Empty cart checkout guard
2. Graceful PDF generation failure handling (bill persists in DB)
3. Duplicate product name validation error in product form
4. Self-deletion prevention for active logged-in user
5. Screen geometry calculation on small 1366x768 and standard displays
"""
import os
import sys
import sqlite3
import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from main import compute_window_geometry
from models import CartItem
from services import Services
from ui import theme
from ui.billing_frame import BillingFrame
from ui.product_frame import ProductFrame
from ui.users_frame import UsersFrame


class TestEdgeCases(unittest.TestCase):
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

        self.admin = self.services.auth.authenticate("admin", "admin123")
        self.staff = self.services.auth.authenticate("staff", "staff123")

    def tearDown(self):
        self.conn.close()

    # ── 1. Empty cart checkout guard ─────────────────────────────────────────
    def test_empty_cart_checkout_guard(self):
        """Verify checkout attempt with an empty cart displays informational prompt and aborts."""
        frame = BillingFrame(self.root, self.services, self.admin)
        try:
            frame.cart.clear()
            with patch("tkinter.messagebox.showinfo") as mock_info:
                frame.checkout()
                mock_info.assert_called_once()
                self.assertIn("Empty cart", mock_info.call_args[0][0])
                self.assertIn("at least one product", mock_info.call_args[0][1])

            # Ensure no sales recorded in database
            sales_count = self.conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
            self.assertEqual(sales_count, 0)
        finally:
            frame.destroy()

    # ── 2. Graceful PDF generation error handling ────────────────────────────
    def test_pdf_failure_handled_gracefully(self):
        """Verify when PDF generation fails, the sale remains saved in DB and warning is displayed."""
        pid = self.services.inventory.add_product("Notebook", "Stationery", 50.0, 20, 5)
        frame = BillingFrame(self.root, self.services, self.admin)
        try:
            frame.cart[pid] = CartItem(pid, "Notebook", 50.0, 2)
            frame.customer.set("Customer A")

            with patch("ui.billing_frame.generate_invoice", side_effect=RuntimeError("Disk full error")), \
                 patch("tkinter.messagebox.showwarning") as mock_warn:
                frame.checkout()
                mock_warn.assert_called_once()
                title, msg = mock_warn.call_args[0]
                self.assertIn("Invoice PDF Warning", title)
                self.assertIn("Disk full error", msg)

            # Bill must still be recorded in database
            sales = self.services.billing.recent_sales(10)
            self.assertEqual(len(sales), 1)
            self.assertEqual(sales[0][2], "Customer A")

            # Stock must still be decremented (20 - 2 = 18)
            p = self.services.inventory.get_product(pid)
            self.assertEqual(p.quantity, 18)

            # Cart must be cleared
            self.assertEqual(len(frame.cart), 0)
        finally:
            frame.destroy()

    # ── 3. Duplicate product name error handling in form ─────────────────────
    def test_duplicate_product_name_error_handling(self):
        """Verify entering an existing product name triggers user-friendly duplicate error dialog."""
        self.services.inventory.add_product("Wireless Mouse", "Electronics", 450.0, 20, 5)
        frame = ProductFrame(self.root, self.services, can_edit=True)
        try:
            frame.vars["name"].set("Wireless Mouse")
            frame.vars["category"].set("Accessories")
            frame.vars["price"].set("500")
            frame.vars["qty"].set("10")
            frame.vars["threshold"].set("5")

            with patch("tkinter.messagebox.showerror") as mock_err:
                frame.add()
                mock_err.assert_called_once()
                title, msg = mock_err.call_args[0]
                self.assertIn("Duplicate Product", title)
                self.assertIn("already exists", msg)
        finally:
            frame.destroy()

    # ── 4. Prevent deleting own active user account ──────────────────────────
    def test_prevent_deleting_own_user_account(self):
        """Verify currently logged-in administrator cannot delete their own active account."""
        frame = UsersFrame(self.root, self.services, self.admin)
        try:
            # Select admin row
            frame.tree.selection_set(str(self.admin.id))

            with patch("tkinter.messagebox.showwarning") as mock_warn, \
                 patch("tkinter.messagebox.askyesno") as mock_ask:
                frame.delete()
                mock_warn.assert_called_once()
                self.assertIn("Delete", mock_warn.call_args[0][0])
                self.assertIn("cannot delete the account you are logged in with", mock_warn.call_args[0][1])
                mock_ask.assert_not_called()

            # Verify admin user is still in the database
            users = self.services.auth.list_users()
            user_ids = [u.id for u in users]
            self.assertIn(self.admin.id, user_ids)
        finally:
            frame.destroy()

    # ── 5. Small screen geometry computation (1366x768 & standard displays) ──
    def test_screen_resolution_bounds_1366x768(self):
        """Verify window dimensions on a 1366x768 laptop screen fit within bounds with positive margin."""
        w, h, x, y = compute_window_geometry(1366, 768)
        self.assertLessEqual(w, 1366)
        self.assertLessEqual(h, 768)
        self.assertGreaterEqual(w, 1080)
        self.assertGreaterEqual(h, 660)
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)
        self.assertEqual(x, (1366 - w) // 2)
        self.assertEqual(y, (768 - h) // 2)

    def test_screen_resolution_bounds_full_hd(self):
        """Verify window dimensions on a 1920x1080 desktop screen cap at target maximums."""
        w, h, x, y = compute_window_geometry(1920, 1080)
        self.assertEqual(w, 1300)
        self.assertEqual(h, 800)
        self.assertEqual(x, (1920 - 1300) // 2)
        self.assertEqual(y, (1080 - 800) // 2)

    def test_screen_resolution_bounds_compact_display(self):
        """Verify window dimensions on small compact 1280x720 display."""
        w, h, x, y = compute_window_geometry(1280, 720)
        self.assertLessEqual(w, 1280)
        self.assertLessEqual(h, 720)
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)


if __name__ == "__main__":
    unittest.main()
