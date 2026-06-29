import random
import math
from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, value, GOAL

class SimulatedAnnealing(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        max_iters = int(getattr(self, 'param_val', 100)) * 100
        if max_iters < 100: max_iters = 10000
        
        max_restarts = 15
        
        for attempt in range(max_restarts):
            current_node = Node(self.start_state, cost=0, depth=0)
            
            for t in range(1, max_iters + 1):
                if cancel_event and cancel_event.is_set():
                    self.result_node = current_node
                    return self.result_node, [], set()
                
                T = float(max_iters) / t
                if T == 0:
                    break
                    
                if current_node.state == GOAL:
                    self.result_node = current_node
                    if log_callback and attempt > 0:
                        log_callback(f"StepLog: Goal found on restart attempt {attempt+1}!")
                    return self.result_node, [], set()
                    
                neighbors = get_neighbors(current_node.state)
                next_state, action = random.choice(neighbors)
                if log_callback and attempt == 0 and t < 10:
                    log_callback(f"Node: Neighbor: action={action}, value={value(next_state)}\n{format_state_matrix(next_state)}")
                    
                delta_e = value(next_state) - value(current_node.state)
                if delta_e > 0 or random.random() < math.exp(delta_e / T):
                    current_node = Node(next_state, current_node, action, current_node.cost+1, current_node.depth+1)
                    if log_callback and attempt == 0 and t < 10:
                        log_callback(f"StepLog:   -> Move to {action} (Value={value(next_state)})")
                        
            if log_callback:
                log_callback(f"StepLog: Local max reached, restarting (attempt {attempt+1}/{max_restarts})...")
                
        self.result_node = current_node
        return self.result_node, [], set()
