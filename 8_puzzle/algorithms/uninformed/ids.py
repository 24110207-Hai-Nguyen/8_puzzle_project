from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, GOAL

class IDS(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        max_depth_limit = self.param_val
        final_explored = set()
        root_node = Node(self.start_state, cost=0, depth=0)
        
        for depth_limit in range(1, max_depth_limit + 1):
            if cancel_event and cancel_event.is_set():
                break
            
            if log_callback: log_callback(f"StepLog: Trying depth limit = {depth_limit}")
            visited_depth = {self.start_state: 0}
            stack = [(root_node, 0)]
            found = False
            
            while stack:
                if cancel_event and cancel_event.is_set():
                    break
                
                node, d = stack.pop()
                final_explored.add(node.state)
                
                if node.state == GOAL:
                    self.result_node = node
                    found = True
                    break
                    
                if d < depth_limit:
                    for state, action in get_neighbors(node.state):
                        if state not in visited_depth or visited_depth[state] > d + 1:
                            visited_depth[state] = d + 1
                            child = Node(state, node, action, node.cost + 1, d + 1)
                            stack.append((child, d + 1))
                            if log_callback:
                                log_callback(f"Node: {child.name} | parent={node.name} | action={action} | d={d+1}\n{format_state_matrix(state)}")
            
            if found:
                break
                
        self.explored = final_explored
        self.frontier = [n for n, _ in stack] if not self.result_node else []
        return self.result_node, self.frontier, self.explored
