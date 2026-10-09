"""Database layer: connection helper and schema creation (SQLite)."""
import sqlite3

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash BLOB NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('Admin', 'Staff'))
);

CREATE TABLE IF NOT EXISTS products (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    category            TEXT DEFAULT '',
    price               REAL NOT NULL CHECK (price >= 0),
    quantity            INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    low_stock_threshold INTEGER NOT NULL DEFAULT 5 CHECK (low_stock_threshold >= 0),
    active              INTEGER NOT NULL DEFAULT 1
);

-- product names must be unique among active products
CREATE UNIQUE INDEX IF NOT EXISTS idx_products_name
    ON products(name COLLATE NOCASE) WHERE active = 1;

CREATE TABLE IF NOT EXISTS sales (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT DEFAULT '',
    subtotal      REAL NOT NULL,
    tax           REAL NOT NULL,
    total         REAL NOT NULL,
    sale_date     TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    user_id       INTEGER NOT NULL REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS sale_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id    INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL
);
"""


def get_connection(path=None):
    """Open a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(path or config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    """Create all tables if they do not exist yet."""
    conn.executescript(SCHEMA)
    conn.commit()
