"""Unit tests for AuthService."""
import sqlite3
import unittest
import db
from services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)
        self.auth = AuthService(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_and_authenticate_user(self):
        self.auth.create_user("testuser", "securepass123", "Staff")
        user = self.auth.authenticate("testuser", "securepass123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "Staff")
        self.assertFalse(user.is_admin)

    def test_authenticate_invalid_password(self):
        self.auth.create_user("testuser", "securepass123", "Staff")
        user = self.auth.authenticate("testuser", "wrongpassword")
        self.assertIsNone(user)

    def test_duplicate_username_fails(self):
        self.auth.create_user("john", "password123", "Staff")
        with self.assertRaises(ValueError):
            self.auth.create_user("john", "password456", "Admin")

    def test_short_password_fails(self):
        with self.assertRaises(ValueError):
            self.auth.create_user("shortpw", "123", "Staff")

    def test_ensure_default_users(self):
        self.auth.ensure_default_users()
        admin = self.auth.authenticate("admin", "admin123")
        staff = self.auth.authenticate("staff", "staff123")
        self.assertIsNotNone(admin)
        self.assertIsNotNone(staff)
        self.assertTrue(admin.is_admin)
        self.assertFalse(staff.is_admin)


if __name__ == "__main__":
    unittest.main()
