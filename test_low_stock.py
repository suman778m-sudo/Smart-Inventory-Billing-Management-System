"""Unit tests for the Low-Stock Alert System (Day 22).

Verifies:
1. Low-stock banner auto-show & auto-hide functionality.
2. Application startup popup warning for low-stock products.
3. Post-checkout low-stock alert dialog for purchased items crossing threshold.
4. "⚠ LOW" and "✔ OK" status badges and table row tagging in ProductFrame.
5. Dynamic color-coded KPI card values (red when low, green when fully stocked).
"""
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
from ui.dashboard import Dashboard
from ui.billing_frame import BillingFrame
from ui.product_frame import ProductFrame


class TestLowStockAlertSystem(unittest.TestCase):
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

        # Initial products: 1 healthy, 1 low stock
        self.p_healthy = self.services.inventory.add_product("Stapler", "Stationery", 80.0, 40, 10)
        self.p_low = self.services.inventory.add_product("Stapler Pins", "Stationery", 20.0, 5, 10)

        self.dash = Dashboard(self.root, self.services, self.admin, on_logout=lambda: None)
        self.dash.pack()

    def tearDown(self):
        self.dash.destroy()
        self.conn.close()

    def test_low_stock_banner_auto_show_and_hide(self):
        # 1. Low stock item exists -> banner should be managed by pack
        self.dash.refresh_kpis()
        self.assertEqual(self.dash.banner_wrap.winfo_manager(), "pack")
        banner_text = self.dash.banner_label.cget("text")
        self.assertIn("Stapler Pins (5)", banner_text)

        # 2. Restock the low item above threshold (5 -> 50)
        self.services.inventory.update_product(self.p_low, "Stapler Pins", "Stationery", 20.0, 50, 10)
        self.dash.refresh_kpis()

        # Banner should auto-hide (unpacked)
        self.assertEqual(self.dash.banner_wrap.winfo_manager(), "")

    @patch("tkinter.messagebox.showwarning")
    def test_startup_popup_alert(self, mock_warn):
        # When low stock items exist, startup alert should show warning
        self.dash._startup_alert()
        mock_warn.assert_called_once()
        self.assertIn("Stapler Pins: 5 left", mock_warn.call_args[0][1])

        # When no items are low, no warning should appear
        mock_warn.reset_mock()
        self.services.inventory.update_product(self.p_low, "Stapler Pins", "Stationery", 20.0, 50, 10)
        self.dash._startup_alert()
        mock_warn.assert_not_called()

    @patch("services.invoice_service.generate_invoice", return_value="dummy_inv.pdf")
    @patch("tkinter.messagebox.askyesno", return_value=False)
    @patch("tkinter.messagebox.showwarning")
    def test_post_checkout_low_stock_alert(self, mock_warn, mock_ask, mock_pdf):
        billing = BillingFrame(self.root, self.services, self.admin)
        billing.pack()

        # Healthy item: 40 stock, threshold 10. Buy 35 -> 5 left (newly low stock!)
        billing.products.selection_set(str(self.p_healthy))
        billing.qty.set("35")
        billing.add_to_cart()

        billing.checkout()

        # Verify low-stock warning was triggered post-checkout
        mock_warn.assert_called_once()
        alert_msg = mock_warn.call_args[0][1]
        self.assertIn("Stapler: 5 left", alert_msg)

        billing.destroy()

    def test_products_table_status_badges(self):
        prod_frame = ProductFrame(self.root, self.services, can_edit=True)
        prod_frame.pack()

        # Healthy item should have ✔ OK status and even/odd tag
        healthy_vals = prod_frame.tree.item(str(self.p_healthy))["values"]
        self.assertEqual(healthy_vals[6], "✔ OK")
        healthy_tags = prod_frame.tree.item(str(self.p_healthy))["tags"]
        self.assertNotIn("low", healthy_tags)

        # Low item should have ⚠ LOW status and 'low' tag
        low_vals = prod_frame.tree.item(str(self.p_low))["values"]
        self.assertEqual(low_vals[6], "⚠ LOW")
        low_tags = prod_frame.tree.item(str(self.p_low))["tags"]
        self.assertIn("low", low_tags)

        prod_frame.destroy()

    def test_color_coded_kpi_card_value(self):
        # When low stock exists: value text is '1', color is DANGER (red)
        self.dash.refresh_kpis()
        self.assertEqual(self.dash.kpi_low.value.cget("text"), "1")
        self.assertEqual(self.dash.kpi_low.value.cget("foreground"), theme.DANGER)
        self.assertEqual(self.dash.kpi_low.note_lbl.cget("text"), "need restocking")

        # Restock item: low stock count becomes '0', color is SUCCESS (green)
        self.services.inventory.update_product(self.p_low, "Stapler Pins", "Stationery", 20.0, 50, 10)
        self.dash.refresh_kpis()
        self.assertEqual(self.dash.kpi_low.value.cget("text"), "0")
        self.assertEqual(self.dash.kpi_low.value.cget("foreground"), theme.SUCCESS)
        self.assertEqual(self.dash.kpi_low.note_lbl.cget("text"), "all stocked")


if __name__ == "__main__":
    unittest.main()
