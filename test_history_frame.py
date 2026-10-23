"""Unit tests for HistoryFrame UI component."""
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
from services.invoice_service import invoice_number
from ui import theme
from ui.history_frame import HistoryFrame


class TestHistoryFrame(unittest.TestCase):
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

        # Create sample products
        self.p1_id = self.services.inventory.add_product("Wireless Mouse", "Electronics", 450.0, 50, 5)
        self.p2_id = self.services.inventory.add_product("USB-C Cable", "Electronics", 150.0, 100, 10)

        # Create two sample sales: one with customer name, one walk-in (empty name)
        cart1 = [CartItem(self.p1_id, "Wireless Mouse", 450.0, 1)]
        self.sale1_id = self.services.billing.create_sale(self.admin.id, "Amit Sharma", cart1)

        cart2 = [CartItem(self.p2_id, "USB-C Cable", 150.0, 2)]
        self.sale2_id = self.services.billing.create_sale(self.admin.id, "", cart2)

        self.frame = HistoryFrame(self.root, self.services)
        self.frame.pack()

    def tearDown(self):
        self.frame.destroy()
        self.conn.close()

    def test_history_table_population(self):
        items = self.frame.tree.get_children()
        self.assertEqual(len(items), 2)

        # Verify sale 2 (latest sale first)
        row_sale2 = self.frame.tree.item(str(self.sale2_id))["values"]
        self.assertEqual(row_sale2[0], invoice_number(self.sale2_id))
        self.assertEqual(row_sale2[2], "Walk-in")
        self.assertEqual(row_sale2[4], "admin")

        # Verify sale 1
        row_sale1 = self.frame.tree.item(str(self.sale1_id))["values"]
        self.assertEqual(row_sale1[0], invoice_number(self.sale1_id))
        self.assertEqual(row_sale1[2], "Amit Sharma")
        self.assertEqual(row_sale1[4], "admin")

    @patch("tkinter.messagebox.showinfo")
    def test_open_invoice_requires_selection(self, mock_info):
        self.frame.tree.selection_remove(self.frame.tree.selection())
        self.frame.open_invoice()
        mock_info.assert_called_once()
        self.assertIn("Select a bill first", mock_info.call_args[0][1])

    @patch("ui.history_frame.open_file")
    @patch("ui.history_frame.generate_invoice", return_value="invoices/INV-000001.pdf")
    def test_open_invoice_success(self, mock_gen, mock_open):
        self.frame.tree.selection_set(str(self.sale1_id))
        self.frame.open_invoice()

        mock_gen.assert_called_once()
        sale_arg = mock_gen.call_args[0][0]
        self.assertEqual(sale_arg["id"], self.sale1_id)
        mock_open.assert_called_once_with("invoices/INV-000001.pdf")

    @patch("tkinter.messagebox.showerror")
    @patch("ui.history_frame.generate_invoice", side_effect=RuntimeError("Disk full"))
    def test_open_invoice_handles_error(self, mock_gen, mock_err):
        self.frame.tree.selection_set(str(self.sale1_id))
        self.frame.open_invoice()

        mock_err.assert_called_once()
        self.assertIn("Could not open the invoice", mock_err.call_args[0][1])
        self.assertIn("Disk full", mock_err.call_args[0][1])

    def test_refresh_updates_table(self):
        # Add a 3rd sale
        cart3 = [CartItem(self.p2_id, "USB-C Cable", 150.0, 1)]
        sale3_id = self.services.billing.create_sale(self.admin.id, "Priya Singh", cart3)

        self.frame.refresh()
        items = self.frame.tree.get_children()
        self.assertEqual(len(items), 3)
        self.assertIn(str(sale3_id), items)


if __name__ == "__main__":
    unittest.main()
