"""Authentication and user management (role-based access: Admin / Staff)."""
import sqlite3

import bcrypt

from models import User

ROLES = ("Admin", "Staff")


class AuthService:
    def __init__(self, conn):
        self.conn = conn

    # ---------- helpers ----------
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # ---------- login ----------
    def authenticate(self, username, password):
        """Return a User if the credentials are valid, otherwise None."""
        row = self.conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
        if row and bcrypt.checkpw(password.encode("utf-8"), row[2]):
            return User(id=row[0], username=row[1], role=row[3])
        return None

    # ---------- user management ----------
    def create_user(self, username, password, role):
        username = username.strip()
        if not username:
            raise ValueError("Username is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
        if role not in ROLES:
            raise ValueError("Role must be Admin or Staff.")
        try:
            self.conn.execute(
                "INSERT INTO users(username, password_hash, role) VALUES (?, ?, ?)",
                (username, self.hash_password(password), role),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise ValueError(f"Username '{username}' already exists.")

    def list_users(self):
        rows = self.conn.execute("SELECT id, username, role FROM users ORDER BY username").fetchall()
        return [User(*r) for r in rows]

    def delete_user(self, user_id):
        role = self.conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
        if not role:
            raise ValueError("User not found.")
        if role[0] == "Admin":
            admins = self.conn.execute("SELECT COUNT(*) FROM users WHERE role='Admin'").fetchone()[0]
            if admins <= 1:
                raise ValueError("Cannot delete the last Admin account.")
        try:
            self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise ValueError("This user has recorded sales and cannot be deleted.")

    def ensure_default_users(self):
        """Create demo accounts on first run: admin/admin123 and staff/staff123."""
        count = self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count == 0:
            self.create_user("admin", "admin123", "Admin")
            self.create_user("staff", "staff123", "Staff")
