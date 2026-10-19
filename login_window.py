"""Login screen: animated brand panel on the left, polished sign-in form on the right."""
import tkinter as tk
from tkinter import messagebox, ttk

import config
from ui import theme
from ui.theme import PRIMARY, PRIMARY_SOFT, SURFACE, font, field

BRAND_BG     = "#16193a"     # deep navy (matches sidebar)
BRAND_ACCENT = "#5b5ef4"     # vivid indigo
BRAND_GLOW   = "#222754"     # slightly lighter navy for decorative circles
BRAND_TEXT   = "#a5b4fc"     # soft lavender text


class LoginFrame(ttk.Frame):
    def __init__(self, master, services, on_success):
        super().__init__(master)
        self.services  = services
        self.on_success = on_success

        self.columnconfigure(0, weight=55, uniform="cols")
        self.columnconfigure(1, weight=45, uniform="cols")
        self.rowconfigure(0, weight=1)

        self._build_brand_panel()
        self._build_form_panel()

    # ──────────────────────── left: brand panel ──────────────────────────────
    def _build_brand_panel(self):
        panel = tk.Canvas(self, bg=BRAND_BG, highlightthickness=0)
        panel.grid(row=0, column=0, sticky="nsew")

        # ── decorative animated circles ────────────────────────────────────
        def draw(_event=None):
            panel.delete("deco")
            w, h = panel.winfo_width(), panel.winfo_height()
            # large top-right glow
            panel.create_oval(w - 300, -180, w + 100, 220,
                              fill=BRAND_GLOW, outline="", tags="deco")
            # large bottom-left glow
            panel.create_oval(-150, h - 300, 250, h + 100,
                              fill=BRAND_GLOW, outline="", tags="deco")
            # small accent dots for texture
            for cx, cy, r, alpha in [(w * 0.8, h * 0.3, 6, "#4547d4"),
                                      (w * 0.15, h * 0.7, 8, "#4547d4"),
                                      (w * 0.6, h * 0.75, 4, "#7c3aed"),
                                      (w * 0.3, h * 0.15, 5, "#7c3aed")]:
                panel.create_oval(cx - r, cy - r, cx + r, cy + r,
                                  fill=alpha, outline="", tags="deco")
            panel.tag_lower("deco")

        content = tk.Frame(panel, bg=BRAND_BG)
        panel.create_window(0, 0, window=content, anchor="center", tags="content")
        panel.bind("<Configure>",
                   lambda e: (draw(), panel.coords("content", e.width / 2, e.height / 2)))

        # ── logo mark ─────────────────────────────────────────────────────
        logo_frame = tk.Frame(content, bg=BRAND_BG)
        logo_frame.pack(anchor="w", pady=(0, 6))

        logo = tk.Canvas(logo_frame, width=72, height=72,
                         bg=BRAND_BG, highlightthickness=0)
        logo.pack(side="left")
        # outer ring
        logo.create_oval(2, 2, 70, 70, fill=BRAND_ACCENT, outline="")
        # inner white circle
        logo.create_oval(16, 16, 56, 56, fill="#ffffff", outline="")
        # letter
        logo.create_text(36, 36, text=config.SHOP_NAME[:1].upper(),
                         fill=BRAND_ACCENT, font=font(22, True))

        tk.Label(content, text=config.SHOP_NAME, bg=BRAND_BG, fg="#ffffff",
                 font=font(36, True)).pack(anchor="w", pady=(12, 0))
        tk.Label(content, text="Inventory & Billing Management",
                 bg=BRAND_BG, fg=BRAND_TEXT,
                 font=font(13)).pack(anchor="w", pady=(4, 28))

        # ── feature list ──────────────────────────────────────────────────
        features = [
            ("🧾", "Fast billing with automatic PDF invoices"),
            ("📦", "Live stock tracking and low-stock alerts"),
            ("📊", "Daily, weekly & monthly sales reports"),
            ("👥", "Role-based access for admin & staff"),
        ]
        for icon, text in features:
            row = tk.Frame(content, bg=BRAND_BG)
            row.pack(anchor="w", pady=7)
            tk.Label(row, text=icon, bg=BRAND_BG, font=(theme.FONT_FAMILY, 13)).pack(side="left")
            tk.Label(row, text=f"  {text}", bg=BRAND_BG, fg="#e0e7ff",
                     font=font(11)).pack(side="left")

        # ── version badge ─────────────────────────────────────────────────
        badge = tk.Frame(content, bg="#1e2245", padx=14, pady=6)
        badge.pack(anchor="w", pady=(28, 0))
        tk.Label(badge, text="v2.0  •  Smart Mart POS", bg="#1e2245",
                 fg="#8b93b8", font=font(9)).pack()

    # ──────────────────────── right: login form ───────────────────────────────
    def _build_form_panel(self):
        side = tk.Frame(self, bg=SURFACE)
        side.grid(row=0, column=1, sticky="nsew")

        # centre the form vertically & horizontally
        form_wrap = tk.Frame(side, bg=SURFACE)
        form_wrap.place(relx=0.5, rely=0.5, anchor="center")

        # ── header ────────────────────────────────────────────────────────
        tk.Label(form_wrap, text="Welcome back 👋", bg=SURFACE, fg=theme.TEXT,
                 font=font(26, True)).pack(anchor="w")
        tk.Label(form_wrap, text="Sign in to continue to your dashboard",
                 bg=SURFACE, fg=theme.MUTED, font=font(11)).pack(anchor="w", pady=(4, 28))

        # ── fields ────────────────────────────────────────────────────────
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self._make_input(form_wrap, "👤  Username", self.username)
        self._make_input(form_wrap, "🔒  Password", self.password, show="•")

        # show-password toggle
        self.show_pw = tk.BooleanVar(value=False)
        chk_frame = tk.Frame(form_wrap, bg=SURFACE)
        chk_frame.pack(fill="x", pady=(6, 0))
        tk.Checkbutton(chk_frame, text="Show password",
                       variable=self.show_pw, bg=SURFACE,
                       fg=theme.MUTED, activebackground=SURFACE,
                       font=font(9), cursor="hand2",
                       command=self._toggle_pw,
                       selectcolor=SURFACE).pack(anchor="w")

        # ── sign-in button ────────────────────────────────────────────────
        btn = tk.Button(form_wrap, text="  Sign in  →",
                        command=self.login, bg=theme.PRIMARY, fg="#ffffff",
                        activebackground=theme.PRIMARY_DARK, activeforeground="#ffffff",
                        relief="flat", bd=0, cursor="hand2",
                        font=font(12, True), padx=24, pady=12,
                        highlightthickness=0)
        btn.pack(fill="x", pady=(22, 0))

        # ── demo credentials hint ─────────────────────────────────────────
        hint = tk.Frame(form_wrap, bg="#f0f4ff", padx=16, pady=14)
        hint.pack(fill="x", pady=(24, 0))
        tk.Label(hint, text="🔑  Demo credentials", bg="#f0f4ff", fg=theme.PRIMARY,
                 font=font(9, True)).pack(anchor="w")
        tk.Label(hint, text="admin / admin123     staff / staff123",
                 bg="#f0f4ff", fg=theme.MUTED, font=font(9)).pack(anchor="w", pady=(3, 0))

        # bind Enter key
        self._pw_entry.bind("<Return>", lambda _e: self.login())
        self._user_entry.bind("<Return>", lambda _e: self._pw_entry.focus_set())
        self._user_entry.focus_set()

    # ── helpers ────────────────────────────────────────────────────────────
    def _make_input(self, parent, label, var, show=None):
        """Create a labelled input with a bottom-border style."""
        tk.Label(parent, text=label, bg=SURFACE, fg=theme.MUTED,
                 font=font(9, True)).pack(anchor="w", pady=(0, 3))
        ent = ttk.Entry(parent, textvariable=var, show=show, width=34, font=font(11))
        ent.pack(fill="x", ipady=4, pady=(0, 14))
        if show:
            self._pw_entry = ent
        else:
            self._user_entry = ent
        return ent

    def _toggle_pw(self):
        self._pw_entry.config(show="" if self.show_pw.get() else "•")

    def login(self):
        user = self.services.auth.authenticate(
            self.username.get(), self.password.get())
        if user is None:
            messagebox.showerror("Login failed", "Invalid username or password.")
            self.password.set("")
            return
        self.on_success(user)
