"""Unit tests for data models (User, Product, CartItem)."""
import unittest
from models import User, Product, CartItem


class TestModels(unittest.TestCase):
    def test_user_is_admin(self):
        admin = User(id=1, username="admin", role="Admin")
        staff = User(id=2, username="staff", role="Staff")
        self.assertTrue(admin.is_admin)
        self.assertFalse(staff.is_admin)

    def test_product_low_stock(self):
        normal_p = Product(id=1, name="Pen", category="Stationery", price=10.0, quantity=20, low_stock_threshold=5)
        low_p = Product(id=2, name="Notebook", category="Stationery", price=45.0, quantity=3, low_stock_threshold=5)
        self.assertFalse(normal_p.is_low_stock)
        self.assertTrue(low_p.is_low_stock)

    def test_cart_item_amount(self):
        item = CartItem(product_id=101, name="Rice 1kg", unit_price=95.0, quantity=3)
        self.assertEqual(item.amount, 285.0)


if __name__ == "__main__":
    unittest.main()
