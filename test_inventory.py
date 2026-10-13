"""Unit tests for InventoryService."""
import os
import sys
import sqlite3
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from services.inventory_service import InventoryService


class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)
        self.inv = InventoryService(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_add_and_get_product(self):
        pid = self.inv.add_product("Ball Pen (Blue)", "Stationery", 10.0, 50, 10)
        product = self.inv.get_product(pid)
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Ball Pen (Blue)")
        self.assertEqual(product.category, "Stationery")
        self.assertEqual(product.price, 10.0)
        self.assertEqual(product.quantity, 50)
        self.assertEqual(product.low_stock_threshold, 10)
        self.assertFalse(product.is_low_stock)

    def test_update_product(self):
        pid = self.inv.add_product("Notebook A4", "Stationery", 45.0, 30, 5)
        self.inv.update_product(pid, "Notebook A4", "Stationery", 50.0, 25, 8)
        updated = self.inv.get_product(pid)
        self.assertEqual(updated.price, 50.0)
        self.assertEqual(updated.quantity, 25)
        self.assertEqual(updated.low_stock_threshold, 8)

    def test_delete_product(self):
        pid = self.inv.add_product("Eraser", "Stationery", 5.0, 100, 10)
        status = self.inv.delete_product(pid)
        self.assertEqual(status, "deleted")
        self.assertIsNone(self.inv.get_product(pid))

    def test_validation_rules(self):
        # Empty name
        with self.assertRaises(ValueError):
            self.inv.add_product("", "Stationery", 10, 10, 5)
        # Negative price
        with self.assertRaises(ValueError):
            self.inv.add_product("Test", "Category", -5, 10, 5)
        # Negative quantity
        with self.assertRaises(ValueError):
            self.inv.add_product("Test", "Category", 10, -1, 5)
        # Non-integer quantity
        with self.assertRaises(ValueError):
            self.inv.add_product("Test", "Category", 10, 2.5, 5)

    def test_duplicate_name_fails(self):
        self.inv.add_product("Sugar 1kg", "Grocery", 48.0, 20, 5)
        with self.assertRaises(ValueError):
            self.inv.add_product("sugar 1kg", "Grocery", 50.0, 10, 5)

    def test_search_and_low_stock_detection(self):
        self.inv.add_product("Tea Powder 250g", "Grocery", 120.0, 3, 10)  # low stock
        self.inv.add_product("Coffee 50g", "Beverages", 150.0, 40, 5)    # normal stock

        # Search by category
        grocery = self.inv.list_products("Grocery")
        self.assertEqual(len(grocery), 1)
        self.assertEqual(grocery[0].name, "Tea Powder 250g")

        # Low stock detection
        low_items = self.inv.low_stock_products()
        self.assertEqual(len(low_items), 1)
        self.assertEqual(low_items[0].name, "Tea Powder 250g")
        self.assertTrue(low_items[0].is_low_stock)


if __name__ == "__main__":
    unittest.main()
