"""Bill history tab: list past bills and reopen their PDF invoices."""
import tkinter as tk
from tkinter import messagebox, ttk

import config
from services.invoice_service import generate_invoice, invoice_number
from ui.theme import Card, font, make_table, row_tag, PRIMARY, SURFACE
from utils import open_file


class HistoryFrame(ttk.Frame):
    def __init__(self, master, services):
        super().__init__(master)
        self.services = services

        card = Card(self, title="🕘  Recent Bills", padding=14)
        card.pack(fill="both", expand=True)
        body = card.body

        # toolbar
        bar = ttk.Frame(body, style="Card.TFrame")
        bar.pack(fill="x", pady=(0, 12))

        tk.Button(bar, text="📄  Open Invoice PDF",
                  command=self.open_invoice,
                  bg=PRIMARY, fg="white", relief="flat", bd=0,
                  cursor="hand2", font=font(10, True), padx=16, pady=7,
                  activebackground="#4547d4", activeforeground="white",
                  highlightthickness=0).pack(side="left")

        ttk.Label(bar,
                  text="Select a bill then click Open  •  showing last 50 bills",
                  style="CardHint.TLabel").pack(side="left", padx=14)

        # table
        box, self.tree = make_table(body, [
            ("inv",      "INVOICE",              100, "center"),
            ("date",     "DATE & TIME",          160, "center"),
            ("customer", "CUSTOMER",             220, "w"),
            ("total",    f"TOTAL ({config.CURRENCY})", 120, "e"),
            ("cashier",  "CASHIER",              120, "center"),
        ])
        box.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self.open_invoice())
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, (sid, date, customer, total, cashier) in enumerate(
                self.services.billing.recent_sales(50)):
            self.tree.insert("", "end", iid=str(sid), tags=row_tag(i),
                             values=(invoice_number(sid), date,
                                     customer or "Walk-in",
                                     f"{total:,.2f}", cashier))

    def open_invoice(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Invoice", "Select a bill first.")
            return
        try:
            path = generate_invoice(self.services.billing.get_sale(int(sel[0])))
            open_file(path)
        except Exception as e:
            messagebox.showerror("Invoice", f"Could not open the invoice:\n{e}")
