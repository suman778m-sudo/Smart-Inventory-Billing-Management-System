"""Unit tests for InvoiceService."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.invoice_service import invoice_number, generate_invoice


class TestInvoiceService(unittest.TestCase):
    def test_invoice_number_format(self):
        self.assertEqual(invoice_number(1), "INV-00001")
        self.assertEqual(invoice_number(42), "INV-00042")
        self.assertEqual(invoice_number(10050), "INV-10050")

    def test_generate_invoice_pdf(self):
        sale_data = {
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

        with tempfile.TemporaryDirectory() as tmp_dir:
            pdf_path = generate_invoice(sale_data, out_dir=tmp_dir)
            self.assertTrue(os.path.exists(pdf_path))
            self.assertTrue(pdf_path.endswith("INV-00001.pdf"))
            # PDF file should have content
            self.assertGreater(os.path.getsize(pdf_path), 1000)

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
            self.assertGreater(os.path.getsize(pdf_path), 1000)


if __name__ == "__main__":
    unittest.main()
