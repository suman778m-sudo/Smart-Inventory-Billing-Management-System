"""Billing: create a sale, deduct stock atomically, and fetch sale details."""
from collections import defaultdict

import config


class BillingService:
    def __init__(self, conn):
        self.conn = conn

    def create_sale(self, user_id, customer_name, cart):
        """Save a sale for `cart` (list of CartItem) and reduce stock.

        Everything happens in one transaction: if any item has insufficient stock,
        nothing is saved. Prices are re-read from the database (never trusted from the UI).
        Returns the new sale id.
        """
        if not cart:
            raise ValueError("The cart is empty.")

        wanted = defaultdict(int)             # merge duplicate lines of the same product
        for item in cart:
            if int(item.quantity) <= 0:
                raise ValueError("Quantity must be at least 1.")
            wanted[item.product_id] += int(item.quantity)

        cur = self.conn.cursor()
        try:
            lines, subtotal = [], 0.0
            for pid, qty in wanted.items():
                row = cur.execute(
                    "SELECT name, price, quantity FROM products WHERE id=? AND active=1", (pid,)
                ).fetchone()
                if row is None:
                    raise ValueError("A product in the cart no longer exists.")
                name, price, stock = row
                if qty > stock:
                    raise ValueError(f"Insufficient stock for '{name}': only {stock} left.")
                lines.append((pid, qty, price))
                subtotal += price * qty

            subtotal = round(subtotal, 2)
            tax = round(subtotal * config.TAX_PERCENT / 100, 2)
            total = round(subtotal + tax, 2)

            cur.execute(
                "INSERT INTO sales(customer_name, subtotal, tax, total, user_id) VALUES (?, ?, ?, ?, ?)",
                ((customer_name or "").strip(), subtotal, tax, total, user_id),
            )
            sale_id = cur.lastrowid
            for pid, qty, price in lines:
                cur.execute(
                    "INSERT INTO sale_items(sale_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                    (sale_id, pid, qty, price),
                )
                cur.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (qty, pid))
            self.conn.commit()
            return sale_id
        except Exception:
            self.conn.rollback()
            raise

    def get_sale(self, sale_id):
        """Return a dict with sale header, cashier name and item lines (for invoices)."""
        head = self.conn.execute(
            "SELECT s.id, s.customer_name, s.subtotal, s.tax, s.total, s.sale_date, u.username "
            "FROM sales s JOIN users u ON u.id = s.user_id WHERE s.id=?",
            (sale_id,),
        ).fetchone()
        if head is None:
            raise ValueError("Sale not found.")
        items = self.conn.execute(
            "SELECT p.name, si.quantity, si.unit_price, si.quantity * si.unit_price "
            "FROM sale_items si JOIN products p ON p.id = si.product_id "
            "WHERE si.sale_id=? ORDER BY si.id",
            (sale_id,),
        ).fetchall()
        return {
            "id": head[0], "customer": head[1], "subtotal": head[2], "tax": head[3],
            "total": head[4], "date": head[5], "cashier": head[6],
            "items": [{"name": n, "qty": q, "price": p, "amount": round(a, 2)} for n, q, p, a in items],
        }

    def recent_sales(self, limit=50):
        return self.conn.execute(
            "SELECT s.id, s.sale_date, s.customer_name, s.total, u.username "
            "FROM sales s JOIN users u ON u.id = s.user_id ORDER BY s.id DESC LIMIT ?",
            (limit,),
        ).fetchall()
