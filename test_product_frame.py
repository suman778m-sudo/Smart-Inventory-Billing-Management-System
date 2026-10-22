"""Unit tests for ProductFrame UI component."""
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
from ui.product_frame import ProductFrame


class TestProductFrame(unittest.TestCase):
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

        # Sample products
        self.p1_id = self.services.inventory.add_product("Notebook A4", "Stationery", 45.0, 50, 10)
        self.p2_id = self.services.inventory.add_product("Gel Pen Blue", "Stationery", 15.0, 5, 10)  # low stock

        self.changed = False

        def on_change():
            self.changed = True

        self.on_change = on_change
        self.frame = ProductFrame(self.root, self.services, can_edit=True, on_change=self.on_change)
        self.frame.pack()

    def tearDown(self):
        self.frame.destroy()
        self.conn.close()

    def test_products_loaded_and_status_tags(self):
        items = self.frame.tree.get_children()
        self.assertEqual(len(items), 2)

        # Check values of p1
        p1_row = self.frame.tree.item(str(self.p1_id))["values"]
        self.assertEqual(p1_row[1], "Notebook A4")
        self.assertEqual(p1_row[6], "✔ OK")

        # Check values of p2 (low stock)
        p2_row = self.frame.tree.item(str(self.p2_id))["values"]
        self.assertEqual(p2_row[1], "Gel Pen Blue")
        self.assertEqual(p2_row[6], "⚠ LOW")

    def test_search_filtering(self):
        self.frame.search.set("Pen")
        filtered = self.frame.tree.get_children()
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], str(self.p2_id))

        self.frame.search.set("")
        self.assertEqual(len(self.frame.tree.get_children()), 2)

    def test_selection_populates_form(self):
        self.frame.tree.selection_set(str(self.p1_id))
        self.frame._on_select()

        self.assertEqual(self.frame.selected_id, self.p1_id)
        self.assertEqual(self.frame.vars["name"].get(), "Notebook A4")
        self.assertEqual(self.frame.vars["category"].get(), "Stationery")
        self.assertEqual(float(self.frame.vars["price"].get()), 45.0)
        self.assertEqual(int(self.frame.vars["qty"].get()), 50)
        self.assertEqual(int(self.frame.vars["threshold"].get()), 10)

        # Test clear form
        self.frame.clear_form()
        self.assertIsNone(self.frame.selected_id)
        self.assertEqual(self.frame.vars["name"].get(), "")

    def test_add_product_admin(self):
        self.frame.vars["name"].set("Permanent Marker")
        self.frame.vars["category"].set("Stationery")
        self.frame.vars["price"].set("25.0")
        self.frame.vars["qty"].set("100")
        self.frame.vars["threshold"].set("15")

        self.frame.add()

        # Database and tree verification
        products = self.services.inventory.list_products("Marker")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Permanent Marker")
        self.assertEqual(len(self.frame.tree.get_children()), 3)
        self.assertTrue(self.changed)

    def test_update_product_admin(self):
        self.frame.tree.selection_set(str(self.p1_id))
        self.frame._on_select()

        # Update price and stock
        self.frame.vars["price"].set("55.0")
        self.frame.vars["qty"].set("60")
        self.frame.update()

        updated = self.services.inventory.get_product(self.p1_id)
        self.assertEqual(updated.price, 55.0)
        self.assertEqual(updated.quantity, 60)
        self.assertTrue(self.changed)

    @patch("tkinter.messagebox.askyesno", return_value=True)
    def test_delete_product_admin(self, mock_ask):
        self.frame.tree.selection_set(str(self.p2_id))
        self.frame._on_select()

        self.frame.delete()

        # p2 should be gone
        self.assertIsNone(self.services.inventory.get_product(self.p2_id))
        self.assertEqual(len(self.frame.tree.get_children()), 1)
        self.assertTrue(self.changed)

    def test_view_only_staff_mode(self):
        staff_frame = ProductFrame(self.root, self.services, can_edit=False)
        staff_frame.pack()

        # Table should be present and populated
        self.assertEqual(len(staff_frame.tree.get_children()), 2)
        # Form attributes (self.vars) should not be created for view-only mode
        self.assertFalse(hasattr(staff_frame, "vars"))

        staff_frame.destroy()


if __name__ == "__main__":
    unittest.main()
