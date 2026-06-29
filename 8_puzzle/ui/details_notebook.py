import tkinter as tk
from tkinter import ttk

class MiniPuzzle(tk.Frame):
    def __init__(self, master, state, step_idx, action, click_cb, **kwargs):
        super().__init__(master, bg="#FFFFFF", **kwargs)
        self.step_idx = step_idx
        self.click_cb = click_cb
        
        def on_click(e):
            if self.click_cb:
                self.click_cb(self.step_idx)
                
        self.bind("<Button-1>", on_click)
        
        lbl_title = tk.Label(self, text=f"Step {step_idx}\n{action}", bg="#FFFFFF", fg="#0891B2", font=("Segoe UI", 9, "bold"), cursor="hand2")
        lbl_title.pack(pady=(2, 2))
        lbl_title.bind("<Button-1>", on_click)
        
        is_belief = isinstance(state[0], (list, tuple))
        states = state if is_belief else [state]
        
        container = tk.Frame(self, bg="#FFFFFF")
        container.pack(pady=(0, 4), padx=2)
        
        for st in states:
            grid_f = tk.Frame(container, bg="#CBD5E1", padx=2, pady=2, cursor="hand2")
            grid_f.pack(side="left", padx=2)
            grid_f.bind("<Button-1>", on_click)
            
            for i, val in enumerate(st):
                text = str(val) if val not in (0, -1) else ("?" if val == -1 else "")
                bg_color = "#1E3A8A" if val != 0 else "#F1F5F9"
                lbl = tk.Label(grid_f, text=text, width=2, height=1, font=("Segoe UI", 8, "bold"), bg=bg_color, fg="#FFFFFF", cursor="hand2")
                lbl.grid(row=i//3, column=i%3, padx=1, pady=1)
                lbl.bind("<Button-1>", on_click)


class DetailsNotebook(tk.Frame):
    def __init__(self, master, on_solution_click_cb, **kwargs):
        super().__init__(master, bg="#F3F4F6", **kwargs)
        self.on_solution_click_cb = on_solution_click_cb
        self._build()

    def _build(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#F3F4F6", borderwidth=0)
        style.configure("TNotebook.Tab", background="#E5E7EB", foreground="#475569", padding=[10, 2])
        style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#0891B2")])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}
        tab_names = ["Nodes", "Frontier", "Explored", "Step Log", "Conditional Plan", "Solution Path"]
        
        for name in tab_names:
            txt = tk.Text(self.notebook, font=("Consolas", 9), bg="#FFFFFF", fg="#1E293B", bd=0, insertbackground="#1E293B")
            self.notebook.add(txt, text=name)
            self.tabs[name] = txt
            
        self.tabs["Solution Path"].config(wrap="word", cursor="arrow")

    def clear_all(self):
        for txt in self.tabs.values():
            txt.config(state="normal")
            txt.delete('1.0', tk.END)

    def rename_tab_text(self, internal_key, new_text):
        if internal_key in self.tabs:
            idx = list(self.tabs.keys()).index(internal_key)
            self.notebook.tab(idx, text=new_text)

    def write_tab(self, tab_name, text):
        if tab_name in self.tabs:
            txt = self.tabs[tab_name]
            txt.config(state="normal")
            txt.insert(tk.END, text + "\n")
            txt.see(tk.END)

    def render_solution_path(self, path):
        txt = self.tabs["Solution Path"]
        txt.config(state="normal")
        txt.delete("1.0", tk.END)
        
        display_path = path
        skipped = False
        if len(path) > 200:
            display_path = path[:100] + [None] + path[-100:]
            skipped = True
            
        for display_idx, node in enumerate(display_path):
            if node is None:
                lbl = tk.Label(txt, text=f" ... \n(Skipped {len(path) - 200} steps)\n ... ", bg="#FFFFFF", fg="#475569", font=("Segoe UI", 10, "italic"))
                txt.window_create(tk.END, window=lbl)
                lbl = tk.Label(txt, text=" ➔ ", bg="#FFFFFF", fg="#475569", font=("Segoe UI", 12))
                txt.window_create(tk.END, window=lbl)
                continue
                
            # Find the actual index in the original path (safe because node instances are unique in the path)
            actual_idx = path.index(node) if node in path else display_idx
            act = getattr(node, 'action', "Start") if getattr(node, 'action', None) else "Start"
            mini = MiniPuzzle(txt, node.state, actual_idx, act, self.on_solution_click_cb)
            txt.window_create(tk.END, window=mini)
            
            if display_idx < len(display_path) - 1:
                lbl = tk.Label(txt, text=" ➔ ", bg="#FFFFFF", fg="#475569", font=("Segoe UI", 12))
                txt.window_create(tk.END, window=lbl)
                
        txt.config(state="disabled")

    def highlight_step(self, step_idx):
        # With graphical tiles, highlighting would mean iterating through embedded widgets
        # For simplicity, we just pass since the canvas updates visually.
        pass
