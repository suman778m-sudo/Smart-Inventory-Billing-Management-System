"""Product management and stock tracking."""
import sqlite3

import config
from models import Product

COLUMNS = "id, name, category, price, quantity, low_stock_threshold"


def _to_int(value):
    """Convert to int but refuse values like 1.5 instead of silently truncating them."""
    if isinstance(value, float) and not value.is_integer():
        raise ValueError("not a whole number")
    return int(value)


def _validate(name, price, quantity, threshold):
    name = (name or "").strip()
    if not name:
        raise ValueError("Product name is required.")
    try:
        price = float(price)
        quantity = _to_int(quantity)
        threshold = _to_int(threshold)
    except (TypeError, ValueError):
        raise ValueError("Price must be a number; quantity and threshold must be whole numbers.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    if quantity < 0 or threshold < 0:
        raise ValueError("Quantity and threshold cannot be negative.")
    return name, price, quantity, threshold


class InventoryService:
    def __init__(self, conn):
        self.conn = conn

    def add_product(self, name, category, price, quantity, threshold=config.DEFAULT_LOW_STOCK):
        name, price, quantity, threshold = _validate(name, price, quantity, threshold)
        try:
            cur = self.conn.execute(
                "INSERT INTO products(name, category, price, quantity, low_stock_threshold) "
                "VALUES (?, ?, ?, ?, ?)",
                (name, (category or "").strip(), price, quantity, threshold),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise ValueError(f"A product named '{name}' already exists.")

    def update_product(self, product_id, name, category, price, quantity, threshold):
        name, price, quantity, threshold = _validate(name, price, quantity, threshold)
        try:
            cur = self.conn.execute(
                "UPDATE products SET name=?, category=?, price=?, quantity=?, low_stock_threshold=? "
                "WHERE id=? AND active=1",
                (name, (category or "").strip(), price, quantity, threshold, product_id),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise ValueError(f"A product named '{name}' already exists.")
        if cur.rowcount == 0:
            raise ValueError("Product not found.")

    def delete_product(self, product_id):
        """Delete a product. If it appears in past sales it is deactivated instead
        so that old invoices and reports stay correct. Returns 'deleted' or 'deactivated'."""
        used = self.conn.execute(
            "SELECT 1 FROM sale_items WHERE product_id=? LIMIT 1", (product_id,)
        ).fetchone()
        if used:
            self.conn.execute("UPDATE products SET active=0 WHERE id=?", (product_id,))
            result = "deactivated"
        else:
            self.conn.execute("DELETE FROM products WHERE id=?", (product_id,))
            result = "deleted"
        self.conn.commit()
        return result

    def get_product(self, product_id):
        row = self.conn.execute(
            f"SELECT {COLUMNS} FROM products WHERE id=? AND active=1", (product_id,)
        ).fetchone()
        return Product(*row) if row else None

    def list_products(self, search=""):
        like = f"%{search.strip()}%"
        rows = self.conn.execute(
            f"SELECT {COLUMNS} FROM products WHERE active=1 AND (name LIKE ? OR category LIKE ?) "
            "ORDER BY name COLLATE NOCASE",
            (like, like),
        ).fetchall()
        return [Product(*r) for r in rows]

    def low_stock_products(self):
        rows = self.conn.execute(
            f"SELECT {COLUMNS} FROM products WHERE active=1 AND quantity <= low_stock_threshold "
            "ORDER BY quantity, name COLLATE NOCASE"
        ).fetchall()
        return [Product(*r) for r in rows]
