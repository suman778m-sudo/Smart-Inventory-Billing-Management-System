"""PDF invoice generation using ReportLab with professional layout styling."""
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, String

import config


def invoice_number(sale_id):
    """Format an integer sale ID into a standardized invoice code (INV-xxxxx)."""
    return f"INV-{sale_id:05d}"


def open_invoice(path):
    """Open an invoice PDF using the operating system's default PDF viewer."""
    from utils import open_file
    open_file(path)


def _build_shop_logo():
    """Return either a configured image logo or a modern vector logo badge."""
    logo_path = getattr(config, "LOGO_PATH", os.path.join(config.BASE_DIR, "logo.png"))
    if logo_path and os.path.exists(logo_path):
        try:
            return Image(logo_path, width=36 * mm, height=18 * mm)
        except Exception:
            pass

    # Stylish vector logo emblem badge
    badge = Drawing(44, 44)
    # Background rounded square
    badge.add(Rect(0, 0, 44, 44, rx=8, ry=8, fillColor=colors.HexColor("#16193a"), strokeColor=None))
    # Accent strip
    badge.add(Rect(6, 6, 32, 2.5, rx=1, ry=1, fillColor=colors.HexColor("#5b5ef4"), strokeColor=None))
    # Shop initials
    words = config.SHOP_NAME.split()
    initials = "".join(w[0].upper() for w in words[:2]) if words else "SM"
    badge.add(String(22, 14, initials, textAnchor="middle", fontName="Helvetica-Bold", fontSize=16, fillColor=colors.white))
    return badge


def generate_invoice(sale, out_dir=None):
    """Create a polished invoices/INV-xxxxx.pdf for a sale dict.

    Args:
        sale: dict with keys: 'id', 'customer', 'cashier', 'date', 'subtotal',
              'tax', 'total', and 'items' ([{'name', 'qty', 'price', 'amount'}]).
        out_dir: Optional output directory (defaults to config.INVOICE_DIR).

    Returns:
        Absolute or relative path to the generated PDF.
    """
    out_dir = out_dir or config.INVOICE_DIR
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{invoice_number(sale['id'])}.pdf")

    styles = getSampleStyleSheet()
    shop_name_style = ParagraphStyle(
        "ShopName", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=colors.HexColor("#16193a")
    )
    shop_sub_style = ParagraphStyle(
        "ShopSub", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=7.5, leading=10,
        textColor=colors.HexColor("#5b5ef4")
    )
    shop_meta_style = ParagraphStyle(
        "ShopMeta", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8, leading=11,
        textColor=colors.HexColor("#64748b")
    )

    inv_title_style = ParagraphStyle(
        "InvTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=17, leading=21,
        alignment=2, textColor=colors.HexColor("#16193a")
    )
    inv_meta_style = ParagraphStyle(
        "InvMeta", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12,
        alignment=2, textColor=colors.HexColor("#334155")
    )

    # 1. Header: Logo + Shop Details on left, Tax Invoice + Invoice Metadata on right
    logo_flowable = _build_shop_logo()
    shop_info = [
        Paragraph(f"<b>{escape(config.SHOP_NAME)}</b>", shop_name_style),
        Paragraph("SMART RETAIL &amp; INVENTORY MANAGEMENT", shop_sub_style),
        Spacer(1, 2),
        Paragraph(f"{escape(config.SHOP_ADDRESS)}<br/>Phone: {escape(config.SHOP_PHONE)}", shop_meta_style),
    ]

    header_left = Table([[logo_flowable, shop_info]], colWidths=[18 * mm, 87 * mm])
    header_left.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    header_right = [
        Paragraph("TAX INVOICE", inv_title_style),
        Spacer(1, 3),
        Paragraph(f"<b>Invoice #:</b> {escape(invoice_number(sale['id']))}", inv_meta_style),
        Paragraph(f"<b>Date:</b> {escape(sale['date'])}", inv_meta_style),
        Paragraph('<b>Payment Status:</b> <font color="#16a34a"><b>PAID</b></font>', inv_meta_style),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[105 * mm, 75 * mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    # 2. Customer & Transaction Information Box
    cust_display = sale["customer"] if sale.get("customer") else "Walk-in Customer"
    cashier_display = sale.get("cashier") or "System"

    meta_cell_left = Paragraph(
        f'<font color="#64748b" size="7.5"><b>BILLED TO</b></font><br/>'
        f'<font size="9.5" color="#0f172a"><b>{escape(cust_display)}</b></font><br/>'
        f'<font color="#64748b" size="8">Payment Mode: Counter / Cash</font>',
        ParagraphStyle("MetaLeft", parent=styles["Normal"], fontName="Helvetica", leading=12)
    )
    meta_cell_right = Paragraph(
        f'<font color="#64748b" size="7.5"><b>TRANSACTION DETAILS</b></font><br/>'
        f'<font size="8.5" color="#0f172a"><b>Cashier:</b> {escape(cashier_display)}</font><br/>'
        f'<font color="#64748b" size="8">POS Register: Terminal #01 (Main)</font>',
        ParagraphStyle("MetaRight", parent=styles["Normal"], fontName="Helvetica", leading=12)
    )

    meta_box = Table([[meta_cell_left, meta_cell_right]], colWidths=[90 * mm, 90 * mm])
    meta_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))

    # 3. Itemized Products Table
    cur = config.CURRENCY
    rows = [["#", "Item Description", "Qty", f"Price ({cur})", f"Amount ({cur})"]]
    for i, it in enumerate(sale["items"], 1):
        rows.append([i, it["name"], it["qty"], f"{it['price']:,.2f}", f"{it['amount']:,.2f}"])

    item_table = Table(rows, colWidths=[12 * mm, 80 * mm, 18 * mm, 35 * mm, 35 * mm], repeatRows=1)
    item_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16193a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    # 4. Styled Totals Table with Bold Grand Total Row
    totals_table = Table(
        [
            ["Subtotal:", f"{cur} {sale['subtotal']:,.2f}"],
            [f"Tax ({config.TAX_PERCENT:g}%):", f"{cur} {sale['tax']:,.2f}"],
            ["GRAND TOTAL:", f"{cur} {sale['total']:,.2f}"],
        ],
        colWidths=[115 * mm, 65 * mm],
    )
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, 1), 9.5),
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
        ("TEXTCOLOR", (0, 0), (-1, 1), colors.HexColor("#334155")),
        ("TOPPADDING", (0, 0), (-1, 1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 1), 4),
        ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#16193a")),
        ("TEXTCOLOR", (0, 2), (-1, 2), colors.white),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 2), (-1, 2), 11.5),
        ("TOPPADDING", (0, 2), (-1, 2), 7),
        ("BOTTOMPADDING", (0, 2), (-1, 2), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    # 5. Footer with Thank You Note and Return Policy
    footer_thankyou = Paragraph(
        "Thank you for shopping with us! We appreciate your business.",
        ParagraphStyle("FThx", parent=styles["Normal"], fontName="Helvetica-Bold",
                       fontSize=9.5, alignment=1, textColor=colors.HexColor("#16193a"))
    )
    footer_policy = Paragraph(
        "Return Policy: Eligible items in original condition may be returned or exchanged within 7 days with invoice intact.",
        ParagraphStyle("FPol", parent=styles["Normal"], fontName="Helvetica",
                       fontSize=8, alignment=1, textColor=colors.HexColor("#64748b"))
    )
    footer_legal = Paragraph(
        "This is a computer-generated tax invoice and requires no physical signature.",
        ParagraphStyle("FLegal", parent=styles["Normal"], fontName="Helvetica-Oblique",
                       fontSize=7.5, alignment=1, textColor=colors.HexColor("#94a3b8"))
    )

    story = [
        header_table,
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#5b5ef4"), spaceBefore=8, spaceAfter=8),
        meta_box,
        Spacer(1, 10),
        item_table,
        Spacer(1, 8),
        totals_table,
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#e2e8f0"), spaceBefore=18, spaceAfter=8),
        footer_thankyou,
        Spacer(1, 3),
        footer_policy,
        Spacer(1, 2),
        footer_legal,
    ]

    SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=invoice_number(sale["id"]),
    ).build(story)

    return path
