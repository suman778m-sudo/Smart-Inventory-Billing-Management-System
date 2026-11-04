"""Smart Inventory & Billing Management System — entry point.

Run:  python main.py
"""
import os
import tkinter as tk

import config
import db
from services import Services
from ui.dashboard import Dashboard
from ui.login_window import LoginFrame
from ui.theme import apply_theme


def compute_window_geometry(sw, sh):
    """Compute optimal window dimensions (w, h, x, y) ensuring smooth fit on 1366x768 up to 4K."""
    target_w = min(1300, max(1080, sw - 40))
    target_h = min(800, max(660, sh - 90))
    w = min(target_w, sw)
    h = min(target_h, sh)
    x = max(0, (sw - w) // 2)
    y = max(0, (sh - h) // 2)
    return w, h, x, y


class App(tk.Tk):
    def __init__(self, conn):
        super().__init__()
        self.title(f"{config.SHOP_NAME}  —  Inventory & Billing Management")

        # ── window sizing: fit any screen (optimized for 1366×768 laptops) ───
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h, x, y = compute_window_geometry(sw, sh)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(1050, 640)

        # ── apply the new theme ───────────────────────────────────────────────
        apply_theme(self)

        # ── set a nice window icon (plain coloured canvas) ───────────────────
        try:
            ico = tk.PhotoImage(width=32, height=32)
            # simple coloured icon using put() — no external file needed
            for row in range(32):
                for col in range(32):
                    r = (row - 16) ** 2 + (col - 16) ** 2
                    if r < 196:        # circle
                        ico.put("#5b5ef4", (col, row))
                    else:
                        ico.put("#f0f4ff", (col, row))
            self.iconphoto(True, ico)
        except Exception:
            pass   # icon is cosmetic only; silently skip if it fails

        self.services = Services(conn)
        self.current  = None
        self.show_login()

    def _swap(self, frame):
        if self.current is not None:
            self.current.destroy()
        self.current = frame
        frame.pack(fill="both", expand=True)

    def show_login(self):
        self._swap(LoginFrame(self, self.services, self.show_dashboard))

    def show_dashboard(self, user):
        self._swap(Dashboard(self, self.services, user, on_logout=self.show_login))


def main():
    os.makedirs(config.INVOICE_DIR, exist_ok=True)
    conn = db.get_connection()
    db.init_db(conn)
    Services(conn).auth.ensure_default_users()   # creates admin/staff on first run
    App(conn).mainloop()
    conn.close()


if __name__ == "__main__":
    main()
