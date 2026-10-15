"""Sales reports (day / week / month), top products and CSV export."""
import csv
import os

import config

PERIOD_FORMATS = {"Day": "%Y-%m-%d", "Week": "%Y-W%W", "Month": "%Y-%m"}


class ReportService:
    def __init__(self, conn):
        self.conn = conn

    def sales_report(self, period="Day"):
        """Rows of (period_label, bills, items_sold, subtotal, tax, total), newest first."""
        if period not in PERIOD_FORMATS:
            raise ValueError("Period must be Day, Week or Month.")
        fmt = PERIOD_FORMATS[period]
        # bill totals and item counts are aggregated separately to avoid double counting
        heads = self.conn.execute(
            "SELECT strftime(?, sale_date) AS label, COUNT(*), SUM(subtotal), SUM(tax), SUM(total) "
            "FROM sales GROUP BY label ORDER BY label DESC",
            (fmt,),
        ).fetchall()
        items = dict(self.conn.execute(
            "SELECT strftime(?, s.sale_date) AS label, SUM(si.quantity) "
            "FROM sales s JOIN sale_items si ON si.sale_id = s.id GROUP BY label",
            (fmt,),
        ).fetchall())
        return [(l, n, items.get(l, 0), round(sub, 2), round(tax, 2), round(tot, 2))
                for l, n, sub, tax, tot in heads]

    def today_summary(self):
        """(bills, total) for today."""
        row = self.conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(total), 0) FROM sales "
            "WHERE date(sale_date) = date('now', 'localtime')"
        ).fetchone()
        return row[0], round(row[1], 2)

    def top_products(self, limit=5):
        return self.conn.execute(
            "SELECT p.name, SUM(si.quantity) AS sold, ROUND(SUM(si.quantity * si.unit_price), 2) "
            "FROM sale_items si JOIN products p ON p.id = si.product_id "
            "GROUP BY p.id ORDER BY sold DESC, p.name LIMIT ?",
            (limit,),
        ).fetchall()

    @staticmethod
    def export_csv(rows, period, path=None):
        os.makedirs(config.EXPORT_DIR, exist_ok=True)
        path = path or os.path.join(config.EXPORT_DIR, f"sales_report_{period.lower()}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([period, "Bills", "Items sold", "Subtotal", "Tax", "Total"])
            w.writerows(rows)
        return path
