"""Unit tests for UI Theme and reusable widgets."""
import os
import sys
import tkinter as tk
from tkinter import ttk
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui import theme


class TestTheme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()  # hide root window
            theme.apply_theme(cls.root)
        except Exception:
            cls.root = None

    @classmethod
    def tearDownClass(cls):
        if cls.root is not None:
            cls.root.destroy()

    def test_palette_constants(self):
        self.assertTrue(theme.BG.startswith("#"))
        self.assertTrue(theme.SURFACE.startswith("#"))
        self.assertTrue(theme.PRIMARY.startswith("#"))
        self.assertTrue(theme.SIDEBAR.startswith("#"))
        self.assertTrue(theme.SUCCESS.startswith("#"))
        self.assertTrue(theme.DANGER.startswith("#"))
        self.assertTrue(theme.WARN.startswith("#"))
        self.assertTrue(theme.INFO.startswith("#"))

    def test_font_helper(self):
        f = theme.font(12, bold=True, italic=False)
        self.assertEqual(len(f), 4)
        self.assertEqual(f[1], 12)
        self.assertEqual(f[2], "bold")
        self.assertEqual(f[3], "roman")

        f_italic = theme.font(9, bold=False, italic=True)
        self.assertEqual(f_italic[2], "normal")
        self.assertEqual(f_italic[3], "italic")

    def test_row_tag(self):
        self.assertEqual(theme.row_tag(0), ("even",))
        self.assertEqual(theme.row_tag(1), ("odd",))
        self.assertEqual(theme.row_tag(2), ("even",))
        self.assertEqual(theme.row_tag(0, low=True), ("low",))

    def test_card_widget(self):
        if self.root is None:
            self.skipTest("Tkinter display not available")
        card = theme.Card(self.root, title="Test Card")
        self.assertIsNotNone(card.body)
        card.destroy()

    def test_stat_card_widget(self):
        if self.root is None:
            self.skipTest("Tkinter display not available")
        stat = theme.StatCard(self.root, caption="Total Revenue", icon="💰", color=theme.PRIMARY)
        self.assertEqual(stat.value.cget("text"), "—")
        stat.set("Rs. 1,500.00", "Updated note")
        self.assertEqual(stat.value.cget("text"), "Rs. 1,500.00")
        self.assertEqual(stat.note_lbl.cget("text"), "Updated note")
        stat.destroy()

    def test_make_table(self):
        if self.root is None:
            self.skipTest("Tkinter display not available")
        cols = [
            ("id", "ID", 60, "center"),
            ("name", "Product Name", 180, "w"),
        ]
        frame, tree = theme.make_table(self.root, cols)
        self.assertIsInstance(tree, ttk.Treeview)
        frame.destroy()

    def test_rounded_button(self):
        if self.root is None:
            self.skipTest("Tkinter display not available")
        btn = theme.rounded_button(self.root, "Click Me", command=lambda: None)
        self.assertIsInstance(btn, tk.Button)
        self.assertEqual(btn.cget("text"), "Click Me")
        self.assertEqual(btn.cget("relief"), "flat")
        btn.destroy()

    def test_field_helper(self):
        if self.root is None:
            self.skipTest("Tkinter display not available")
        var = tk.StringVar()
        w = theme.field(self.root, "Item Name", 0, var=var)
        self.assertIsInstance(w, ttk.Entry)


if __name__ == "__main__":
    unittest.main()
