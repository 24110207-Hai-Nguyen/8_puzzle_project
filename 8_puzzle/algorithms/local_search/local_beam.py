import random
from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, value, GOAL

class LocalBeamSearch(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        k = self.param_val
        if log_callback: log_callback(f"StepLog: Beam width k = {k}")
        
        current_states = [Node(self.start_state, cost=0, depth=0)]
        
        if log_callback:
            log_callback(f"StepLog: Initial beam:")
            for ns in current_states:
                log_callback(f"StepLog:   {ns.name} (Value={value(ns.state)})")
                
        visited = {self.start_state}
        max_iters = 100
        iters = 0
                
        while iters < max_iters:
            iters += 1
            if cancel_event and cancel_event.is_set():
                break
            
            all_neighbors = []
            found_goal = None
            
            for node in current_states:
                for state, action in get_neighbors(node.state):
                    child = Node(state, node, action, node.cost+1, node.depth+1)
                    all_neighbors.append(child)
                    if state == GOAL:
                        found_goal = child
                        break
                if found_goal: break
                
            if found_goal:
                self.result_node = found_goal
                break
                
            all_neighbors.sort(key=lambda n: value(n.state), reverse=True)
            
            # Filter out visited states to prevent trivial loops
            unvisited_neighbors = [n for n in all_neighbors if n.state not in visited]
            
            if not unvisited_neighbors:
                if log_callback: log_callback("StepLog: Dead end reached (all neighbors visited).")
                self.result_node = current_states[0]
                break
                
            next_states = unvisited_neighbors[:k]
            for ns in next_states:
                visited.add(ns.state)
            
            if log_callback:
                log_callback(f"StepLog: Next beam (Iter {iters}):")
                for ns in next_states:
                    log_callback(f"StepLog:   {ns.name} (Value={value(ns.state)})")
                    log_callback(f"Node: Beam item: {ns.name}\n{format_state_matrix(ns.state)}")
                    
            current_states = next_states
            self.result_node = current_states[0] # Keep track of the best node so far
            
        return self.result_node, [], set()
