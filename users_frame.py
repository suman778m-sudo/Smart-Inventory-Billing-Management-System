"""User management tab (Admin only): add and remove Admin / Staff accounts."""
import tkinter as tk
from tkinter import messagebox, ttk

from services.auth_service import ROLES
from ui.theme import Card, field, font, make_table, row_tag, PRIMARY, MUTED, SURFACE


class UsersFrame(ttk.Frame):
    def __init__(self, master, services, current_user):
        super().__init__(master)
        self.services     = services
        self.current_user = current_user

        # ── left: user table ────────────────────────────────────────────────
        left = Card(self, title="👥  System Users", padding=14)
        left.pack(side="left", fill="both", expand=True)
        box, self.tree = make_table(left.body, [
            ("id",       "ID",        50, "center"),
            ("username", "USERNAME", 200, "w"),
            ("role",     "ROLE",     100, "center"),
        ])
        box.pack(fill="both", expand=True)

        # ── right: add-user form ─────────────────────────────────────────────
        card = Card(self, title="➕  Add User", padding=18)
        card.pack(side="left", fill="y", padx=(14, 0))

        form = ttk.Frame(card.body, style="Card.TFrame")
        form.pack(fill="both", expand=True)
        form.columnconfigure(0, weight=1)

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.role     = tk.StringVar(value="Staff")

        field(form, "Username", 0, var=self.username, width=26)
        field(form, "Password", 1, var=self.password, show="•", width=26)
        field(form, "Role",     2,
              widget=ttk.Combobox(form, textvariable=self.role,
                                  values=ROLES, state="readonly", width=24,
                                  font=font(10)))

        _btn_cfg = dict(relief="flat", bd=0, cursor="hand2",
                        highlightthickness=0, pady=9, font=font(10, True))

        tk.Button(form, text="✅  Create User", command=self.add,
                  bg=PRIMARY, fg="white",
                  activebackground="#4547d4", activeforeground="white",
                  **_btn_cfg).grid(row=8, column=0, sticky="ew", pady=(22, 6))

        tk.Button(form, text="🗑  Delete Selected", command=self.delete,
                  bg="#fff0f0", fg="#ef4444",
                  activebackground="#fee2e2", activeforeground="#b91c1c",
                  **_btn_cfg).grid(row=9, column=0, sticky="ew")

        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, u in enumerate(self.services.auth.list_users()):
            self.tree.insert("", "end", iid=str(u.id), tags=row_tag(i),
                             values=(u.id, u.username, u.role))

    def add(self):
        try:
            self.services.auth.create_user(
                self.username.get(), self.password.get(), self.role.get())
        except ValueError as e:
            messagebox.showerror("Cannot create user", str(e))
            return
        self.username.set("")
        self.password.set("")
        self.refresh()

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a user first.")
            return
        if int(sel[0]) == self.current_user.id:
            messagebox.showwarning("Delete",
                                   "You cannot delete the account you are logged in with.")
            return
        if not messagebox.askyesno("Delete user", "Delete the selected user?"):
            return
        try:
            self.services.auth.delete_user(int(sel[0]))
        except ValueError as e:
            messagebox.showerror("Cannot delete user", str(e))
            return
        self.refresh()
