"""Unit tests for UsersFrame UI component."""
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
from ui.users_frame import UsersFrame


class TestUsersFrame(unittest.TestCase):
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
        self.staff = self.services.auth.authenticate("staff", "staff123")

        self.frame = UsersFrame(self.root, self.services, self.admin)
        self.frame.pack()

    def tearDown(self):
        self.frame.destroy()
        self.conn.close()

    def test_users_table_population(self):
        rows = self.frame.tree.get_children()
        self.assertEqual(len(rows), 2)

        admin_item = self.frame.tree.item(str(self.admin.id))["values"]
        self.assertEqual(admin_item[1], "admin")
        self.assertEqual(admin_item[2], "Admin")

        staff_item = self.frame.tree.item(str(self.staff.id))["values"]
        self.assertEqual(staff_item[1], "staff")
        self.assertEqual(staff_item[2], "Staff")

    def test_add_user_success(self):
        self.frame.username.set("cashier1")
        self.frame.password.set("cashierPass1")
        self.frame.role.set("Staff")

        self.frame.add()

        # Database and table verify
        new_user = self.services.auth.authenticate("cashier1", "cashierPass1")
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.role, "Staff")

        self.assertEqual(len(self.frame.tree.get_children()), 3)
        self.assertEqual(self.frame.username.get(), "")
        self.assertEqual(self.frame.password.get(), "")

    @patch("tkinter.messagebox.showerror")
    def test_add_user_validation_error(self, mock_err):
        self.frame.username.set("")
        self.frame.password.set("")
        self.frame.add()

        mock_err.assert_called_once()
        self.assertIn("Cannot create user", mock_err.call_args[0][0])

    @patch("tkinter.messagebox.showinfo")
    def test_delete_requires_selection(self, mock_info):
        self.frame.tree.selection_remove(self.frame.tree.selection())
        self.frame.delete()
        mock_info.assert_called_once()
        self.assertIn("Select a user first", mock_info.call_args[0][1])

    @patch("tkinter.messagebox.showwarning")
    def test_delete_own_user_prevented(self, mock_warn):
        self.frame.tree.selection_set(str(self.admin.id))
        self.frame.delete()

        mock_warn.assert_called_once()
        self.assertIn("cannot delete the account you are logged in with", mock_warn.call_args[0][1])
        # Admin should still exist
        user_ids = [u.id for u in self.services.auth.list_users()]
        self.assertIn(self.admin.id, user_ids)

    @patch("tkinter.messagebox.askyesno", return_value=True)
    def test_delete_other_user_success(self, mock_ask):
        self.frame.tree.selection_set(str(self.staff.id))
        self.frame.delete()

        user_ids = [u.id for u in self.services.auth.list_users()]
        self.assertNotIn(self.staff.id, user_ids)
        self.assertEqual(len(self.frame.tree.get_children()), 1)


if __name__ == "__main__":
    unittest.main()
