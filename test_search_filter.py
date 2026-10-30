"""Unit tests for Live Search & Filtering on Products and Billing screens (Day 23).

Verifies:
1. Multi-field search by product name OR category (case-insensitive).
2. Live keystroke filtering via Tkinter StringVar traces in ProductFrame and BillingFrame.
3. Visual styling retention: low-stock items retain 'low' highlighting during search.
4. Selection persistence: selected product remains selected after table refresh.
"""
import os
import sys
import sqlite3
import tkinter as tk
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from services import Services
from ui import theme
from ui.product_frame import ProductFrame
from ui.billing_frame import BillingFrame


class TestSearchAndFilter(unittest.TestCase):
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
        self.admin = self.services.auth.authenticate("admin", "admin123")

        # Create sample products with distinct categories
        # Category: Stationery
        self.p1 = self.services.inventory.add_product("Spiral Notebook A5", "Stationery", 60.0, 50, 10)
        self.p2 = self.services.inventory.add_product("Ballpoint Pen Blue", "Stationery", 15.0, 4, 10)  # low stock

        # Category: Grocery
        self.p3 = self.services.inventory.add_product("Roasted Almonds 200g", "Grocery", 240.0, 30, 5)
        self.p4 = self.services.inventory.add_product("Instant Oats 1kg", "Grocery", 180.0, 2, 5)     # low stock

        # Category: Electronics
        self.p5 = self.services.inventory.add_product("USB Optical Mouse", "Electronics", 350.0, 20, 5)

    def tearDown(self):
        self.conn.close()

    def test_inventory_service_search_by_name_or_category(self):
        # Search by exact name substring
        res_name = self.services.inventory.list_products("Almonds")
        self.assertEqual(len(res_name), 1)
        self.assertEqual(res_name[0].id, self.p3)

        # Search by category
        res_cat = self.services.inventory.list_products("Stationery")
        self.assertEqual(len(res_cat), 2)
        cat_ids = {p.id for p in res_cat}
        self.assertEqual(cat_ids, {self.p1, self.p2})

        # Case-insensitive search
        res_case = self.services.inventory.list_products("gRoCeRy")
        self.assertEqual(len(res_case), 2)

        # Partial match matching multiple categories/names
        res_partial = self.services.inventory.list_products("o")
        # Notebook, Almonds, Oats, Optical Mouse
        self.assertGreaterEqual(len(res_partial), 4)

    def test_product_frame_live_keystroke_search(self):
        frame = ProductFrame(self.root, self.services, can_edit=True)
        frame.pack()

        # Initial view displays all 5 products
        self.assertEqual(len(frame.tree.get_children()), 5)

        # Live keystroke: type category "Grocery"
        frame.search.set("Grocery")
        grocery_items = frame.tree.get_children()
        self.assertEqual(len(grocery_items), 2)
        self.assertIn(str(self.p3), grocery_items)
        self.assertIn(str(self.p4), grocery_items)

        # Live keystroke: type product name "Pen"
        frame.search.set("Pen")
        pen_items = frame.tree.get_children()
        self.assertEqual(len(pen_items), 1)
        self.assertEqual(pen_items[0], str(self.p2))

        # Clear search: all 5 return
        frame.search.set("")
        self.assertEqual(len(frame.tree.get_children()), 5)

        frame.destroy()

    def test_product_frame_search_retains_low_stock_visual_highlighting(self):
        frame = ProductFrame(self.root, self.services, can_edit=True)
        frame.pack()

        # Filter by Stationery -> p1 (healthy) and p2 (low)
        frame.search.set("Stationery")

        p1_tags = frame.tree.item(str(self.p1))["tags"]
        self.assertNotIn("low", p1_tags)
        self.assertEqual(frame.tree.item(str(self.p1))["values"][6], "✔ OK")

        p2_tags = frame.tree.item(str(self.p2))["tags"]
        self.assertIn("low", p2_tags)
        self.assertEqual(frame.tree.item(str(self.p2))["values"][6], "⚠ LOW")

        frame.destroy()

    def test_product_frame_retains_selected_product_after_refresh(self):
        frame = ProductFrame(self.root, self.services, can_edit=True)
        frame.pack()

        # Select p3 in table
        frame.tree.selection_set(str(self.p3))
        frame._on_select()
        self.assertEqual(frame.selected_id, self.p3)

        # Refresh without search change
        frame.refresh()
        sel = frame.tree.selection()
        self.assertEqual(sel, (str(self.p3),))

        frame.destroy()

    def test_billing_frame_live_search_and_selection_retention(self):
        billing = BillingFrame(self.root, self.services, self.admin)
        billing.pack()

        # 5 products loaded initially
        self.assertEqual(len(billing.products.get_children()), 5)

        # Filter by category "Electronics"
        billing.search.set("Electronics")
        elec_items = billing.products.get_children()
        self.assertEqual(len(elec_items), 1)
        self.assertEqual(elec_items[0], str(self.p5))

        # Select p5
        billing.products.selection_set(str(self.p5))

        # Low-stock item highlighted in search: filter by "Ballpoint"
        billing.search.set("Ballpoint")
        low_items = billing.products.get_children()
        self.assertEqual(len(low_items), 1)
        self.assertIn("low", billing.products.item(str(self.p2))["tags"])

        # Reset search and verify selection persistence
        billing.search.set("")
        billing.products.selection_set(str(self.p1))
        billing.refresh()
        self.assertEqual(billing.products.selection(), (str(self.p1),))

        billing.destroy()


if __name__ == "__main__":
    unittest.main()
