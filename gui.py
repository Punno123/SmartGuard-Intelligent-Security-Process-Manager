# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import os

from monitor import list_processes
from logger import log_event
from detector import detect_suspicious
from utils import kill_process
from tkinter.scrolledtext import ScrolledText


# -------------------------------
# 🪟 Window
# -------------------------------
root = tk.Tk()
root.title("SmartGuard - Process Monitor")
root.geometry("800x450")

# -------------------------------
# 🔍 Search Bar
# -------------------------------
search_var = tk.StringVar()

search_frame = tk.Frame(root)
search_frame.pack(fill=tk.X, padx=10, pady=5)

tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# -------------------------------
# 🌳 Table (Treeview)
# -------------------------------
columns = ("PID", "Name", "CPU", "Threads", "Status")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)

tree.column("PID", width=80)
tree.column("Name", width=250)
tree.column("CPU", width=100)
tree.column("Threads", width=100)
tree.column("Status", width=150)

# 🟡/🔴 Color tags
tree.tag_configure("medium", background="khaki")
tree.tag_configure("danger", background="lightcoral")

tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# -------------------------------
# ❌ Smart Kill Function
# -------------------------------
def kill_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "No process selected")
        return

    item = tree.item(selected[0])
    pid = item['values'][0]
    name = item['values'][1]

    # 🔐 Prevent killing system processes
    if pid in [0, 4] or name in ["System", "System Idle Process", "Registry", "svchost.exe"]:
        messagebox.showwarning("Warning", "Cannot kill system process!")
        return

    # 🔐 Prevent killing this GUI
    if pid == os.getpid():
        messagebox.showwarning("Warning", "Cannot kill this application!")
        return

    # 🔍 Get updated process info
    processes = list_processes()
    selected_process = None

    for p in processes:
        if p['pid'] == pid:
            selected_process = p
            break

    if not selected_process:
        messagebox.showerror("Error", "Process not found!")
        return

    # 🧠 Get reasons
    reasons = detect_suspicious(selected_process)

    # ❗ Smart decision
    if not reasons:
        confirm = messagebox.askyesno(
            "Confirm Kill",
            f"{name} seems NORMAL.\nAre you sure you want to kill it?"
        )
        if not confirm:
            return
    else:
        confirm = messagebox.askyesno(
            "Confirm Kill",
            f"Kill {name}?\n\nReasons:\n- " + "\n- ".join(reasons)
        )
        if not confirm:
            return

    # 💥 Kill process
    success = kill_process(pid)

    if success:
        messagebox.showinfo("Success", f"{name} (PID {pid}) terminated!")
    else:
        messagebox.showerror("Error", "Failed to terminate process")

def open_log_window():
    log_window = tk.Toplevel(root)
    log_window.title("System Logs")
    log_window.geometry("700x400")

    # Title
    tk.Label(log_window, text="Log History", font=("Arial", 14)).pack(pady=5)

    # Scrollable text box
    log_box = ScrolledText(log_window)
    log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_logs():
        try:
            with open("logs.txt", "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = "No logs available."

        log_box.delete(1.0, tk.END)
        log_box.insert(tk.END, content)

        # Auto refresh every 3 sec
        log_window.after(3000, load_logs)

    load_logs()        

# -------------------------------
# 🔘 Kill Button
# -------------------------------
btn = tk.Button(root, text="Kill Selected Process", command=kill_selected)
btn.pack(pady=8)
log_btn = tk.Button(root, text="Check Log", command=open_log_window)
log_btn.pack(pady=5)

# -------------------------------
# 🔄 Update Function
# -------------------------------
def update_processes():
    # Clear table
    for row in tree.get_children():
        tree.delete(row)

    processes = list_processes()
    query = search_var.get().lower()

    for p in processes:
        name = p.get('name')
        pid = p.get('pid')
        cpu = round(p.get('cpu_percent', 0), 2)
        threads = p.get('threads', 0)

        # 🔐 Skip system processes
        if pid in [0, 4] or name in ["System", "System Idle Process", "Registry", "svchost.exe"]:
            continue
        if name is None:
            continue

        # 🔍 Search filter
        if query and query not in name.lower():
            continue

        # 🧠 Detection
        result = detect_suspicious(p)
        if result:
          message = f"{name} (PID {pid}) -> {', '.join(result)}"
          log_event(message)

        # 🎯 Status logic
        status = "Normal"
        tag = ""

        if cpu > 80:
            status = "🔴 High Risk"
            tag = "danger"
        elif cpu > 50:
            status = "🟡 Medium Risk"
            tag = "medium"
        elif result:
            status = "⚠️ " + ", ".join(result)

        # Insert row
        if tag:
            tree.insert("", tk.END, values=(pid, name, cpu, threads, status), tags=(tag,))
        else:
            tree.insert("", tk.END, values=(pid, name, cpu, threads, status))

    # Refresh every 3 sec
    root.after(3000, update_processes)

# -------------------------------
# ▶️ Start
# -------------------------------
update_processes()
root.mainloop()