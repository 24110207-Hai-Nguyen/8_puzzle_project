import collections
from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, GOAL

class BFS(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        root_node = Node(self.start_state, cost=0, depth=0)
        queue = collections.deque([root_node])
        self.explored.add(self.start_state)
        
        while queue:
            if cancel_event and cancel_event.is_set():
                break
            
            node = queue.popleft()
            if log_callback: log_callback(f"Expanded: {node.name}")
            
            if node.state == GOAL:
                self.result_node = node
                break
                
            for state, action in get_neighbors(node.state):
                if state not in self.explored and node.depth < self.param_val:
                    self.explored.add(state)
                    child = Node(state, node, action, node.cost + 1, node.depth + 1)
                    queue.append(child)
                    if log_callback:
                        log_callback(f"Node: {child.name} | parent={node.name} | action={action} | depth={child.depth}\n{format_state_matrix(state)}")
        
        self.frontier = list(queue)
        return self.result_node, self.frontier, self.explored
