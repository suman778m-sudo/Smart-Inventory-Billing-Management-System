"""Plain data classes (the 'model' layer) used across services and UI."""
from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    role: str  # 'Admin' or 'Staff'

    @property
    def is_admin(self):
        return self.role == "Admin"


@dataclass
class Product:
    id: int
    name: str
    category: str
    price: float
    quantity: int
    low_stock_threshold: int

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold


@dataclass
class CartItem:
    product_id: int
    name: str
    unit_price: float
    quantity: int

    @property
    def amount(self):
        return round(self.unit_price * self.quantity, 2)
