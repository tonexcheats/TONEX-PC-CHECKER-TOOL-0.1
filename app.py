import os
import sys
import platform
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None

BG = "#090909"
PANEL = "#121212"
PANEL2 = "#181818"
RED = "#ff2438"
RED_DARK = "#8f1020"
TEXT = "#f2f2f2"
MUTED = "#969696"
GREEN = "#62e6a7"

class TonexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TONEX PC CHECKER TOOL")
        self.root.geometry("1120x720")
        self.root.minsize(900, 580)
        self.root.configure(bg=BG)
        self.sort_reverse = False
        self.build_style()
        self.build_ui()
        self.refresh_all()
        self.schedule_refresh()

    def build_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL2, foreground=TEXT,
                        fieldbackground=PANEL2, rowheight=27, borderwidth=0,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#242424", foreground=RED,
                        relief="flat", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", RED_DARK)],
                  foreground=[("selected", "white")])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL2, foreground=MUTED,
                        padding=(18, 9), font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", RED_DARK)],
                  foreground=[("selected", "white")])

    def label(self, parent, text, size=10, color=TEXT, bold=False):
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def button(self, parent, text, command, danger=False):
        return tk.Button(parent, text=text, command=command, bg=RED if danger else "#292929",
                         fg="white", activebackground=RED_DARK, activeforeground="white",
                         relief="flat", bd=0, padx=14, pady=8,
                         font=("Segoe UI", 9, "bold"), cursor="hand2")

    def build_ui(self):
        top = tk.Frame(self.root, bg="#0d0d0d", height=76,
                       highlightbackground=RED_DARK, highlightthickness=1)
        top.pack(fill="x")
        top.pack_propagate(False)
        title = tk.Frame(top, bg="#0d0d0d")
        title.pack(side="left", padx=22, pady=12)
        tk.Label(title, text="TONEX", bg="#0d0d0d", fg=RED,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(title, text="PC CHECKER TOOL  /  SYSTEM INTELLIGENCE",
                 bg="#0d0d0d", fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.clock = self.label(top, "", 10, MUTED, True)
        self.clock.pack(side="right", padx=22)

        self.statusbar = tk.Label(self.root, text="  ● SYSTEM ONLINE",
                                  bg="#171717", fg=GREEN, anchor="w",
                                  font=("Segoe UI", 9, "bold"), pady=7)
        self.statusbar.pack(fill="x", side="bottom")

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=14)

        self.cards = tk.Frame(body, bg=BG)
        self.cards.pack(fill="x", pady=(0, 13))
        self.cpu_value = self.make_card(self.cards, "CPU LOAD", "—")
        self.ram_value = self.make_card(self.cards, "MEMORY USAGE", "—")
        self.disk_value = self.make_card(self.cards, "SYSTEM DISK", "—")
        self.proc_value = self.make_card(self.cards, "RUNNING PROCESSES", "—")

        self.tabs = ttk.Notebook(body)
        self.tabs.pack(fill="both", expand=True)
        self.dashboard_tab = tk.Frame(self.tabs, bg=BG)
        self.process_tab = tk.Frame(self.tabs, bg=BG)
        self.services_tab = tk.Frame(self.tabs, bg=BG)
        self.info_tab = tk.Frame(self.tabs, bg=BG)
        self.tabs.add(self.dashboard_tab, text="OVERVIEW")
        self.tabs.add(self.process_tab, text="PROCESSES")
        self.tabs.add(self.services_tab, text="SERVICES")
        self.tabs.add(self.info_tab, text="SYSTEM INFO")
        self.build_dashboard()
        self.build_processes()
        self.build_services()
        self.build_info()

    def make_card(self, parent, title, value):
        card = tk.Frame(parent, bg=PANEL, highlightbackground="#303030", highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 9))
        tk.Label(card, text=title, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=13, pady=(11, 3))
        val = tk.Label(card, text=value, bg=PANEL, fg=RED,
                       font=("Segoe UI", 20, "bold"))
        val.pack(anchor="w", padx=13, pady=(0, 11))
        return val

    def build_dashboard(self):
        left = tk.Frame(self.dashboard_tab, bg=PANEL, padx=18, pady=16)
        left.pack(fill="both", expand=True, padx=3, pady=3)
        self.label(left, "LIVE SYSTEM STATUS", 12, RED, True).pack(anchor="w", pady=(0, 14))
        self.dashboard_text = tk.Text(left, bg=PANEL2, fg=TEXT, insertbackground=RED,
                                      relief="flat", font=("Consolas", 10),
                                      padx=14, pady=12, height=16)
        self.dashboard_text.pack(fill="both", expand=True)
        self.dashboard_text.configure(state="disabled")
        self.button(left, "REFRESH NOW", self.refresh_all).pack(anchor="e", pady=(12, 0))

    def build_processes(self):
        bar = tk.Frame(self.process_tab, bg=BG)
        bar.pack(fill="x", pady=(5, 10))
        self.search_var = tk.StringVar()
        entry = tk.Entry(bar, textvariable=self.search_var, bg=PANEL2, fg=TEXT,
                         insertbackground=RED, relief="flat", font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        entry.insert(0, "")
        self.button(bar, "SEARCH", self.refresh_processes).pack(side="left", padx=4)
        self.button(bar, "REFRESH", self.refresh_processes).pack(side="left", padx=4)
        self.button(bar, "END TASK", self.end_process, True).pack(side="left", padx=4)
        frame = tk.Frame(self.process_tab, bg=PANEL)
        frame.pack(fill="both", expand=True)
        cols = ("pid", "name", "cpu", "memory", "status")
        self.proc_tree = ttk.Treeview(frame, columns=cols, show="headings")
        widths = (85, 350, 110, 130, 140)
        for c, w in zip(cols, widths):
            self.proc_tree.heading(c, text=c.upper())
            self.proc_tree.column(c, width=w, anchor="w" if c == "name" else "center")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.proc_tree.yview)
        self.proc_tree.configure(yscrollcommand=scroll.set)
        self.proc_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def build_services(self):
        bar = tk.Frame(self.services_tab, bg=BG)
        bar.pack(fill="x", pady=(5, 10))
        self.button(bar, "REFRESH SERVICES", self.refresh_services).pack(side="left")
        self.label(bar, "  Read-only service list", 9, MUTED).pack(side="left")
        frame = tk.Frame(self.services_tab, bg=PANEL)
        frame.pack(fill="both", expand=True)
        cols = ("name", "display", "status", "start")
        self.service_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c, w in zip(cols, (220, 430, 120, 140)):
            self.service_tree.heading(c, text=c.upper())
            self.service_tree.column(c, width=w)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.service_tree.yview)
        self.service_tree.configure(yscrollcommand=scroll.set)
        self.service_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def build_info(self):
        frame = tk.Frame(self.info_tab, bg=PANEL, padx=20, pady=18)
        frame.pack(fill="both", expand=True, padx=3, pady=3)
        self.info_text = tk.Text(frame, bg=PANEL2, fg=TEXT, relief="flat",
                                 font=("Consolas", 10), padx=15, pady=15)
        self.info_text.pack(fill="both", expand=True)

    def set_text(self, widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def refresh_all(self):
        if psutil is None:
            self.set_text(self.dashboard_text, "psutil is missing. Install dependencies using the included build workflow.")
            return
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(os.environ.get("SystemDrive", "C:\\") + "\\")
            procs = len(psutil.pids())
            self.cpu_value.config(text=f"{cpu:.0f}%")
            self.ram_value.config(text=f"{mem.percent:.0f}%")
            self.disk_value.config(text=f"{disk.percent:.0f}%")
            self.proc_value.config(text=str(procs))
            now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
            text = (
                f"TONEX PC CHECKER TOOL\n{'='*58}\n"
                f"Last updated       : {now}\n"
                f"Operating system   : {platform.system()} {platform.release()}\n"
                f"Computer name      : {platform.node()}\n"
                f"Processor           : {platform.processor() or 'Not reported'}\n"
                f"CPU logical cores  : {psutil.cpu_count(logical=True)}\n"
                f"CPU utilization    : {cpu:.1f}%\n"
                f"Physical memory    : {mem.used / (1024**3):.2f} / {mem.total / (1024**3):.2f} GB ({mem.percent:.1f}%)\n"
                f"Available memory   : {mem.available / (1024**3):.2f} GB\n"
                f"System disk        : {disk.used / (1024**3):.1f} / {disk.total / (1024**3):.1f} GB ({disk.percent:.1f}%)\n"
                f"Running processes  : {procs}\n\n"
                "Use the PROCESSES tab to inspect running apps. Ending a process can cause unsaved work to be lost.\n"
                "The SERVICES tab is read-only in this edition."
            )
            self.set_text(self.dashboard_text, text)
            self.set_text(self.info_text, self.build_info_content())
            self.clock.config(text=now)
            self.refresh_processes()
            self.refresh_services()
            self.statusbar.config(text="  ● SYSTEM ONLINE  |  Monitoring active", fg=GREEN)
        except Exception as e:
            self.statusbar.config(text=f"  ● MONITOR WARNING: {e}", fg=RED)

    def refresh_processes(self):
        if psutil is None or not hasattr(self, "proc_tree"):
            return
        for item in self.proc_tree.get_children():
            self.proc_tree.delete(item)
        query = self.search_var.get().strip().lower()
        rows = []
        for p in psutil.process_iter(["pid", "name", "memory_info", "status"]):
            try:
                name = p.info.get("name") or "Unknown"
                if query and query not in name.lower() and query not in str(p.info["pid"]):
                    continue
                mem = p.info.get("memory_info")
                memory = (mem.rss / (1024**2)) if mem else 0
                try:
                    cpu = p.cpu_percent(interval=None)
                except Exception:
                    cpu = 0
                rows.append((p.info["pid"], name, cpu, memory, p.info.get("status", "—")))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        rows.sort(key=lambda x: x[3], reverse=True)
        for row in rows:
            self.proc_tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.1f}%",
                                                     f"{row[3]:.1f} MB", row[4]))

    def end_process(self):
        selected = self.proc_tree.selection()
        if not selected:
            messagebox.showinfo("TONEX", "Select a process first.")
            return
        values = self.proc_tree.item(selected[0], "values")
        pid, name = int(values[0]), values[1]
        if pid == os.getpid():
            messagebox.showwarning("TONEX", "The checker cannot end itself.")
            return
        if not messagebox.askyesno("Confirm END TASK",
                                   f"End process '{name}' (PID {pid})?\nUnsaved work in that app may be lost."):
            return
        try:
            psutil.Process(pid).terminate()
            self.root.after(700, self.refresh_processes)
        except Exception as e:
            messagebox.showerror("Could not end process", str(e))

    def refresh_services(self):
        if psutil is None or not hasattr(self, "service_tree") or os.name != "nt":
            return
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
        try:
            for s in psutil.win_service_iter():
                try:
                    info = s.as_dict()
                    self.service_tree.insert("", "end", values=(
                        info.get("name", ""), info.get("display_name", ""),
                        info.get("status", ""), info.get("start_type", "")))
                except Exception:
                    pass
        except Exception:
            pass

    def build_info_content(self):
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(os.environ.get("SystemDrive", "C:\\") + "\\")
            return (
                f"DEVICE NAME       : {platform.node()}\n"
                f"OS                : {platform.platform()}\n"
                f"ARCHITECTURE      : {platform.machine()}\n"
                f"PROCESSOR         : {platform.processor() or 'Unknown'}\n"
                f"CPU CORES         : {psutil.cpu_count(logical=False)} physical / {psutil.cpu_count()} logical\n"
                f"TOTAL RAM         : {mem.total / (1024**3):.2f} GB\n"
                f"AVAILABLE RAM     : {mem.available / (1024**3):.2f} GB\n"
                f"BOOT TIME         : {datetime.fromtimestamp(psutil.boot_time())}\n"
                f"SYSTEM DRIVE      : {disk.total / (1024**3):.1f} GB total\n"
                f"HOSTNAME          : {socket.gethostname()}\n"
            )
        except Exception as e:
            return f"System information unavailable: {e}"

    def schedule_refresh(self):
        self.root.after(2500, self.periodic_refresh)

    def periodic_refresh(self):
        self.refresh_all()
        self.schedule_refresh()

def main():
    if psutil is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("TONEX", "Required monitoring library is missing.")
        return
    root = tk.Tk()
    TonexApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
