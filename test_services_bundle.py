"""Unit tests for the Services bundle and integration."""
import os
import sys
import sqlite3
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from services import Services
from services.auth_service import AuthService
from services.inventory_service import InventoryService
from services.billing_service import BillingService
from services.report_service import ReportService


class TestServicesBundle(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        db.init_db(self.conn)
        self.services = Services(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_services_initialization(self):
        self.assertIsInstance(self.services.auth, AuthService)
        self.assertIsInstance(self.services.inventory, InventoryService)
        self.assertIsInstance(self.services.billing, BillingService)
        self.assertIsInstance(self.services.reports, ReportService)

        # All services must share the same connection
        self.assertIs(self.services.auth.conn, self.conn)
        self.assertIs(self.services.inventory.conn, self.conn)
        self.assertIs(self.services.billing.conn, self.conn)
        self.assertIs(self.services.reports.conn, self.conn)

    def test_integration_workflow(self):
        # 1. Setup users
        self.services.auth.ensure_default_users()
        admin = self.services.auth.authenticate("admin", "admin123")
        self.assertIsNotNone(admin)

        # 2. Add product
        pid = self.services.inventory.add_product("Notebook", "Stationery", 45.0, 50, 10)
        self.assertIsNotNone(pid)

        # 3. Process sale via billing
        from models import CartItem
        cart = [CartItem(pid, "Notebook", 45.0, 2)]
        sale_id = self.services.billing.create_sale(admin.id, "Demo Customer", cart)
        self.assertIsNotNone(sale_id)

        # 4. Verify stock reduction
        prod = self.services.inventory.get_product(pid)
        self.assertEqual(prod.quantity, 48)

        # 5. Verify report reflection
        bills, total = self.services.reports.today_summary()
        self.assertEqual(bills, 1)
        self.assertGreater(total, 0)


if __name__ == "__main__":
    unittest.main()
