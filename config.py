"""Central configuration for the Smart Inventory & Billing Management System."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
INVOICE_DIR = os.path.join(BASE_DIR, "invoices")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# Shop details printed on every invoice (edit these for your shop)
SHOP_NAME = "Smart Mart"
SHOP_ADDRESS = "Dwarka, New Delhi - 110075"
SHOP_PHONE = "+91 00000 00000"

TAX_PERCENT = 5.0          # GST / tax applied to every bill (set 0 for no tax)
CURRENCY = "Rs."           # 'Rs.' is used because built-in PDF fonts have no rupee glyph
DEFAULT_LOW_STOCK = 5      # default low-stock threshold for new products
