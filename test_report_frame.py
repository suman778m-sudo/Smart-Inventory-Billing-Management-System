"""Unit tests for ReportFrame UI component."""
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
from ui.report_frame import ReportFrame


class TestReportFrame(unittest.TestCase):
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

        # Create products and sales data
        self.p1_id = self.services.inventory.add_product("Coffee Beans", "Beverages", 250.0, 100, 10)
        self.p2_id = self.services.inventory.add_product("Green Tea", "Beverages", 120.0, 80, 10)

        cart1 = [CartItem(self.p1_id, "Coffee Beans", 250.0, 2)]
        self.sale1_id = self.services.billing.create_sale(self.admin.id, "Vikram Malhotra", cart1)

        cart2 = [CartItem(self.p2_id, "Green Tea", 120.0, 3)]
        self.sale2_id = self.services.billing.create_sale(self.admin.id, "Sneha Sen", cart2)

        self.frame = ReportFrame(self.root, self.services)
        self.frame.pack()

    def tearDown(self):
        self.frame.destroy()
        self.conn.close()

    def test_report_frame_initialization_and_tables(self):
        # Summary rows should exist for "Day"
        summary_rows = self.frame.tree.get_children()
        self.assertGreater(len(summary_rows), 0)

        # Today's indicator label should show 2 bills
        today_text = self.frame.today.get()
        self.assertIn("2 bill(s)", today_text)

        # Top products table should have rows
        top_rows = self.frame.top.get_children()
        self.assertEqual(len(top_rows), 2)

    def test_period_switch_refresh(self):
        # Change to Week
        self.frame.period.set("Week")
        self.frame.refresh()
        week_rows = self.frame.tree.get_children()
        self.assertGreater(len(week_rows), 0)

        # Change to Month
        self.frame.period.set("Month")
        self.frame.refresh()
        month_rows = self.frame.tree.get_children()
        self.assertGreater(len(month_rows), 0)

    @patch("tkinter.messagebox.showinfo")
    def test_export_csv(self, mock_info):
        self.frame.export()
        mock_info.assert_called_once()
        self.assertIn("Report saved to", mock_info.call_args[0][1])

    @patch("tkinter.messagebox.showinfo")
    def test_export_empty_rows(self, mock_info):
        self.frame.rows = []
        self.frame.export()
        mock_info.assert_called_once()
        self.assertIn("no data to export", mock_info.call_args[0][1])


if __name__ == "__main__":
    unittest.main()
