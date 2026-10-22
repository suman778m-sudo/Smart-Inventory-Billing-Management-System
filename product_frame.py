"""Product management tab: add / update / delete products and track stock."""
import tkinter as tk
from tkinter import messagebox, ttk

import config
from ui.theme import Card, field, font, make_table, row_tag, PRIMARY, SURFACE, MUTED


class ProductFrame(ttk.Frame):
    def __init__(self, master, services, can_edit, on_change=None):
        super().__init__(master)
        self.services     = services
        self.can_edit     = can_edit
        self.on_change    = on_change or (lambda: None)
        self.selected_id  = None

        # ══════════ left: search + table ══════════════════════════════════
        left = Card(self, title="📦  Product Catalogue", padding=14)
        left.pack(side="left", fill="both", expand=True)
        lb = left.body

        # search bar
        bar = ttk.Frame(lb, style="Card.TFrame")
        bar.pack(fill="x", pady=(0, 12))
        tk.Label(bar, text="🔍", bg=SURFACE, font=(font()[0], 13)).pack(side="left", padx=(0, 6))
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(bar, textvariable=self.search, width=34, font=font(10)).pack(
            side="left", ipady=3)
        ttk.Label(bar, text="🔴 Red = low stock", style="CardHint.TLabel").pack(side="right")

        box, self.tree = make_table(lb, [
            ("id",       "ID",                   34, "center"),
            ("name",     "PRODUCT",             130, "w"),
            ("category", "CATEGORY",             95, "w"),
            ("price",    f"PRICE ({config.CURRENCY})", 100, "e"),
            ("qty",      "STOCK",                60, "center"),
            ("alert",    "ALERT AT",             60, "center"),
            ("status",   "STATUS",               70, "center"),
        ])
        box.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ══════════ right: form (admin) or view-only note ═════════════════
        if can_edit:
            card = Card(self, title="✏️  Product Details", padding=18)
            card.pack(side="left", fill="y", padx=(14, 0))
            form = ttk.Frame(card.body, style="Card.TFrame")
            form.pack(fill="both", expand=True)
            form.columnconfigure(0, weight=1)

            self.vars = {k: tk.StringVar()
                         for k in ("name", "category", "price", "qty", "threshold")}
            fields = [
                ("name",      "Product Name"),
                ("category",  "Category"),
                ("price",     f"Price ({config.CURRENCY})"),
                ("qty",       "Stock Quantity"),
                ("threshold", "Low-Stock Alert At"),
            ]
            for i, (key, label) in enumerate(fields):
                field(form, label, i, var=self.vars[key], width=26)
            self.vars["threshold"].set(str(config.DEFAULT_LOW_STOCK))

            # action buttons
            btns = ttk.Frame(form, style="Card.TFrame")
            btns.grid(row=12, column=0, pady=(22, 0), sticky="ew")

            _btn_cfg = dict(relief="flat", bd=0, cursor="hand2",
                            highlightthickness=0, pady=8)

            tk.Button(btns, text="➕ Add",    command=self.add,
                      bg=PRIMARY, fg="white",
                      activebackground="#4547d4", activeforeground="white",
                      font=font(10, True), **_btn_cfg).grid(
                row=0, column=0, sticky="ew", padx=(0, 4), pady=3)

            tk.Button(btns, text="✏️ Update", command=self.update,
                      bg="#f0f4ff", fg=PRIMARY,
                      activebackground="#dde3f0", activeforeground=PRIMARY,
                      font=font(10, True), **_btn_cfg).grid(
                row=0, column=1, sticky="ew", padx=(4, 0), pady=3)

            tk.Button(btns, text="🗑 Delete", command=self.delete,
                      bg="#fff0f0", fg="#ef4444",
                      activebackground="#fee2e2", activeforeground="#b91c1c",
                      font=font(10, True), **_btn_cfg).grid(
                row=1, column=0, sticky="ew", padx=(0, 4), pady=3)

            tk.Button(btns, text="✖ Clear",  command=self.clear_form,
                      bg="#f5f5f5", fg=MUTED,
                      activebackground="#e5e5e5", activeforeground=MUTED,
                      font=font(10, True), **_btn_cfg).grid(
                row=1, column=1, sticky="ew", padx=(4, 0), pady=3)

            btns.columnconfigure((0, 1), weight=1, uniform="b")

        else:
            note = Card(self, padding=20)
            note.pack(side="left", fill="y", padx=(14, 0))
            tk.Label(note.body, text="👁  View Only", bg=SURFACE, fg=PRIMARY,
                     font=font(13, True)).pack(anchor="w")
            tk.Label(note.body, text="Only admins can\nmanage products.",
                     bg=SURFACE, fg=MUTED, font=font(10),
                     justify="left").pack(anchor="w", pady=(6, 0))

        self.refresh()

    # ─────────────────────────── data ────────────────────────────────────────
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self.services.inventory.list_products(self.search.get())):
            self.tree.insert("", "end", iid=str(p.id),
                             tags=row_tag(i, p.is_low_stock),
                             values=(p.id, p.name, p.category,
                                     f"{p.price:,.2f}", p.quantity,
                                     p.low_stock_threshold,
                                     "⚠ LOW" if p.is_low_stock else "✔ OK"))
        if self.selected_id and self.tree.exists(str(self.selected_id)):
            self.tree.selection_set(str(self.selected_id))

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel or not self.can_edit:
            return
        p = self.services.inventory.get_product(int(sel[0]))
        if p is None:
            return
        self.selected_id = p.id
        for key, val in (("name", p.name), ("category", p.category),
                         ("price", p.price), ("qty", p.quantity),
                         ("threshold", p.low_stock_threshold)):
            self.vars[key].set(str(val))

    def clear_form(self):
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
        for key in self.vars:
            self.vars[key].set("")
        self.vars["threshold"].set(str(config.DEFAULT_LOW_STOCK))

    def _values(self):
        v = self.vars
        return (v["name"].get(), v["category"].get(), v["price"].get(),
                v["qty"].get(), v["threshold"].get())

    # ─────────────────────────── actions ─────────────────────────────────────
    def add(self):
        try:
            self.services.inventory.add_product(*self._values())
        except ValueError as e:
            messagebox.showerror("Cannot add product", str(e))
            return
        self.clear_form()
        self.refresh()
        self.on_change()

    def update(self):
        if not self.selected_id:
            messagebox.showinfo("Update", "Select a product from the table first.")
            return
        try:
            self.services.inventory.update_product(self.selected_id, *self._values())
        except ValueError as e:
            messagebox.showerror("Cannot update product", str(e))
            return
        self.refresh()
        self.on_change()

    def delete(self):
        if not self.selected_id:
            messagebox.showinfo("Delete", "Select a product from the table first.")
            return
        if not messagebox.askyesno("Delete product",
                                   "Delete the selected product?"):
            return
        result = self.services.inventory.delete_product(self.selected_id)
        if result == "deactivated":
            messagebox.showinfo(
                "Product removed",
                "This product appears in past bills, so it was hidden instead of erased "
                "(old invoices and reports stay correct).")
        self.clear_form()
        self.refresh()
        self.on_change()
