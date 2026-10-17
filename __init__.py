"""Service layer: business logic, independent of the UI."""
from services.auth_service import AuthService
from services.billing_service import BillingService
from services.inventory_service import InventoryService
from services.report_service import ReportService


class Services:
    """Bundles all services around one database connection so the UI can receive a single object."""

    def __init__(self, conn):
        self.conn = conn
        self.auth = AuthService(conn)
        self.inventory = InventoryService(conn)
        self.billing = BillingService(conn)
        self.reports = ReportService(conn)
