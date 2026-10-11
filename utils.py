"""Small helpers shared by the app."""
import os
import subprocess
import sys


def open_file(path):
    """Open a file with the operating system's default viewer (used to view/print invoices)."""
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa: S606 (Windows only)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def money(value):
    import config
    return f"{config.CURRENCY} {value:,.2f}"
