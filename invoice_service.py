"""PDF invoice generation using ReportLab."""
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import config


def invoice_number(sale_id):
    return f"INV-{sale_id:05d}"


def generate_invoice(sale, out_dir=None):
    """Create invoices/INV-xxxxx.pdf for a sale dict (from BillingService.get_sale)."""
    out_dir = out_dir or config.INVOICE_DIR
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{invoice_number(sale['id'])}.pdf")

    styles = getSampleStyleSheet()
    shop = ParagraphStyle("shop", parent=styles["Title"], fontSize=22, spaceAfter=2)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9, alignment=1,
                           textColor=colors.HexColor("#555555"))
    heading = ParagraphStyle("heading", parent=styles["Heading2"], alignment=1, spaceBefore=8)
    cur = config.CURRENCY

    story = [
        Paragraph(escape(config.SHOP_NAME), shop),
        Paragraph(escape(f"{config.SHOP_ADDRESS}  |  {config.SHOP_PHONE}"), small),
        Paragraph("TAX INVOICE", heading),
        Spacer(1, 6),
    ]

    meta = Table(
        [
            ["Invoice No:", invoice_number(sale["id"]), "Date:", sale["date"]],
            ["Customer:", sale["customer"] or "Walk-in customer", "Cashier:", sale["cashier"]],
        ],
        colWidths=[26 * mm, 62 * mm, 22 * mm, 60 * mm],
    )
    meta.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story += [meta, Spacer(1, 10)]

    rows = [["#", "Item", "Qty", f"Price ({cur})", f"Amount ({cur})"]]
    for i, it in enumerate(sale["items"], 1):
        rows.append([i, it["name"], it["qty"], f"{it['price']:,.2f}", f"{it['amount']:,.2f}"])
    table = Table(rows, colWidths=[10 * mm, 82 * mm, 16 * mm, 36 * mm, 36 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5fa")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c8d0dc")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [table, Spacer(1, 8)]

    totals = Table(
        [
            ["Subtotal:", f"{cur} {sale['subtotal']:,.2f}"],
            [f"Tax ({config.TAX_PERCENT:g}%):", f"{cur} {sale['tax']:,.2f}"],
            ["TOTAL:", f"{cur} {sale['total']:,.2f}"],
        ],
        colWidths=[120 * mm, 60 * mm],
    )
    totals.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 12),
        ("LINEABOVE", (1, -1), (1, -1), 0.8, colors.black),
    ]))
    story += [totals, Spacer(1, 24), Paragraph("Thank you for your purchase!", small)]

    SimpleDocTemplate(
        path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm, title=invoice_number(sale["id"]),
    ).build(story)
    return path
