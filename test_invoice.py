"""Unit tests for InvoiceService and Day 25 PDF layout polish."""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from services.invoice_service import (
    _build_shop_logo,
    generate_invoice,
    invoice_number,
    open_invoice,
)


class TestInvoiceService(unittest.TestCase):
    def setUp(self):
        self.sample_sale = {
            "id": 1,
            "customer": "Rohan Gupta",
            "cashier": "staff",
            "date": "2026-10-16 14:30:00",
            "subtotal": 150.0,
            "tax": 7.5,
            "total": 157.5,
            "items": [
                {"name": "Notebook A4", "qty": 2, "price": 50.0, "amount": 100.0},
                {"name": "Ball Pen (Blue)", "qty": 5, "price": 10.0, "amount": 50.0},
            ],
        }

    def test_invoice_number_format(self):
        self.assertEqual(invoice_number(1), "INV-00001")
        self.assertEqual(invoice_number(42), "INV-00042")
        self.assertEqual(invoice_number(10050), "INV-10050")

    def test_generate_invoice_pdf(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pdf_path = generate_invoice(self.sample_sale, out_dir=tmp_dir)
            self.assertTrue(os.path.exists(pdf_path))
            self.assertTrue(pdf_path.endswith("INV-00001.pdf"))
            # PDF file should have substantial content
            self.assertGreater(os.path.getsize(pdf_path), 2000)

    def test_generate_invoice_walk_in_customer(self):
        sale_data = {
            "id": 2,
            "customer": "",  # walk-in customer test
            "cashier": "admin",
            "date": "2026-10-16 15:00:00",
            "subtotal": 20.0,
            "tax": 1.0,
            "total": 21.0,
            "items": [
                {"name": "Mineral Water 1L", "qty": 1, "price": 20.0, "amount": 20.0},
            ],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            pdf_path = generate_invoice(sale_data, out_dir=tmp_dir)
            self.assertTrue(os.path.exists(pdf_path))
            self.assertTrue(pdf_path.endswith("INV-00002.pdf"))
            self.assertGreater(os.path.getsize(pdf_path), 2000)

    def test_build_shop_logo_badge_default(self):
        """Verify vector logo badge generated with initials when no image file configured."""
        badge = _build_shop_logo()
        self.assertIsNotNone(badge)
        self.assertEqual(badge.width, 44)
        self.assertEqual(badge.height, 44)

    def test_build_shop_logo_with_custom_image(self):
        """Verify custom image logo is loaded when file exists."""
        from reportlab.platypus import Image as RLImage

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_name = tmp.name
            # Write a minimal 1x1 valid PNG
            tmp.write(
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\x9f"
                b"\x01\x01\x00\x00\xff\xff\x02\xfe\x01\xdb\x9e\x9fK\x00\x00\x00\x00IEND\xaeB`\x82"
            )

        try:
            with patch.object(config, "LOGO_PATH", tmp_name):
                logo = _build_shop_logo()
                self.assertIsInstance(logo, RLImage)
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

    @patch("utils.open_file")
    def test_open_invoice_delegates_to_utils(self, mock_open):
        """Verify open_invoice calls utils.open_file."""
        test_path = "invoices/INV-00001.pdf"
        open_invoice(test_path)
        mock_open.assert_called_once_with(test_path)

    @patch("os.startfile", create=True)
    def test_utils_open_file_on_windows(self, mock_startfile):
        """Verify utils.open_file calls os.startfile on Windows systems."""
        import utils
        with patch.object(sys, "platform", "win32"):
            utils.open_file("invoices/INV-00001.pdf")
            mock_startfile.assert_called_once_with("invoices/INV-00001.pdf")


if __name__ == "__main__":
    unittest.main()
