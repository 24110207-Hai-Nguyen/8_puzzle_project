from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, GOAL

class DFS(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        root_node = Node(self.start_state, cost=0, depth=0)
        stack = [root_node]
        self.explored = set()
        visited_depth = {self.start_state: 0}
        
        while stack:
            if cancel_event and cancel_event.is_set():
                break
            
            node = stack.pop()
            self.explored.add(node.state)
            if log_callback: log_callback(f"Expanded: {node.name}")
            
            if node.state == GOAL:
                self.result_node = node
                break
                
            if node.depth < self.param_val:
                for state, action in get_neighbors(node.state):
                    if state not in visited_depth or visited_depth[state] > node.depth + 1:
                        visited_depth[state] = node.depth + 1
                        child = Node(state, node, action, node.cost + 1, node.depth + 1)
                        stack.append(child)
                        if log_callback:
                            log_callback(f"Node: {child.name} | parent={node.name} | action={action} | depth={child.depth}\n{format_state_matrix(state)}")
        
        self.frontier = stack
        return self.result_node, self.frontier, self.explored
