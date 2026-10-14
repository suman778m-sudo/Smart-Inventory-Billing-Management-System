"""Unit tests for BillingService."""
import os
import sys
import sqlite3
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import db
from models import CartItem
from services.auth_service import AuthService
from services.inventory_service import InventoryService
from services.billing_service import BillingService


class TestBillingService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)
        self.auth = AuthService(self.conn)
        self.inv = InventoryService(self.conn)
        self.bill = BillingService(self.conn)

        self.auth.ensure_default_users()
        self.cashier = self.auth.authenticate("staff", "staff123")

        self.p1_id = self.inv.add_product("Ball Pen", "Stationery", 10.0, 50, 10)
        self.p2_id = self.inv.add_product("Notebook", "Stationery", 40.0, 20, 5)

    def tearDown(self):
        self.conn.close()

    def test_create_sale_reduces_stock_and_calculates_totals(self):
        cart = [
            CartItem(product_id=self.p1_id, name="Ball Pen", unit_price=10.0, quantity=3),
            CartItem(product_id=self.p2_id, name="Notebook", unit_price=40.0, quantity=2),
        ]
        sale_id = self.bill.create_sale(self.cashier.id, "Amit Sharma", cart)
        self.assertIsNotNone(sale_id)

        # Verify stock was deducted
        self.assertEqual(self.inv.get_product(self.p1_id).quantity, 47)
        self.assertEqual(self.inv.get_product(self.p2_id).quantity, 18)

        # Verify sale details
        sale = self.bill.get_sale(sale_id)
        expected_subtotal = (3 * 10.0) + (2 * 40.0)  # 110.0
        expected_tax = round(expected_subtotal * config.TAX_PERCENT / 100, 2)  # 5.50
        expected_total = round(expected_subtotal + expected_tax, 2)  # 115.50

        self.assertEqual(sale["customer"], "Amit Sharma")
        self.assertEqual(sale["cashier"], "staff")
        self.assertEqual(sale["subtotal"], expected_subtotal)
        self.assertEqual(sale["tax"], expected_tax)
        self.assertEqual(sale["total"], expected_total)
        self.assertEqual(len(sale["items"]), 2)

    def test_insufficient_stock_aborts_entire_transaction(self):
        cart = [
            CartItem(product_id=self.p1_id, name="Ball Pen", unit_price=10.0, quantity=2),
            CartItem(product_id=self.p2_id, name="Notebook", unit_price=40.0, quantity=50),  # exceeds stock 20
        ]
        with self.assertRaises(ValueError):
            self.bill.create_sale(self.cashier.id, "Customer", cart)

        # Stock should be untouched due to transaction rollback
        self.assertEqual(self.inv.get_product(self.p1_id).quantity, 50)
        self.assertEqual(self.inv.get_product(self.p2_id).quantity, 20)

    def test_empty_cart_fails(self):
        with self.assertRaises(ValueError):
            self.bill.create_sale(self.cashier.id, "Customer", [])

    def test_invalid_quantity_fails(self):
        with self.assertRaises(ValueError):
            self.bill.create_sale(self.cashier.id, "Customer", [CartItem(self.p1_id, "Pen", 10.0, 0)])
        with self.assertRaises(ValueError):
            self.bill.create_sale(self.cashier.id, "Customer", [CartItem(self.p1_id, "Pen", 10.0, -5)])

    def test_recent_sales(self):
        cart = [CartItem(product_id=self.p1_id, name="Ball Pen", unit_price=10.0, quantity=1)]
        sid1 = self.bill.create_sale(self.cashier.id, "Customer 1", cart)
        sid2 = self.bill.create_sale(self.cashier.id, "Customer 2", cart)

        recent = self.bill.recent_sales(limit=10)
        self.assertGreaterEqual(len(recent), 2)
        # Most recent first
        self.assertEqual(recent[0][0], sid2)
        self.assertEqual(recent[1][0], sid1)


if __name__ == "__main__":
    unittest.main()
