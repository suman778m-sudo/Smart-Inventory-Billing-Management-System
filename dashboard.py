"""Main window after login: sidebar navigation + pages.

Redesigned sidebar with icons, animated hover, gradient brand header, and richer KPI cards.
"""
import tkinter as tk
from tkinter import messagebox, ttk

import config
from ui import theme
from ui.billing_frame  import BillingFrame
from ui.history_frame  import HistoryFrame
from ui.product_frame  import ProductFrame
from ui.report_frame   import ReportFrame
from ui.theme import (BG, DANGER, DANGER_DARK, DANGER_SOFT, INFO, INFO_SOFT,
                      PRIMARY, SIDEBAR, SIDEBAR_HOVER, SIDEBAR_TEXT,
                      SUCCESS, SUCCESS_SOFT, WARN, WARN_SOFT,
                      StatCard, font)
from ui.users_frame    import UsersFrame
from utils import money


# ─────────────────────────────── sidebar item ───────────────────────────────
class NavItem(tk.Frame):
    """Sidebar nav button: icon + label, with smooth hover and active states."""

    ACTIVE_BG  = "#222754"
    ACTIVE_FG  = "#ffffff"
    NORMAL_FG  = SIDEBAR_TEXT
    HOVER_BG   = "#1c2050"

    def __init__(self, master, icon, text, command):
        super().__init__(master, bg=SIDEBAR, cursor="hand2")
        self.command = command
        self.active  = False

        # left accent bar (hidden unless active)
        self.bar = tk.Frame(self, bg=SIDEBAR, width=4)
        self.bar.pack(side="left", fill="y")

        # icon
        self.icon_lbl = tk.Label(self, text=icon, bg=SIDEBAR, fg=SIDEBAR_TEXT,
                                 font=(theme.FONT_FAMILY, 15), padx=6, pady=10)
        self.icon_lbl.pack(side="left")

        # text
        self.label = tk.Label(self, text=text, bg=SIDEBAR, fg=SIDEBAR_TEXT,
                              anchor="w", font=font(11), padx=6, pady=10)
        self.label.pack(side="left", fill="x", expand=True)

        for w in (self, self.label, self.icon_lbl):
            w.bind("<Button-1>", lambda _e: self.command())
            w.bind("<Enter>",    lambda _e: self._paint(hover=True))
            w.bind("<Leave>",    lambda _e: self._paint(hover=False))

    def set_active(self, active):
        self.active = active
        self._paint()

    def _paint(self, hover=False):
        if self.active:
            bg, fg, bar_c = self.ACTIVE_BG, self.ACTIVE_FG, PRIMARY
            lf = font(11, True)
        elif hover:
            bg, fg, bar_c = self.HOVER_BG, "#d0d6f0", SIDEBAR
            lf = font(11)
        else:
            bg, fg, bar_c = SIDEBAR, self.NORMAL_FG, SIDEBAR
            lf = font(11)

        self.config(bg=bg)
        self.label.config(bg=bg, fg=fg, font=lf)
        self.icon_lbl.config(bg=bg, fg=fg)
        self.bar.config(bg=bar_c)


# ─────────────────────────────── main dashboard ─────────────────────────────
class Dashboard(ttk.Frame):
    def __init__(self, master, services, user, on_logout):
        super().__init__(master)
        self.services = services
        self.user      = user
        self.nav       = {}
        self.pages     = {}
        self.titles    = {}
        self.current_key = None

        # ═══════════════ sidebar ════════════════════════════════════════════
        side = tk.Frame(self, bg=SIDEBAR, width=240)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        # ── brand / logo ────────────────────────────────────────────────────
        brand_frame = tk.Frame(side, bg=SIDEBAR)
        brand_frame.pack(fill="x", padx=16, pady=(24, 18))

        logo = tk.Canvas(brand_frame, width=44, height=44,
                         bg=SIDEBAR, highlightthickness=0)
        logo.create_oval(1, 1, 43, 43, fill=PRIMARY, outline="")
        logo.create_text(22, 22, text=config.SHOP_NAME[:1].upper(),
                         fill="white", font=font(18, True))
        logo.pack(side="left")

        names = tk.Frame(brand_frame, bg=SIDEBAR)
        names.pack(side="left", padx=(12, 0))
        tk.Label(names, text=config.SHOP_NAME, bg=SIDEBAR, fg="white",
                 font=font(14, True)).pack(anchor="w")
        tk.Label(names, text="Inventory & Billing", bg=SIDEBAR, fg="#5b6180",
                 font=font(8)).pack(anchor="w")

        # ── section label ───────────────────────────────────────────────────
        sep = tk.Frame(side, bg="#252a55", height=1)
        sep.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(side, text="NAVIGATION", bg=SIDEBAR, fg="#3d4470",
                 font=font(7, True), anchor="w", padx=20).pack(fill="x", pady=(0, 4))

        self.nav_box = tk.Frame(side, bg=SIDEBAR)
        self.nav_box.pack(fill="x")

        # ── user card pinned at bottom ──────────────────────────────────────
        sep2 = tk.Frame(side, bg="#252a55", height=1)
        sep2.pack(side="bottom", fill="x", padx=16, pady=(0, 4))

        who = tk.Frame(side, bg=SIDEBAR_HOVER, padx=14, pady=14)
        who.pack(side="bottom", fill="x", padx=12, pady=(0, 16))

        av = tk.Canvas(who, width=38, height=38, bg=SIDEBAR_HOVER, highlightthickness=0)
        av.create_oval(1, 1, 37, 37, fill=PRIMARY, outline="")
        av.create_text(19, 19, text=user.username[:1].upper(),
                       fill="white", font=font(14, True))
        av.grid(row=0, column=0, rowspan=2)

        tk.Label(who, text=user.username, bg=SIDEBAR_HOVER, fg="white",
                 font=font(10, True), anchor="w").grid(
            row=0, column=1, sticky="w", padx=(12, 0))
        role_color = PRIMARY if user.is_admin else "#10b981"
        tk.Label(who, text=f"● {user.role}", bg=SIDEBAR_HOVER, fg=role_color,
                 font=font(8), anchor="w").grid(row=1, column=1, sticky="w", padx=(12, 0))

        logout_btn = tk.Button(who, text="⏻  Log out", command=on_logout,
                               bg="#2a2f5e", fg="#a5b4fc", relief="flat", bd=0,
                               cursor="hand2", font=font(9), padx=10, pady=5,
                               activebackground="#1e2245", activeforeground="white",
                               highlightthickness=0)
        logout_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        who.columnconfigure(1, weight=1)

        # ═══════════════ main content area ══════════════════════════════════
        main = ttk.Frame(self, padding=(28, 18, 28, 18))
        main.pack(side="left", fill="both", expand=True)

        # ── page header ─────────────────────────────────────────────────────
        head = ttk.Frame(main)
        head.pack(fill="x")
        self.title    = tk.StringVar()
        self.subtitle = tk.StringVar()

        hdr_left = ttk.Frame(head)
        hdr_left.pack(side="left", fill="x", expand=True)
        tk.Label(hdr_left, textvariable=self.title, bg=BG, fg=theme.TEXT,
                 font=font(22, True)).pack(anchor="w")
        tk.Label(hdr_left, textvariable=self.subtitle, bg=BG, fg=theme.MUTED,
                 font=font(10)).pack(anchor="w", pady=(2, 0))

        # ── KPI cards ───────────────────────────────────────────────────────
        kpis = ttk.Frame(main)
        kpis.pack(fill="x", pady=(16, 0))

        self.kpi_sales    = StatCard(kpis, "Today's Sales",    "💰", PRIMARY,     "#ededff")
        self.kpi_bills    = StatCard(kpis, "Bills Today",      "🧾", INFO,        INFO_SOFT)
        self.kpi_products = StatCard(kpis, "Products",         "📦", SUCCESS,     SUCCESS_SOFT)
        self.kpi_low      = StatCard(kpis, "Low Stock",        "⚠️", WARN,        WARN_SOFT)

        for i, card in enumerate((self.kpi_sales, self.kpi_bills,
                                   self.kpi_products, self.kpi_low)):
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            kpis.columnconfigure(i, weight=1, uniform="kpi")

        # ── low-stock banner ─────────────────────────────────────────────────
        self.banner_wrap  = tk.Frame(main, bg=BG)
        self.banner       = tk.Frame(self.banner_wrap, bg=DANGER_SOFT,
                                     padx=0, pady=0)
        self.banner.pack(fill="x", pady=(10, 0))

        tk.Frame(self.banner, bg=DANGER, width=5).pack(side="left", fill="y")
        self.banner_icon  = tk.Label(self.banner, text="⚠️ ", bg=DANGER_SOFT,
                                     fg=DANGER_DARK, font=(theme.FONT_FAMILY, 11))
        self.banner_icon.pack(side="left", padx=(10, 0), pady=8)
        self.banner_label = tk.Label(self.banner, text="", bg=DANGER_SOFT,
                                     fg=DANGER_DARK, anchor="w",
                                     pady=8, font=font(10, True))
        self.banner_label.pack(side="left", fill="x", expand=True)

        # ── page container ───────────────────────────────────────────────────
        self.stack = ttk.Frame(main)
        self.stack.pack(fill="both", expand=True, pady=(16, 0))
        self.stack.rowconfigure(0, weight=1)
        self.stack.columnconfigure(0, weight=1)

        # ── register pages ──────────────────────────────────────────────────
        self._add_page("billing",   "🧾", "Billing",
                       "New bill",
                       "Pick products, build the cart and print the invoice.",
                       BillingFrame(self.stack, services, user, on_change=self._data_changed))

        self._add_page("products",
                       "📦",
                       "Products" if user.is_admin else "Stock",
                       "Products" if user.is_admin else "Stock",
                       "Add, edit and track your inventory." if user.is_admin
                       else "Check what is available on the shelf.",
                       ProductFrame(self.stack, services,
                                    can_edit=user.is_admin,
                                    on_change=self._data_changed))

        self._add_page("history",   "🕘", "Bill History",
                       "Bill history", "Re-open any past invoice as a PDF.",
                       HistoryFrame(self.stack, services))

        if user.is_admin:
            self._add_page("reports", "📊", "Sales Reports",
                           "Sales reports",
                           "Revenue by day, week or month plus your best sellers.",
                           ReportFrame(self.stack, services))
            self._add_page("users",   "👥", "Users",
                           "Users", "Manage who can sign in to the system.",
                           UsersFrame(self.stack, services, user))

        self.refresh_kpis()
        self.show_page("billing")
        self.after(400, self._startup_alert)

    # ─────────────────────── navigation ─────────────────────────────────────
    def _add_page(self, key, icon, nav_text, title, subtitle, frame):
        item = NavItem(self.nav_box, icon, nav_text, lambda k=key: self.show_page(k))
        item.pack(fill="x", pady=1, padx=4)
        frame.grid(row=0, column=0, sticky="nsew")
        self.nav[key]    = item
        self.pages[key]  = frame
        self.titles[key] = (title, subtitle)

    def show_page(self, key):
        self.current_key = key
        for k, item in self.nav.items():
            item.set_active(k == key)
        self.title.set(self.titles[key][0])
        self.subtitle.set(self.titles[key][1])
        self.pages[key].tkraise()
        if hasattr(self.pages[key], "refresh"):
            self.pages[key].refresh()
        self.refresh_kpis()

    # ─────────────────────── KPIs & alert banner ─────────────────────────────
    def refresh_kpis(self):
        bills, total  = self.services.reports.today_summary()
        products      = self.services.inventory.list_products("")
        low           = self.services.inventory.low_stock_products()

        self.kpi_sales.set(money(total),     f"{bills} bill(s) today")
        self.kpi_bills.set(str(bills),       "transactions")
        self.kpi_products.set(str(len(products)), "in catalogue")
        self.kpi_low.set(str(len(low)),      "need restocking" if low else "all stocked")
        self.kpi_low.value.config(fg=DANGER if low else SUCCESS)

        self.refresh_banner(low)

    def refresh_banner(self, low=None):
        if low is None:
            low = self.services.inventory.low_stock_products()
        if low:
            names = ", ".join(f"{p.name} ({p.quantity})" for p in low[:6])
            more  = f"  +{len(low) - 6} more" if len(low) > 6 else ""
            self.banner_label.config(text=f"Low stock alert:  {names}{more}")
            self.banner_wrap.pack(fill="x", before=self.stack)
        else:
            self.banner_wrap.pack_forget()

    def _startup_alert(self):
        low = self.services.inventory.low_stock_products()
        if low:
            messagebox.showwarning(
                "Low stock alert",
                f"{len(low)} product(s) are running low on stock:\n\n" +
                "\n".join(f"  • {p.name}: {p.quantity} left" for p in low[:10]))

    def _data_changed(self):
        self.refresh_kpis()
