"""Billing tab: build a cart, save the sale, reduce stock and create the PDF invoice."""
import tkinter as tk
from tkinter import messagebox, ttk

import config
from models import CartItem
from services.invoice_service import generate_invoice
from ui.theme import Card, font, make_table, row_tag, PRIMARY, SURFACE, MUTED
from utils import money, open_file


class BillingFrame(ttk.Frame):
    def __init__(self, master, services, user, on_change=None):
        super().__init__(master)
        self.services  = services
        self.user      = user
        self.on_change = on_change or (lambda: None)
        self.cart      = {}   # product_id -> CartItem

        self.columnconfigure(0, weight=1, uniform="half")
        self.columnconfigure(1, weight=1, uniform="half")
        self.rowconfigure(0, weight=1)

        # ══════════════ left: product picker ════════════════════════════════
        left = Card(self, title="🛍️  Select Products")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        lb = left.body

        # search bar
        bar = ttk.Frame(lb, style="Card.TFrame")
        bar.pack(fill="x", pady=(0, 12))
        tk.Label(bar, text="🔍", bg=SURFACE, font=(font()[0], 13)).pack(side="left", padx=(0, 6))
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.refresh())
        srch = ttk.Entry(bar, textvariable=self.search, font=font(10))
        srch.pack(side="left", fill="x", expand=True, ipady=3)
        ttk.Label(bar, text="Double-click to add", style="CardHint.TLabel").pack(side="right")

        box, self.products = make_table(lb, [
            ("name",  "PRODUCT",              160, "w"),
            ("price", f"PRICE ({config.CURRENCY})", 100, "e"),
            ("stock", "IN STOCK",              80, "center")])
        box.pack(fill="both", expand=True)
        self.products.bind("<Double-1>", lambda _e: self.add_to_cart())

        # quantity + add button
        add_bar = ttk.Frame(lb, style="Card.TFrame")
        add_bar.pack(fill="x", pady=(14, 0))
        ttk.Label(add_bar, text="Qty:", style="Field.TLabel").pack(side="left", padx=(0, 6))
        self.qty = tk.StringVar(value="1")
        ttk.Spinbox(add_bar, from_=1, to=9999, textvariable=self.qty,
                    width=6, font=font(10)).pack(side="left")
        tk.Button(add_bar, text="Add to Cart  →", command=self.add_to_cart,
                  bg=PRIMARY, fg="white", relief="flat", bd=0,
                  cursor="hand2", font=font(10, True), padx=16, pady=6,
                  activebackground="#4547d4", activeforeground="white",
                  highlightthickness=0).pack(side="right")

        # ══════════════ right: cart + bill ══════════════════════════════════
        right = Card(self, title="🧾  Cart & Bill")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        rb = right.body

        box, self.cart_tree = make_table(rb, [
            ("name",   "ITEM",   130, "w"),
            ("qty",    "QTY",     45, "center"),
            ("price",  "PRICE",   80, "e"),
            ("amount", "AMOUNT",  90, "e")])
        box.pack(fill="both", expand=True)

        cbar = ttk.Frame(rb, style="Card.TFrame")
        cbar.pack(fill="x", pady=(12, 0))
        ttk.Button(cbar, text="🗑 Remove selected", style="Danger.TButton",
                   command=self.remove_selected).pack(side="left")
        ttk.Button(cbar, text="Clear cart", command=self.clear_cart).pack(
            side="left", padx=8)

        # customer name
        cust = ttk.Frame(rb, style="Card.TFrame")
        cust.pack(fill="x", pady=(14, 0))
        ttk.Label(cust, text="CUSTOMER NAME  (optional)", style="Field.TLabel").pack(
            anchor="w", pady=(0, 4))
        self.customer = tk.StringVar()
        ttk.Entry(cust, textvariable=self.customer, font=font(10)).pack(
            fill="x", ipady=3)

        # totals panel
        totals = tk.Frame(rb, bg="#f0f4ff", padx=16, pady=14)
        totals.pack(fill="x", pady=(14, 0))

        self.lbl_sub, self.lbl_tax, self.lbl_total = (tk.StringVar() for _ in range(3))

        rows = [
            ("Subtotal",                    self.lbl_sub,   MUTED,   10, False),
            (f"Tax ({config.TAX_PERCENT:g}%)", self.lbl_tax, MUTED,  10, False),
            ("TOTAL",                       self.lbl_total, PRIMARY, 16, True),
        ]
        for r, (label, var, color, sz, bold) in enumerate(rows):
            tk.Label(totals, text=label, bg="#f0f4ff", fg=color,
                     font=font(sz, bold)).grid(row=r, column=0, sticky="w", pady=3)
            tk.Label(totals, textvariable=var, bg="#f0f4ff", fg=color,
                     font=font(sz, bold)).grid(row=r, column=1, sticky="e", pady=3)
        totals.columnconfigure(1, weight=1)

        # checkout button
        tk.Button(rb, text="✅  Generate Bill & Invoice",
                  command=self.checkout,
                  bg=PRIMARY, fg="white", relief="flat", bd=0,
                  cursor="hand2", font=font(12, True), pady=10,
                  activebackground="#4547d4", activeforeground="white",
                  highlightthickness=0).pack(fill="x", pady=(16, 0))

        self.refresh()
        self._update_totals()

    # ─────────────────────── product list ────────────────────────────────────
    def refresh(self):
        selected = self.products.selection()
        selected_id = selected[0] if selected else None
        self.products.delete(*self.products.get_children())
        for i, p in enumerate(self.services.inventory.list_products(self.search.get())):
            self.products.insert("", "end", iid=str(p.id), tags=row_tag(i, p.is_low_stock),
                                 values=(p.name, f"{p.price:,.2f}", p.quantity))
        if selected_id and self.products.exists(selected_id):
            self.products.selection_set(selected_id)
        for pid in list(self.cart):
            if self.services.inventory.get_product(pid) is None:
                del self.cart[pid]
        self._render_cart()

    # ─────────────────────── cart ────────────────────────────────────────────
    def _parse_qty(self):
        try:
            qty = int(self.qty.get())
        except ValueError:
            qty = 0
        if qty < 1:
            messagebox.showerror("Invalid quantity",
                                 "Quantity must be a whole number of at least 1.")
            return None
        return qty

    def add_to_cart(self):
        sel = self.products.selection()
        if not sel:
            messagebox.showinfo("Add to cart", "Select a product first.")
            return
        qty = self._parse_qty()
        if qty is None:
            return
        product = self.services.inventory.get_product(int(sel[0]))
        if product is None:
            return
        already = self.cart[product.id].quantity if product.id in self.cart else 0
        if already + qty > product.quantity:
            messagebox.showwarning(
                "Insufficient stock",
                f"Only {product.quantity} of '{product.name}' in stock "
                f"({already} already in the cart).")
            return
        if product.id in self.cart:
            self.cart[product.id].quantity += qty
        else:
            self.cart[product.id] = CartItem(product.id, product.name, product.price, qty)
        self.qty.set("1")
        self._render_cart()

    def remove_selected(self):
        sel = self.cart_tree.selection()
        if sel:
            self.cart.pop(int(sel[0]), None)
            self._render_cart()

    def clear_cart(self):
        self.cart.clear()
        self._render_cart()

    def _render_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        for i, item in enumerate(self.cart.values()):
            self.cart_tree.insert("", "end", iid=str(item.product_id), tags=row_tag(i),
                                  values=(item.name, item.quantity,
                                          f"{item.unit_price:,.2f}",
                                          f"{item.amount:,.2f}"))
        self._update_totals()

    def _update_totals(self):
        subtotal = round(sum(i.amount for i in self.cart.values()), 2)
        tax      = round(subtotal * config.TAX_PERCENT / 100, 2)
        self.lbl_sub.set(money(subtotal))
        self.lbl_tax.set(money(tax))
        self.lbl_total.set(money(round(subtotal + tax, 2)))

    # ─────────────────────── checkout ────────────────────────────────────────
    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Empty cart", "Add at least one product to the cart.")
            return
        bought = [i.product_id for i in self.cart.values()]
        try:
            sale_id = self.services.billing.create_sale(
                self.user.id, self.customer.get(), list(self.cart.values()))
        except ValueError as e:
            messagebox.showerror("Cannot create bill", str(e))
            self.refresh()
            return

        sale = self.services.billing.get_sale(sale_id)
        try:
            path = generate_invoice(sale)
        except Exception as e:
            messagebox.showerror("Invoice error",
                                 f"Bill #{sale_id} was saved, but the PDF failed:\n{e}")
            path = None

        low = [p for p in self.services.inventory.low_stock_products() if p.id in bought]
        self.cart.clear()
        self.customer.set("")
        self.refresh()
        self.on_change()

        if path and messagebox.askyesno(
                "Bill saved ✅",
                f"Bill #{sale_id} saved!\nTotal: {money(sale['total'])}\n\n"
                f"Invoice: {path}\n\nOpen the invoice now (to print)?"):
            try:
                open_file(path)
            except Exception as e:
                messagebox.showinfo("Open invoice", f"Could not open automatically:\n{e}")

        if low:
            messagebox.showwarning(
                "Low stock alert",
                "These items are now low on stock:\n\n" +
                "\n".join(f"  • {p.name}: {p.quantity} left" for p in low))
