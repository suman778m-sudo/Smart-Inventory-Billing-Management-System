"""Visual theme for the whole app: colours, fonts, ttk styles and reusable widgets.

Every screen imports its colours and helpers from here. Edit the palette below to
restyle the entire application in one place.
"""
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

# ─────────────────────────────── palette ────────────────────────────────────
BG          = "#f0f4ff"          # soft lavender-blue background
SURFACE     = "#ffffff"          # card / panel surface
BORDER      = "#dde3f0"          # subtle border / separator
TEXT        = "#1a1f36"          # primary text  (near-black)
MUTED       = "#6b7a99"          # secondary text

PRIMARY      = "#5b5ef4"         # vivid indigo-purple
PRIMARY_DARK = "#4547d4"
PRIMARY_SOFT = "#ededff"

ACCENT       = "#7c3aed"         # violet accent (logo ring etc.)

# Sidebar
SIDEBAR      = "#16193a"         # deep navy
SIDEBAR_HOVER= "#222754"
SIDEBAR_TEXT = "#8b93b8"
SIDEBAR_ACT  = "#ffffff"

# Semantic colours
SUCCESS      = "#10b981"
SUCCESS_SOFT = "#d1fae5"
DANGER       = "#ef4444"
DANGER_DARK  = "#b91c1c"
DANGER_SOFT  = "#fee2e2"
WARN         = "#f59e0b"
WARN_SOFT    = "#fef3c7"
INFO         = "#0ea5e9"
INFO_SOFT    = "#e0f2fe"

ROW_ALT  = "#f7f9ff"

FONT_FAMILY = "Segoe UI"


# ─────────────────────────────── helpers ────────────────────────────────────
def font(size=10, bold=False, italic=False):
    """Return a font tuple using the family chosen by apply_theme()."""
    weight = "bold" if bold else "normal"
    slant  = "italic" if italic else "roman"
    return (FONT_FAMILY, size, weight, slant)


def _pick_font_family(root):
    available = set(tkfont.families(root))
    for name in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter",
                 "Noto Sans", "Ubuntu", "DejaVu Sans", "Helvetica", "Arial"):
        if name in available:
            return name
    return "TkDefaultFont"


# ─────────────────────────────── ttk styles ─────────────────────────────────
def apply_theme(root):
    """Configure ttk styles. Call once right after creating the Tk root."""
    global FONT_FAMILY
    FONT_FAMILY = _pick_font_family(root)
    root.configure(background=BG)

    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        try:
            tkfont.nametofont(name).configure(family=FONT_FAMILY, size=10)
        except tk.TclError:
            pass

    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=TEXT, font=font(10),
                 borderwidth=0, focuscolor=BG, troughcolor=BORDER)

    # ── frames & labels ──────────────────────────────────────────────────────
    s.configure("TFrame",          background=BG)
    s.configure("Card.TFrame",     background=SURFACE)
    s.configure("Soft.TFrame",     background=PRIMARY_SOFT)
    s.configure("Sidebar.TFrame",  background=SIDEBAR)

    s.configure("TLabel",          background=BG,        foreground=TEXT)
    s.configure("Card.TLabel",     background=SURFACE,   foreground=TEXT)
    s.configure("Soft.TLabel",     background=PRIMARY_SOFT, foreground=TEXT)
    s.configure("SoftTotal.TLabel",background=PRIMARY_SOFT,
                foreground=PRIMARY_DARK, font=font(15, True))

    s.configure("H1.TLabel",       font=font(20, True),  foreground=TEXT)
    s.configure("H1Sub.TLabel",    foreground=MUTED,     font=font(10))
    s.configure("Title.TLabel",    background=SURFACE,   font=font(26, True), foreground=TEXT)
    s.configure("Sub.TLabel",      background=SURFACE,   font=font(10),       foreground=MUTED)
    s.configure("Section.TLabel",  background=SURFACE,   font=font(12, True), foreground=TEXT)
    s.configure("Field.TLabel",    background=SURFACE,   font=font(9, True),  foreground=MUTED)
    s.configure("Hint.TLabel",     foreground=MUTED,     font=font(9))
    s.configure("CardHint.TLabel", background=SURFACE,   foreground=MUTED,    font=font(9))
    s.configure("Total.TLabel",    background=PRIMARY_SOFT, font=font(15, True), foreground=PRIMARY_DARK)

    # ── buttons ──────────────────────────────────────────────────────────────
    def _btn(style, bg, fg, border, hover, pressed=None, padding=(16, 9), bold=False):
        pressed = pressed or hover
        s.configure(style, background=bg, foreground=fg, bordercolor=border,
                    lightcolor=bg, darkcolor=bg, focuscolor=bg,
                    relief="solid", borderwidth=1, padding=padding, font=font(10, bold))
        s.map(style,
              background=[("disabled", BORDER), ("pressed", pressed), ("active", hover)],
              bordercolor=[("pressed", pressed), ("active", hover if bg != SURFACE else PRIMARY)],
              lightcolor=[("pressed", pressed), ("active", hover)],
              darkcolor=[("pressed", pressed), ("active", hover)],
              foreground=[("disabled", MUTED)])

    _btn("TButton",       SURFACE,  TEXT,    "#c8d0e7", PRIMARY_SOFT, "#dce1f5")
    _btn("Accent.TButton",PRIMARY,  "#fff",  PRIMARY,   PRIMARY_DARK, "#3730b8", bold=True)
    _btn("Danger.TButton",SURFACE,  DANGER,  "#fca5a5", DANGER_SOFT, "#fecaca")
    _btn("Header.TButton",SURFACE,  TEXT,    "#c8d0e7", PRIMARY_SOFT, "#dce1f5", padding=(14, 7))
    _btn("Ghost.TButton", BG,       MUTED,   BG,        "#e2e8f5",    "#d4daf0")

    # ── inputs ───────────────────────────────────────────────────────────────
    for style in ("TEntry", "TSpinbox", "TCombobox"):
        s.configure(style, fieldbackground=SURFACE, background=SURFACE,
                    foreground=TEXT, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER,
                    insertcolor=TEXT, padding=(10, 7),
                    arrowcolor=MUTED, borderwidth=1, relief="flat")
        s.map(style,
              bordercolor=[("focus", PRIMARY)],
              lightcolor=[("focus", PRIMARY)],
              darkcolor=[("focus", PRIMARY)],
              fieldbackground=[("readonly", SURFACE)],
              foreground=[("readonly", TEXT)],
              selectbackground=[("readonly", SURFACE)],
              selectforeground=[("readonly", TEXT)])
    root.option_add("*TCombobox*Listbox.background",       SURFACE)
    root.option_add("*TCombobox*Listbox.foreground",       TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", PRIMARY)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    root.option_add("*TCombobox*Listbox.font",             font(10))

    s.configure("Card.TCheckbutton", background=SURFACE, foreground=MUTED, font=font(9))
    s.map("Card.TCheckbutton",
          background=[("active", SURFACE)],
          foreground=[("active", TEXT)])

    # ── tables ───────────────────────────────────────────────────────────────
    s.configure("Treeview", background=SURFACE, fieldbackground=SURFACE,
                foreground=TEXT, rowheight=34, borderwidth=0, relief="flat", font=font(10))
    s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    s.map("Treeview",
          background=[("selected", PRIMARY_SOFT)],
          foreground=[("selected", PRIMARY_DARK)])
    s.configure("Treeview.Heading", background="#eef0f8", foreground=MUTED,
                font=font(9, True), relief="flat", padding=(8, 10), borderwidth=0)
    s.map("Treeview.Heading", background=[("active", "#e0e4f5")])

    # ── slim scrollbars ───────────────────────────────────────────────────────
    s.layout("Vertical.TScrollbar", [
        ("Vertical.Scrollbar.trough", {
            "sticky": "ns",
            "children": [("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
    s.configure("Vertical.TScrollbar", background="#c8d0e7", troughcolor=SURFACE,
                bordercolor=SURFACE, lightcolor="#c8d0e7", darkcolor="#c8d0e7",
                gripcount=0, width=8)
    s.map("Vertical.TScrollbar",
          background=[("active", "#8898c4"), ("pressed", "#8898c4")],
          lightcolor=[("active", "#8898c4")],
          darkcolor=[("active", "#8898c4")])

    # ── progress bar ─────────────────────────────────────────────────────────
    s.configure("TProgressbar", background=PRIMARY, troughcolor=PRIMARY_SOFT,
                bordercolor=PRIMARY_SOFT, lightcolor=PRIMARY, darkcolor=PRIMARY_DARK)

    # ── separator ────────────────────────────────────────────────────────────
    s.configure("TSeparator", background=BORDER)


# ─────────────────────────────── reusable widgets ───────────────────────────

class Card(tk.Frame):
    """White card panel with a subtle drop-shadow border and optional title."""

    def __init__(self, master, title=None, padding=16, shadow_color="#d8dff0", **kw):
        super().__init__(master, bg=shadow_color, padx=1, pady=1, **kw)
        self.body = ttk.Frame(self, style="Card.TFrame", padding=padding)
        self.body.pack(fill="both", expand=True)
        if title:
            hdr = ttk.Frame(self.body, style="Card.TFrame")
            hdr.pack(fill="x", pady=(0, 12))
            ttk.Label(hdr, text=title, style="Section.TLabel").pack(side="left", anchor="w")


class StatCard(tk.Frame):
    """KPI tile with a coloured gradient-strip, emoji icon, caption and value."""

    def __init__(self, master, caption, icon="📊", color=PRIMARY, soft=None):
        soft = soft or PRIMARY_SOFT
        super().__init__(master, bg=color, padx=2, pady=2)
        inner = tk.Frame(self, bg=SURFACE)
        inner.pack(fill="both", expand=True)

        # colour bar on the left
        bar = tk.Frame(inner, bg=color, width=6)
        bar.pack(side="left", fill="y")

        body = tk.Frame(inner, bg=SURFACE, padx=14, pady=12)
        body.pack(side="left", fill="both", expand=True)

        # top row: caption + icon
        top = tk.Frame(body, bg=SURFACE)
        top.pack(fill="x")
        tk.Label(top, text=caption.upper(), bg=SURFACE, fg=MUTED,
                 font=font(8, True)).pack(side="left")
        tk.Label(top, text=icon, bg=SURFACE, font=(FONT_FAMILY, 14)).pack(side="right")

        self.value = tk.Label(body, text="—", bg=SURFACE, fg=TEXT,
                              font=font(22, True))
        self.value.pack(anchor="w", pady=(4, 0))

        self.note_lbl = tk.Label(body, text="", bg=SURFACE, fg=MUTED, font=font(8))
        self.note_lbl.pack(anchor="w")

    def set(self, value, note=""):
        self.value.config(text=value)
        self.note_lbl.config(text=note)


def make_table(master, columns, height=2, selectmode="browse", scroll=True):
    """Treeview with auto-hiding slim scrollbar and zebra/low-stock row tags."""
    box = ttk.Frame(master, style="Card.TFrame")
    tree = ttk.Treeview(box, columns=[c[0] for c in columns], show="headings",
                        selectmode=selectmode, height=height)
    for key, text, width, anchor in columns:
        tree.heading(key, text=text, anchor="center" if anchor == "center" else anchor)
        tree.column(key, width=width, minwidth=40, anchor=anchor, stretch=True)
    tree.tag_configure("odd",  background=ROW_ALT)
    tree.tag_configure("even", background=SURFACE)
    tree.tag_configure("low",  background=DANGER_SOFT, foreground=DANGER_DARK)
    tree.pack(side="left", fill="both", expand=True)

    if scroll:
        sb = ttk.Scrollbar(box, orient="vertical", command=tree.yview)

        def on_scroll(first, last):
            if float(first) <= 0.0 and float(last) >= 1.0:
                sb.pack_forget()
            else:
                sb.pack(side="left", fill="y")
            sb.set(first, last)

        tree.configure(yscrollcommand=on_scroll)
    return box, tree


def row_tag(index, low=False):
    """Return a tag tuple for zebra-striping or low-stock highlighting."""
    return ("low",) if low else (("odd",) if index % 2 else ("even",))


def field(parent, label, row, var=None, show=None, width=24, widget=None, column=0):
    """Grid a label + input pair. Returns the input widget."""
    ttk.Label(parent, text=label.upper(), style="Field.TLabel").grid(
        row=row * 2, column=column, sticky="w", pady=(10, 3))
    w = widget or ttk.Entry(parent, textvariable=var, show=show, width=width)
    w.grid(row=row * 2 + 1, column=column, sticky="ew")
    return w


def rounded_button(parent, text, command, bg=PRIMARY, fg="white", padx=18, pady=8,
                   font_size=10, bold=True):
    """Plain tk.Button with a flat modern look (no relief artifacts)."""
    btn = tk.Button(parent, text=text, command=command,
                    bg=bg, fg=fg, activebackground=PRIMARY_DARK, activeforeground="white",
                    relief="flat", cursor="hand2",
                    font=font(font_size, bold), padx=padx, pady=pady,
                    bd=0, highlightthickness=0)
    return btn
