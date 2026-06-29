import tkinter as tk

class PuzzleCanvas(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#FFFFFF", **kwargs)
        self.grid_frames = []
        self.cells = [] # list of lists of labels
        
        self.turn_label = tk.Label(self, text="", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#1E293B")
        self.turn_label.pack(pady=(0, 5))
        
        self.container = tk.Frame(self, bg="#FFFFFF")
        self.container.pack(expand=True)

    def set_turn(self, action_str):
        if not action_str:
            self.turn_label.config(text="")
            return
            
        if "[MAX]" in action_str:
            self.turn_label.config(text="MAX'S TURN", fg="#2563EB")
        elif "[MIN]" in action_str:
            self.turn_label.config(text="MIN'S TURN", fg="#EF4444")
        elif "[CHANCE]" in action_str:
            self.turn_label.config(text="CHANCE'S TURN", fg="#F59E0B")
        else:
            self.turn_label.config(text="")

    def _build_grids(self, num_grids):
        for f in self.grid_frames:
            f.destroy()
        self.grid_frames = []
        self.cells = []
        
        # If there are many grids, scale down the font so they fit
        font_size = 24 if num_grids == 1 else 16
        width = 4 if num_grids == 1 else 3
        height = 2 if num_grids == 1 else 1

        for g in range(num_grids):
            frame = tk.Frame(self.container, bg="#FFFFFF")
            frame.pack(side="left", padx=10)
            
            if num_grids > 1:
                tk.Label(frame, text=f"State {g+1}", bg="#FFFFFF", fg="#475569", font=("Segoe UI", 10, "bold")).pack(pady=(0, 5))
                
            grid_f = tk.Frame(frame, bg="#CBD5E1", padx=2, pady=2)
            grid_f.pack()
            
            grid_cells = []
            for i in range(9):
                lbl = tk.Label(
                    grid_f, 
                    text="", 
                    font=("Segoe UI", font_size, "bold"), 
                    width=width, height=height,
                    bg="#2563EB", fg="#FFFFFF", 
                    bd=0, highlightthickness=0
                )
                lbl.grid(row=i//3, column=i%3, padx=2, pady=2)
                grid_cells.append(lbl)
                
            self.grid_frames.append(frame)
            self.cells.append(grid_cells)

    def update_grid(self, state_or_belief):
        if not state_or_belief: return
        
        # Check if single state or belief state
        is_belief = isinstance(state_or_belief[0], (list, tuple))
        
        states = state_or_belief if is_belief else [state_or_belief]
        
        if len(states) != len(self.grid_frames):
            self._build_grids(len(states))
            
        colors = ["#2563EB", "#7C3AED", "#0891B2"] # Blue, Purple, Cyan for different states
            
        for g, state in enumerate(states):
            primary_color = colors[g % len(colors)] if is_belief else "#2563EB"
            for i, val in enumerate(state):
                if val == 0 or val == -1:
                    text = "?" if val == -1 else ""
                    self.cells[g][i].config(text=text, bg="#E5E7EB", fg="#1E293B" if val == -1 else "#FFFFFF")
                else:
                    self.cells[g][i].config(text=str(val), bg=primary_color, fg="#FFFFFF")
