"""Sales reports tab (Admin only): day / week / month totals, chart, top products, CSV export."""
import os
import tkinter as tk
from tkinter import messagebox, ttk

import config
from services.report_service import PERIOD_FORMATS
from ui.theme import (BORDER, MUTED, PRIMARY, PRIMARY_DARK, PRIMARY_SOFT,
                      SURFACE, TEXT, Card, font, make_table, row_tag)
from utils import money

try:    # chart is optional; the tab still works if matplotlib is missing
    os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".mplconfig"))
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_CHART = True
except Exception:
    HAS_CHART = False


class ReportFrame(ttk.Frame):
    def __init__(self, master, services):
        super().__init__(master)
        self.services = services
        self.rows     = []

        # ── toolbar card ────────────────────────────────────────────────────
        tool = Card(self, padding=(14, 12))
        tool.pack(fill="x")
        bar = ttk.Frame(tool.body, style="Card.TFrame")
        bar.pack(fill="x")

        ttk.Label(bar, text="📅  Report by", style="Field.TLabel").pack(
            side="left", padx=(0, 10))

        self.period = tk.StringVar(value="Day")
        combo = ttk.Combobox(bar, textvariable=self.period,
                             values=list(PERIOD_FORMATS),
                             state="readonly", width=9, font=font(10))
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        ttk.Button(bar, text="🔄 Refresh", command=self.refresh).pack(
            side="left", padx=(14, 0))

        tk.Button(bar, text="📥 Export CSV", command=self.export,
                  bg=PRIMARY, fg="white", relief="flat", bd=0,
                  cursor="hand2", font=font(10, True), padx=14, pady=6,
                  activebackground="#4547d4", activeforeground="white",
                  highlightthickness=0).pack(side="left", padx=8)

        self.today = tk.StringVar()
        ttk.Label(bar, textvariable=self.today, style="Section.TLabel",
                  foreground=PRIMARY_DARK).pack(side="right")

        # ── body ────────────────────────────────────────────────────────────
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=(14, 0))
        body.columnconfigure(0, weight=3, uniform="r")
        body.columnconfigure(1, weight=2, uniform="r")
        body.rowconfigure(0, weight=1)

        # ── left column ──────────────────────────────────────────────────────
        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(0, weight=3)
        left.rowconfigure(1, weight=2)
        left.columnconfigure(0, weight=1)

        c1 = Card(left, title="📈  Sales Summary", padding=14)
        c1.grid(row=0, column=0, sticky="nsew")
        box, self.tree = make_table(c1.body, [
            ("label",    "PERIOD",               95, "center"),
            ("bills",    "BILLS",                50, "center"),
            ("items",    "ITEMS",                55, "center"),
            ("subtotal", "SUBTOTAL",             84, "e"),
            ("tax",      "TAX",                  60, "e"),
            ("total",    f"TOTAL ({config.CURRENCY})", 98, "e"),
        ], selectmode="none")
        box.pack(fill="both", expand=True)

        c2 = Card(left, title="🏆  Top Selling Products", padding=14)
        c2.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        box, self.top = make_table(c2.body, [
            ("name",    "PRODUCT",    180, "w"),
            ("sold",    "UNITS SOLD",  90, "center"),
            ("revenue", "REVENUE",    100, "e"),
        ], selectmode="none")
        box.pack(fill="both", expand=True)

        # ── right column: chart ──────────────────────────────────────────────
        self.canvas = None
        c3 = Card(body, title="📊  Sales Trend", padding=14)
        c3.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        if HAS_CHART:
            self.fig = Figure(figsize=(4.6, 3.6), dpi=100, facecolor=SURFACE)
            self.ax  = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=c3.body)
            self.canvas.get_tk_widget().configure(background=SURFACE,
                                                  highlightthickness=0)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            ttk.Label(c3.body,
                      text="Install matplotlib to see the chart.",
                      style="CardHint.TLabel").pack()

        self.refresh()

    def refresh(self):
        period    = self.period.get()
        self.rows = self.services.reports.sales_report(period)

        self.tree.delete(*self.tree.get_children())
        for i, (label, bills, items, sub, tax, total) in enumerate(self.rows):
            self.tree.insert("", "end", tags=row_tag(i),
                             values=(label, bills, items,
                                     f"{sub:,.2f}", f"{tax:,.2f}", f"{total:,.2f}"))

        bills, total = self.services.reports.today_summary()
        self.today.set(f"Today:  {bills} bill(s)   •   {money(total)}")

        self.top.delete(*self.top.get_children())
        for i, (name, sold, revenue) in enumerate(self.services.reports.top_products(5)):
            self.top.insert("", "end", tags=row_tag(i),
                            values=(name, sold, f"{revenue:,.2f}"))

        self._draw_chart(period)

    def _draw_chart(self, period):
        if not self.canvas:
            return
        data = list(reversed(self.rows[:10]))
        ax   = self.ax
        ax.clear()
        ax.set_facecolor(SURFACE)
        self.fig.patch.set_facecolor(SURFACE)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(BORDER)
        ax.tick_params(colors=MUTED, length=0, labelsize=8)

        if data:
            values = [r[5] for r in data]
            bars   = ax.bar(range(len(data)), values, width=0.55,
                            color=PRIMARY, zorder=3,
                            linewidth=0)
            # gradient-like: lighten top of bars
            for bar in bars:
                bar.set_alpha(0.88)
            ax.yaxis.grid(True, color=BORDER, linewidth=0.8, zorder=0)
            ax.set_axisbelow(True)
            top_v = max(values) or 1
            ax.set_ylim(0, top_v * 1.2)
            for bar, v in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        v + top_v * 0.02,
                        f"{v:,.0f}",
                        ha="center", va="bottom", fontsize=8, color=PRIMARY_DARK)
            ax.set_xlim(-0.8, max(len(data) - 1, 1) + 0.8)
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels([r[0] for r in data],
                               rotation=40, ha="right", fontsize=8)
        else:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.text(0.5, 0.5, "No sales yet", ha="center", va="center",
                    transform=ax.transAxes, color=MUTED, fontsize=12)

        ax.set_title(f"Sales by {period.lower()} ({config.CURRENCY})",
                     fontsize=10, color=MUTED, loc="left", pad=8)
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def export(self):
        if not self.rows:
            messagebox.showinfo("Export", "There is no data to export yet.")
            return
        path = self.services.reports.export_csv(self.rows, self.period.get())
        messagebox.showinfo("Export CSV ✅", f"Report saved to:\n{path}")
