import random
from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, value, GOAL

class StochasticHillClimbing(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        current_node = Node(self.start_state, cost=0, depth=0)
        if log_callback:
            log_callback(f"StepLog: Start: {format_state_matrix(current_node.state)} (Value={value(current_node.state)})")
            
        while True:
            if cancel_event and cancel_event.is_set():
                break
            
            if current_node.state == GOAL:
                self.result_node = current_node
                break
                
            better_neighbors = []
            current_value = value(current_node.state)
            
            for state, action in get_neighbors(current_node.state):
                v = value(state)
                if log_callback:
                    log_callback(f"Node: Neighbor: action={action}, value={v}\n{format_state_matrix(state)}")
                if v > current_value:
                    better_neighbors.append((state, action, v))
                    
            if better_neighbors:
                # Stochastic: Pick randomly among better neighbors
                state, action, v = random.choice(better_neighbors)
                current_node = Node(state, current_node, action, current_node.cost+1, current_node.depth+1)
                if log_callback:
                    log_callback(f"StepLog:   -> Move randomly to (Value={v})")
            else:
                if log_callback: log_callback(f"StepLog: Local maximum at {current_node.name}")
                self.result_node = current_node
                break
                
        return self.result_node, [], set()
