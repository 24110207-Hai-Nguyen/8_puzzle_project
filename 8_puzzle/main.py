import sys, os
import tkinter as tk
from tkinter import ttk
import threading
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from map_generator import GOAL, get_neighbors, format_state_matrix
from algorithms import ALGORITHMS
from ui import PuzzleCanvas, StatsPanel, DetailsNotebook

ALGO_GROUPS = [
    ("Uninformed Search",       ["BFS", "DFS", "UCS", "IDS"]),
    ("Informed Search",         ["Greedy Best-First", "A*"]),
    ("Local Search",            ["Simple Hill Climbing", "Steepest-Ascent Hill Climbing", "Stochastic Hill Climbing", "Simulated Annealing", "Local Beam Search (k=3)"]),
    ("Complex Environment",    ["Belief-State BFS", "Partial Observation", "AND-OR Graph Search"]),
    ("Constraint Satisfaction", ["CSP: Backtracking", "CSP: Forward Checking", "CSP: AC-3", "CSP: Min-Conflicts"]),
    ("Adversarial Search",     ["Minimax", "Alpha-Beta Pruning", "Expectimax"]),
]

class EightPuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle Search Algorithms")
        self.configure(bg="#F9FAFB")
        self.resizable(True, True)
        self.minsize(1100, 780)

        self.current_state = list(GOAL)
        self.path = []
        self.current_step_idx = 0
        self.is_running = False
        self.is_animating = False

        self._build_ui()
        self._reset()

    def _build_ui(self):
        # Top Control Bar
        top_controls = tk.Frame(self, bg="#FFFFFF", pady=8, padx=14)
        top_controls.pack(fill="x")
        
        tk.Label(top_controls, text="8-PUZZLE SEARCH ALGORITHMS", bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 16, "bold")).pack(side="left", padx=(0, 20))
        
        tk.Label(top_controls, text="Group:", bg="#FFFFFF", fg="#475569", font=("Segoe UI", 9)).pack(side="left", padx=(10, 2))
        self._group_var = tk.StringVar(value=ALGO_GROUPS[0][0])
        group_cb = ttk.Combobox(top_controls, textvariable=self._group_var, values=[g[0] for g in ALGO_GROUPS], state="readonly", width=18)
        group_cb.pack(side="left", padx=4)
        
        tk.Label(top_controls, text="Algorithm:", bg="#FFFFFF", fg="#475569", font=("Segoe UI", 9)).pack(side="left", padx=(15, 2))
        self._algo_var = tk.StringVar(value=ALGO_GROUPS[0][1][0])
        self.algo_cb = ttk.Combobox(top_controls, textvariable=self._algo_var, values=ALGO_GROUPS[0][1], state="readonly", width=22)
        self.algo_cb.pack(side="left", padx=4)
        
        def on_group_change(e):
            group_name = self._group_var.get()
            for g, algos in ALGO_GROUPS:
                if g == group_name:
                    self.algo_cb.config(values=algos)
                    self.algo_cb.current(0)
                    self._on_algo_change()
                    break
        group_cb.bind("<<ComboboxSelected>>", on_group_change)
        self.algo_cb.bind("<<ComboboxSelected>>", self._on_algo_change)
        
        tk.Label(top_controls, text="Parameter:", bg="#FFFFFF", fg="#475569", font=("Segoe UI", 9)).pack(side="left", padx=(15, 2))
        self.param_entry = tk.Spinbox(top_controls, from_=1, to=200, width=5)
        self.param_entry.delete(0, "end")
        self.param_entry.insert(0, "35")
        self.param_entry.pack(side="left", padx=2)
        
        btn_cfg = dict(font=("Segoe UI", 9), relief="solid", cursor="hand2", pady=2, padx=12, bd=1)
        self._make_btn(top_controls, "Random", "#FFFFFF", "#1E293B", self._shuffle, side="left", pack_padx=(20, 4), **btn_cfg)
        
        self._btn_run = self._make_btn(top_controls, "Run", "#2563EB", "#FFFFFF", self._run, side="left", pack_padx=4, **btn_cfg)
        self._btn_run.config(bd=0, font=("Segoe UI", 9, "bold")) # Make Run button stand out
        
        self._btn_stop_algo = self._make_btn(top_controls, "Stop", "#EF4444", "#FFFFFF", self._stop_algo, state="disabled", side="left", pack_padx=4, **btn_cfg)
        self._btn_stop_algo.config(bd=0, font=("Segoe UI", 9, "bold"))

        self._make_btn(top_controls, "Reset", "#FFFFFF", "#1E293B", self._reset, side="right", pack_padx=10, **btn_cfg)

        # Main Layout
        middle_frame = tk.Frame(self, bg="#F9FAFB")
        middle_frame.pack(fill="x", padx=10, pady=10)

        # Left Panel (Goal + Board + Controls)
        left_panel = tk.Frame(middle_frame, bg="#F9FAFB")
        left_panel.pack(side="left", fill="both", expand=True)

        board_container = tk.Frame(left_panel, bg="#F9FAFB")
        board_container.pack(fill="x", pady=10)
        
        goal_frame = tk.LabelFrame(board_container, text="Goal State", bg="#F9FAFB", fg="#475569")
        goal_frame.pack(side="left", anchor="n", padx=(10, 20))
        goal_inner = tk.Frame(goal_frame, bg="#F9FAFB")
        goal_inner.pack(padx=5, pady=5)
        for i in range(9):
            val = GOAL[i]
            tk.Label(goal_inner, text=str(val) if val!=0 else "-", font=("Segoe UI", 10), width=2, bg="#F9FAFB").grid(row=i//3, column=i%3)
            
        self.canvas = PuzzleCanvas(board_container)
        self.canvas.pack(side="left")

        nav_frame = tk.Frame(left_panel, bg="#F9FAFB")
        nav_frame.pack(fill="x", pady=10, padx=10)
        tk.Button(nav_frame, text="◀ Prev", command=self._prev_step, **btn_cfg).pack(side="left", padx=4)
        tk.Button(nav_frame, text="Next ▶", command=self._next_step, **btn_cfg).pack(side="left", padx=4)
        self._btn_stop = tk.Button(nav_frame, text="Auto Play", command=self._start_animation, **btn_cfg)
        self._btn_stop.pack(side="left", padx=(4, 20))
        
        tk.Label(nav_frame, text="Speed", bg="#F9FAFB", font=("Segoe UI", 9)).pack(side="left", padx=2)
        self.speed_scale = tk.Scale(nav_frame, from_=50, to=1000, orient="horizontal", bg="#F9FAFB", bd=0, showvalue=1, resolution=50, length=200, highlightthickness=0)
        self.speed_scale.set(300)
        self.speed_scale.pack(side="left")

        # Right Panel (Stats)
        right_panel = tk.Frame(middle_frame, bg="#F9FAFB", width=280)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        self.stats = StatsPanel(right_panel)
        self.stats.pack(fill="both", expand=True)

        # Bottom Frame (Notebook)
        bottom_frame = tk.Frame(self, bg="#F9FAFB")
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.notebook = DetailsNotebook(bottom_frame, on_solution_click_cb=self._jump_to_step)
        self.notebook.pack(fill="both", expand=True)

    def _make_btn(self, parent, text, bg, fg, cmd, side="left", pack_padx=0, pack_pady=0, **kw):
        btn = tk.Button(parent, text=text, bg=bg, fg=fg, command=cmd, **kw)
        btn.pack(side=side, padx=pack_padx, pady=pack_pady)
        return btn

    @staticmethod
    def _lighten(hex_color):
        try:
            r = min(255, int(hex_color[1:3], 16) + 40)
            g = min(255, int(hex_color[3:5], 16) + 40)
            b = min(255, int(hex_color[5:7], 16) + 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

    def _on_algo_change(self, e=None):
        algo_name = self._algo_var.get()
        group_name = self._group_var.get()
        
        self.param_entry.delete(0, "end")
        if group_name == "Constraint Satisfaction":
            self.param_entry.insert(0, "4")
        elif group_name == "Adversarial Search":
            self.param_entry.insert(0, "11")
        elif group_name == "Local Search":
            if algo_name == "Simulated Annealing":
                self.param_entry.insert(0, "100")
            elif algo_name == "Local Beam Search (k=3)":
                self.param_entry.insert(0, "3")
            else:
                self.param_entry.insert(0, "50")
        else:
            self.param_entry.insert(0, "35")

        if hasattr(self.notebook, 'rename_tab_text'):
            if group_name == "Informed Search":
                self.notebook.rename_tab_text("Frontier", "Reached")
            else:
                self.notebook.rename_tab_text("Frontier", "Frontier")

        if algo_name == "Belief-State BFS":
            state1 = tuple(self.current_state)
            state2 = list(state1)
            for _ in range(5):
                state2 = list(random.choice(get_neighbors(tuple(state2)))[0])
            self.canvas.update_grid((state1, tuple(state2)))
        elif algo_name == "Partial Observation":
            st = list(self.current_state)
            hidden = 0
            for i in range(8, -1, -1):
                if st[i] != 0:
                    st[i] = -1
                    hidden += 1
                    if hidden == 2: break
            self.canvas.update_grid((tuple(st),))
        elif algo_name == "AND-OR Graph Search":
            state = list(GOAL)
            for _ in range(3):
                state = list(random.choice(get_neighbors(tuple(state)))[0])
            self.current_state = state
            self.canvas.update_grid(tuple(state))
        elif algo_name.startswith("CSP:"):
            from collections import deque
            queue = deque([(tuple(GOAL), 0)])
            visited = {tuple(GOAL)}
            states_at_depth = []
            while queue:
                st, d = queue.popleft()
                if d == 4:
                    states_at_depth.append(list(st))
                    continue
                if d > 4: break
                for n_st, _ in get_neighbors(st):
                    if n_st not in visited:
                        visited.add(n_st)
                        queue.append((n_st, d + 1))
            self.current_state = random.choice(states_at_depth) if states_at_depth else list(GOAL)
            self.canvas.update_grid(tuple(self.current_state))
        elif group_name == "Adversarial Search":
            from collections import deque
            queue = deque([(tuple(GOAL), 0)])
            visited = {tuple(GOAL)}
            states_at_depth = []
            while queue:
                st, d = queue.popleft()
                if d == 10:
                    states_at_depth.append(list(st))
                    continue
                if d > 10: break
                for n_st, _ in get_neighbors(st):
                    if n_st not in visited:
                        visited.add(n_st)
                        queue.append((n_st, d + 1))
            self.current_state = random.choice(states_at_depth) if states_at_depth else list(GOAL)
            self.canvas.update_grid(tuple(self.current_state))
            self.after(100, lambda: self.notebook.write_tab("Step Log", "LƯU Ý: 8-Puzzle là bài toán 1 người chơi (Single-agent). Việc áp dụng Minimax/Alpha-Beta ở đây là tạo ra một luật chơi giả định (2 người chơi luân phiên: MAX cố giải, MIN cố phá) chỉ nhằm mục đích minh họa cách duyệt cây đối kháng!"))
        else:
            self.canvas.update_grid(self.current_state)

    def _reset(self):
        self._stop_animation()
        self.current_state = list(GOAL)
        self.path = []
        self.current_step_idx = 0
        self.canvas.update_grid(self.current_state)
        self.notebook.clear_all()
        self.stats.reset_current()
        self.stats.update_stat("algo", self._algo_var.get())

    def _shuffle(self):
        self._reset()
        state = list(GOAL)
        for _ in range(14):
            state = list(random.choice(get_neighbors(tuple(state)))[0])
        self.current_state = state
        self._on_algo_change()

    def _stop_animation(self):
        self.is_animating = False
        if hasattr(self, '_btn_stop'):
            self._btn_stop.config(state="disabled")

    def _stop_algo(self):
        if self.is_running and hasattr(self, '_cancel_event'):
            self._cancel_event.set()
            self._btn_stop_algo.config(state="disabled")
            self._safe_log("StepLog: Đã gửi lệnh hủy tìm kiếm...")

    def _safe_log(self, text, tab="Step Log"):
        self.after(0, lambda: self.notebook.write_tab(tab, text))
        
    def _safe_log_routing(self, text):
        if text.startswith("Node: "):
            self._safe_log(text[6:], "Nodes")
        elif text.startswith("StepLog: "):
            self._safe_log(text[9:], "Step Log")
        elif text.startswith("Conditional Plan:"):
            # Strip "Conditional Plan:\n" if it's there, or just print it.
            # and_or_search.py sends: "Conditional Plan:\n..."
            content = text.replace("Conditional Plan:\n", "")
            if content == "Conditional Plan: FAILURE (Depth limit reached or no path)":
                self._safe_log("FAILURE (Depth limit reached or no path)", "Conditional Plan")
            else:
                self._safe_log(content, "Conditional Plan")
        else:
            self._safe_log(text, "Step Log")

    def _run(self):
        if self.is_running or self.is_animating: return
        self.is_running = True
        self._cancel_event = threading.Event()
        self._btn_run.config(state="disabled")
        self._btn_stop.config(state="disabled")
        self._btn_stop_algo.config(state="normal")
        self.notebook.clear_all()
        if hasattr(self.notebook, 'rename_tab_text'):
            self.notebook.rename_tab_text("Solution Path", "Solution Path")
        
        algo_name = self._algo_var.get()
        self.stats.update_stat("algo", algo_name)
        self.stats.update_status("Đang tìm kiếm...", "#F38BA8")
        
        try:
            param = int(self.param_entry.get())
        except:
            param = 35

        algo_cls = ALGORITHMS.get(algo_name)
        if not algo_cls:
            self.is_running = False
            self._btn_run.config(state="normal")
            return
            
        if algo_name == "Belief-State BFS":
            # Generate a belief state with 2 elements
            state1 = tuple(self.current_state)
            state2 = list(state1)
            for _ in range(5):
                state2 = list(random.choice(get_neighbors(tuple(state2)))[0])
            start_tuple = (state1, tuple(state2))
            self.canvas.update_grid(start_tuple)
        elif algo_name == "Partial Observation":
            # Hide 2 tiles
            st = list(self.current_state)
            hidden = 0
            for i in range(8, -1, -1):
                if st[i] != 0:
                    st[i] = -1
                    hidden += 1
                    if hidden == 2: break
            start_tuple = tuple(st)
            self.canvas.update_grid(start_tuple)
        else:
            start_tuple = tuple(self.current_state)
            self.canvas.update_grid(start_tuple)

        solver = algo_cls(start_tuple, param_val=param)
        
        threading.Thread(target=self._solve_thread, args=(solver,), daemon=True).start()

    def _solve_thread(self, solver):
        t0 = time.time()
        result_node, frontier, explored = solver.solve(log_callback=self._safe_log_routing, cancel_event=self._cancel_event)
        t1 = time.time()
        
        self.after(0, lambda: self._on_solve_done(result_node, frontier, explored, t1 - t0))

    def _on_solve_done(self, result_node, frontier, explored, time_taken):
        self.is_running = False
        self._btn_run.config(state="normal")
        self._btn_stop_algo.config(state="disabled")
        
        if self._cancel_event.is_set():
            self.stats.update_status(f"Đã hủy ({time_taken:.2f}s)", "#F38BA8")
        else:
            is_goal_reached = result_node and getattr(result_node, 'state', None) == tuple(GOAL)
            if is_goal_reached or self._algo_var.get() == "Partial Observation" or self._algo_var.get() == "Belief-State BFS":
                self.stats.update_status(f"Hoàn thành ({time_taken:.2f}s)")
            else:
                self.stats.update_status(f"Kẹt ở Local Max ({time_taken:.2f}s)", "#F59E0B")
                if hasattr(self.notebook, 'rename_tab_text'):
                    self.notebook.rename_tab_text("Solution Path", "Path to Local Max")
        if explored:
            self.stats.update_stat("explored", len(explored))
        if frontier:
            self.stats.update_stat("frontier", len(frontier))
        
        def format_state_row(states):
            if not states: return ""
            if isinstance(states[0], (list, tuple)) and isinstance(states[0][0], (list, tuple)):
                blocks = []
                for st in states:
                    formatted = [format_state_matrix(s).split('\n') for s in st]
                    rows = []
                    for i in range(3):
                        rows.append(" | ".join(f[i] for f in formatted))
                    blocks.append(rows)
                res_rows = []
                for i in range(3):
                    res_rows.append("    ".join(b[i] for b in blocks))
                return "\n".join(res_rows)
            else:
                blocks = [format_state_matrix(s).split('\n') for s in states]
                res_rows = []
                for i in range(3):
                    res_rows.append("    ".join(b[i] for b in blocks))
                return "\n".join(res_rows)

        def print_states(tab_name, state_list, limit=30):
            d_name = "Reached" if tab_name == "Frontier" and self._group_var.get() == "Informed Search" else tab_name
            self.notebook.write_tab(tab_name, f"{d_name} ({len(state_list)} states):")
            to_print = state_list[:limit]
            
            items_per_row = 6
            if to_print and isinstance(to_print[0], (list, tuple)) and isinstance(to_print[0][0], (list, tuple)):
                items_per_row = max(1, 10 // (len(to_print[0]) + 1))
                
            for i in range(0, len(to_print), items_per_row):
                chunk = to_print[i:i+items_per_row]
                self.notebook.write_tab(tab_name, format_state_row(chunk) + "\n")
            if len(state_list) > limit:
                self.notebook.write_tab(tab_name, f"... and {len(state_list)-limit} more")

        if frontier:
            print_states("Frontier", [f.state for f in frontier])
                
        if explored:
            print_states("Explored", list(explored))

        path = []
        curr = result_node
        while curr:
            path.append(curr)
            curr = getattr(curr, 'parent', None)
        path.reverse()
        
        self.path = path
        if path:
            self.stats.update_stat("path_cost", getattr(result_node, 'cost', 0))
            self.stats.update_stat("depth", getattr(result_node, 'depth', 0))
            self.notebook.render_solution_path(path)
            self._jump_to_step(0)
            self._start_animation()
        else:
            self.notebook.write_tab("Solution Path", "No path found or algorithm is a placeholder.")
            
    def _start_animation(self):
        if len(self.path) <= 1:
            return
        self.is_animating = True
        self._btn_stop.config(state="normal")
        self._animate_step()
        
    def _animate_step(self):
        if not self.is_animating: return
        
        next_step = self.current_step_idx + 1
        if next_step < len(self.path):
            self._jump_to_step(next_step)
            self.after(300, self._animate_step)
        else:
            self._stop_animation()

    def _jump_to_step(self, step_idx):
        if not self.path or step_idx < 0 or step_idx >= len(self.path): return
        self.current_step_idx = step_idx
        node = self.path[step_idx]
        
        highlight_idx = None
        next_action_str = ""
        if step_idx < len(self.path) - 1:
            next_node = self.path[step_idx + 1]
            next_action_str = getattr(next_node, 'action', '')
            if isinstance(next_node.state, (list, tuple)) and isinstance(next_node.state[0], int):
                highlight_idx = next_node.state.index(0)
        else:
            next_action_str = "GAME OVER"
            
        # Update board and pass highlight info
        if hasattr(self.canvas, 'update_grid') and 'highlight_idx' in self.canvas.update_grid.__code__.co_varnames:
            self.canvas.update_grid(node.state, highlight_idx=highlight_idx, turn_str=next_action_str)
        else:
            self.canvas.update_grid(node.state)
            
        action_str = getattr(node, 'action', 'Start') if getattr(node, 'action', None) else "Start"
        self.stats.update_stat("step", f"{step_idx} / {len(self.path)-1}")
        self.stats.update_stat("action", action_str)
        
        if hasattr(self.canvas, 'set_turn'):
            self.canvas.set_turn(next_action_str)
            
        self.notebook.highlight_step(step_idx)

    def _next_step(self):
        self._stop_animation()
        self._jump_to_step(self.current_step_idx + 1)
        
    def _prev_step(self):
        self._stop_animation()
        self._jump_to_step(self.current_step_idx - 1)


if __name__ == "__main__":
    app = EightPuzzleApp()
    app.mainloop()
