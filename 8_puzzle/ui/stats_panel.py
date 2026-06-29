import tkinter as tk
from tkinter import ttk

class StatsPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#FFFFFF", **kwargs)
        self._build()

    def _build(self):
        self.labels = {}
        fields = [
            ("step",      "Step:"),
            ("algo",      "Algorithm:"),
            ("expanded",  "Expanded:"),
            ("action",    "Action:"),
            ("path_cost", "Path Cost:"),
            ("depth",     "Depth:"),
            ("ids_limit", "IDS Limit:"),
            ("frontier",  "Frontier:"),
            ("explored",  "Explored:"),
            ("status",    "Status:"),
        ]
        
        for key, label in fields:
            row = tk.Frame(self, bg="#FFFFFF")
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text=label, bg="#FFFFFF", fg="#475569",
                     font=("Segoe UI", 10), width=12, anchor="w").pack(side="left")
            default_val = "Ready." if key == "status" else "-"
            lbl = tk.Label(row, text=default_val, bg="#FFFFFF", fg="#1E293B",
                           font=("Segoe UI", 10, "italic" if key=="status" else "normal"), anchor="w")
            lbl.pack(side="left")
            self.labels[key] = lbl

    def update_stat(self, key, value):
        if key in self.labels:
            self.labels[key].config(text=str(value))
            
    def update_status(self, text, color="#2563EB"):
        self.labels["status"].config(text=text, fg=color)

    def reset_current(self):
        for key, lbl in self.labels.items():
            if key == "status":
                lbl.config(text="Ready.", fg="#1E293B")
            else:
                lbl.config(text="-", fg="#1E293B")
