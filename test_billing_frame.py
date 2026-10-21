"""Unit tests for BillingFrame UI component."""
import os
import sys
import sqlite3
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from models import CartItem
from services import Services
from ui import theme
from ui.billing_frame import BillingFrame


class TestBillingFrame(unittest.TestCase):
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
        self.user = self.services.auth.authenticate("staff", "staff123")

        # Add sample items
        self.p1_id = self.services.inventory.add_product("Ball Pen", "Stationery", 10.0, 50, 5)
        self.p2_id = self.services.inventory.add_product("Notebook A4", "Stationery", 50.0, 30, 5)

        self.changed = False

        def on_change():
            self.changed = True

        self.frame = BillingFrame(self.root, self.services, self.user, on_change)
        self.frame.pack()

    def tearDown(self):
        self.frame.destroy()
        self.conn.close()

    def test_products_loaded_and_search_filter(self):
        # Verify 2 products loaded
        items = self.frame.products.get_children()
        self.assertEqual(len(items), 2)

        # Test search filter
        self.frame.search.set("Note")
        filtered = self.frame.products.get_children()
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], str(self.p2_id))

        # Reset search
        self.frame.search.set("")
        self.assertEqual(len(self.frame.products.get_children()), 2)

    def test_add_to_cart_and_totals(self):
        # Select p1 and add 2 units
        self.frame.products.selection_set(str(self.p1_id))
        self.frame.qty.set("2")
        self.frame.add_to_cart()

        self.assertIn(self.p1_id, self.frame.cart)
        self.assertEqual(self.frame.cart[self.p1_id].quantity, 2)
        self.assertEqual(self.frame.cart[self.p1_id].amount, 20.0)

        # Add 1 unit of p2
        self.frame.products.selection_set(str(self.p2_id))
        self.frame.qty.set("1")
        self.frame.add_to_cart()

        self.assertEqual(len(self.frame.cart), 2)
        # Subtotal: 20 + 50 = 70.0
        self.assertIn("70.00", self.frame.lbl_sub.get())

    def test_remove_and_clear_cart(self):
        self.frame.products.selection_set(str(self.p1_id))
        self.frame.qty.set("1")
        self.frame.add_to_cart()
        self.assertEqual(len(self.frame.cart), 1)

        # Remove item
        self.frame.cart_tree.selection_set(str(self.p1_id))
        self.frame.remove_selected()
        self.assertEqual(len(self.frame.cart), 0)

        # Add again and clear
        self.frame.products.selection_set(str(self.p2_id))
        self.frame.add_to_cart()
        self.assertEqual(len(self.frame.cart), 1)
        self.frame.clear_cart()
        self.assertEqual(len(self.frame.cart), 0)

    @patch("tkinter.messagebox.askyesno", return_value=False)
    @patch("services.invoice_service.generate_invoice", return_value="dummy_invoice.pdf")
    def test_checkout_workflow(self, mock_invoice, mock_ask):
        self.frame.products.selection_set(str(self.p1_id))
        self.frame.qty.set("3")
        self.frame.add_to_cart()

        self.frame.customer.set("Ramesh Verma")
        self.frame.checkout()

        # Cart should be cleared
        self.assertEqual(len(self.frame.cart), 0)
        self.assertEqual(self.frame.customer.get(), "")

        # Stock should be deducted from 50 to 47
        p1 = self.services.inventory.get_product(self.p1_id)
        self.assertEqual(p1.quantity, 47)

        # on_change callback should have been fired
        self.assertTrue(self.changed)


if __name__ == "__main__":
    unittest.main()
