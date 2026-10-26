"""Unit tests for the application entry point (main.py)."""
import os
import sys
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import db
from main import App, main
from services import Services
from ui.dashboard import Dashboard
from ui.login_window import LoginFrame


class TestApp(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)
        Services(self.conn).auth.ensure_default_users()

        try:
            self.app = App(self.conn)
            self.app.withdraw()  # headless for tests
        except Exception:
            self.app = None

    def tearDown(self):
        if self.app is not None:
            self.app.destroy()
        self.conn.close()

    def test_app_initialization(self):
        if self.app is None:
            self.skipTest("Tkinter display not available")

        # Window title should contain shop name
        self.assertIn(config.SHOP_NAME, self.app.title())

        # Services initialized
        self.assertIsInstance(self.app.services, Services)

        # Initial screen should be LoginFrame
        self.assertIsInstance(self.app.current, LoginFrame)

    def test_routing_to_dashboard_and_back(self):
        if self.app is None:
            self.skipTest("Tkinter display not available")

        admin_user = self.app.services.auth.authenticate("admin", "admin123")
        self.assertIsNotNone(admin_user)

        # Navigate to Dashboard
        self.app.show_dashboard(admin_user)
        self.assertIsInstance(self.app.current, Dashboard)
        self.assertEqual(self.app.current.user.username, "admin")

        # Navigate back to Login (Logout)
        self.app.show_login()
        self.assertIsInstance(self.app.current, LoginFrame)

    @patch("main.App")
    @patch("db.get_connection")
    @patch("db.init_db")
    def test_main_function_lifecycle(self, mock_init_db, mock_get_conn, mock_app_cls):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        main()

        # Check DB initialized
        mock_get_conn.assert_called_once()
        mock_init_db.assert_called_once_with(mock_conn)

        # Check App created and mainloop started
        mock_app_cls.assert_called_once_with(mock_conn)
        mock_app_instance.mainloop.assert_called_once()

        # Check connection closed on exit
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
