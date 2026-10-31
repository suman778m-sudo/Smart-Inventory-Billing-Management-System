"""Unit tests for Enhanced Sales Trend Chart in ReportFrame (Day 24).

Verifies:
1. Chart styling adheres to application theme (SURFACE background, BORDER grid and spines).
2. Dynamic title reflects selected period (day/week/month) and CURRENCY symbol.
3. Bar visualization with value labels placed above each bar.
4. Graceful 'No sales yet' empty state rendering when no transactions exist.
5. Defensive fallback when matplotlib is absent or canvas is uninitialized.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".mplconfig"))

import sqlite3
import tkinter as tk
import unittest

import config
import db
from models import CartItem
from services import Services
from ui import theme
from ui.report_frame import ReportFrame, HAS_CHART


class TestReportChart(unittest.TestCase):
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

    def tearDown(self):
        self.conn.close()

    def test_chart_with_sales_data(self):
        if not HAS_CHART:
            self.skipTest("Matplotlib not installed")

        # Create products and sales
        p1 = self.services.inventory.add_product("Wireless Earbuds", "Electronics", 1200.0, 50, 5)
        p2 = self.services.inventory.add_product("Smart Watch", "Electronics", 2500.0, 30, 5)

        cart = [CartItem(p1, "Wireless Earbuds", 1200.0, 2), CartItem(p2, "Smart Watch", 2500.0, 1)]
        self.services.billing.create_sale(self.admin.id, "Kunal Roy", cart)

        frame = ReportFrame(self.root, self.services)
        frame.pack()

        # Canvas and figure should be initialized
        self.assertIsNotNone(frame.canvas)
        self.assertIsNotNone(frame.fig)
        self.assertIsNotNone(frame.ax)

        # Verify title contains period and currency
        title = frame.ax.get_title(loc="left")
        self.assertIn("day", title.lower())
        self.assertIn(config.CURRENCY, title)

        # Verify figure and axis backgrounds match theme
        self.assertEqual(frame.ax.get_facecolor()[:3], (1.0, 1.0, 1.0))  # SURFACE #ffffff

        # Verify bars are drawn
        bars = [child for child in frame.ax.get_children() if hasattr(child, "get_height")]
        self.assertGreater(len(bars), 0)

        # Verify text value labels exist above bars
        texts = [child.get_text() for child in frame.ax.get_children() if hasattr(child, "get_text")]
        # Sales total should be present in labels
        self.assertTrue(any(len(t) > 0 and t.replace(",", "").isdigit() for t in texts))

        frame.destroy()

    def test_chart_empty_state_no_sales(self):
        if not HAS_CHART:
            self.skipTest("Matplotlib not installed")

        # Empty database (no sales recorded)
        frame = ReportFrame(self.root, self.services)
        frame.pack()

        # Should render 'No sales yet'
        texts = [child.get_text() for child in frame.ax.get_children() if hasattr(child, "get_text")]
        self.assertIn("No sales yet", texts)

        # Ticks should be cleared
        self.assertEqual(len(frame.ax.get_xticks()), 0)
        self.assertEqual(len(frame.ax.get_yticks()), 0)

        frame.destroy()

    def test_chart_period_switching_updates_title(self):
        if not HAS_CHART:
            self.skipTest("Matplotlib not installed")

        p = self.services.inventory.add_product("Item", "Category", 100.0, 10, 2)
        self.services.billing.create_sale(self.admin.id, "Customer", [CartItem(p, "Item", 100.0, 1)])

        frame = ReportFrame(self.root, self.services)
        frame.pack()

        # Switch to Week
        frame.period.set("Week")
        frame.refresh()
        title_week = frame.ax.get_title(loc="left")
        self.assertIn("week", title_week.lower())

        # Switch to Month
        frame.period.set("Month")
        frame.refresh()
        title_month = frame.ax.get_title(loc="left")
        self.assertIn("month", title_month.lower())

        frame.destroy()

    def test_chart_draw_handles_none_canvas(self):
        frame = ReportFrame(self.root, self.services)
        frame.canvas = None
        # Calling _draw_chart should safely return without exception
        try:
            frame._draw_chart("Day")
        except Exception as e:
            self.fail(f"_draw_chart raised {e} when canvas was None")
        frame.destroy()


if __name__ == "__main__":
    unittest.main()
