"""Unit tests for LoginFrame UI component."""
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
from ui.login_window import LoginFrame


class TestLoginWindow(unittest.TestCase):
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

        self.logged_in_user = None

        def on_success(user):
            self.logged_in_user = user

        self.frame = LoginFrame(self.root, self.services, on_success)
        self.frame.pack()

    def tearDown(self):
        self.frame.destroy()
        self.conn.close()

    def test_login_success_admin(self):
        self.frame.username.set("admin")
        self.frame.password.set("admin123")
        self.frame.login()

        self.assertIsNotNone(self.logged_in_user)
        self.assertEqual(self.logged_in_user.username, "admin")
        self.assertTrue(self.logged_in_user.is_admin)

    def test_login_success_staff(self):
        self.frame.username.set("staff")
        self.frame.password.set("staff123")
        self.frame.login()

        self.assertIsNotNone(self.logged_in_user)
        self.assertEqual(self.logged_in_user.username, "staff")
        self.assertFalse(self.logged_in_user.is_admin)

    @patch("tkinter.messagebox.showerror")
    def test_login_failure_bad_password(self, mock_error):
        self.frame.username.set("admin")
        self.frame.password.set("wrongpassword")
        self.frame.login()

        self.assertIsNone(self.logged_in_user)
        mock_error.assert_called_once()
        self.assertEqual(self.frame.password.get(), "")

    def test_toggle_show_password(self):
        self.frame.show_pw.set(True)
        self.frame._toggle_pw()
        self.assertEqual(self.frame._pw_entry.cget("show"), "")

        self.frame.show_pw.set(False)
        self.frame._toggle_pw()
        self.assertEqual(self.frame._pw_entry.cget("show"), "•")


if __name__ == "__main__":
    unittest.main()
