"""Unit tests for ReportService."""
import os
import sys
import sqlite3
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from models import CartItem
from services.auth_service import AuthService
from services.inventory_service import InventoryService
from services.billing_service import BillingService
from services.report_service import ReportService


class TestReportService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)

        self.auth = AuthService(self.conn)
        self.inv = InventoryService(self.conn)
        self.bill = BillingService(self.conn)
        self.rep = ReportService(self.conn)

        self.auth.ensure_default_users()
        self.user = self.auth.authenticate("staff", "staff123")

        # Create products
        self.p1_id = self.inv.add_product("Pen", "Stationery", 10.0, 100, 10)
        self.p2_id = self.inv.add_product("Notebook", "Stationery", 50.0, 50, 5)

        # Make sales
        cart1 = [CartItem(self.p1_id, "Pen", 10.0, 5)]  # 5 pens
        cart2 = [
            CartItem(self.p1_id, "Pen", 10.0, 2),
            CartItem(self.p2_id, "Notebook", 50.0, 1),
        ]  # 2 pens, 1 notebook

        self.bill.create_sale(self.user.id, "Customer A", cart1)
        self.bill.create_sale(self.user.id, "Customer B", cart2)

    def tearDown(self):
        self.conn.close()

    def test_today_summary(self):
        bills, total = self.rep.today_summary()
        self.assertEqual(bills, 2)
        self.assertGreater(total, 0)

    def test_sales_report_day(self):
        rows = self.rep.sales_report("Day")
        self.assertEqual(len(rows), 1)
        date_label, bill_count, items_sold, subtotal, tax, total = rows[0]
        self.assertEqual(bill_count, 2)
        self.assertEqual(items_sold, 8)  # 5 + 2 + 1
        self.assertEqual(subtotal, 120.0)  # 50 + 70

    def test_sales_report_invalid_period(self):
        with self.assertRaises(ValueError):
            self.rep.sales_report("Year")

    def test_top_products(self):
        top = self.rep.top_products(limit=5)
        self.assertEqual(len(top), 2)
        # Pen: 7 sold; Notebook: 1 sold
        self.assertEqual(top[0][0], "Pen")
        self.assertEqual(top[0][1], 7)
        self.assertEqual(top[1][0], "Notebook")
        self.assertEqual(top[1][1], 1)

    def test_export_csv(self):
        rows = self.rep.sales_report("Day")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp_path = tmp.name

        try:
            out_path = self.rep.export_csv(rows, "Day", path=tmp_path)
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Day,Bills,Items sold,Subtotal,Tax,Total", content)
            self.assertIn("120.0", content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
