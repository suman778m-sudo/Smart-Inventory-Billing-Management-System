"""Unit tests for utility helpers."""
import unittest
from utils import money
import config


class TestUtils(unittest.TestCase):
    def test_money_formatting(self):
        self.assertEqual(money(100), f"{config.CURRENCY} 100.00")
        self.assertEqual(money(1234.5), f"{config.CURRENCY} 1,234.50")
        self.assertEqual(money(0), f"{config.CURRENCY} 0.00")
        self.assertEqual(money(99.99), f"{config.CURRENCY} 99.99")


if __name__ == "__main__":
    unittest.main()
