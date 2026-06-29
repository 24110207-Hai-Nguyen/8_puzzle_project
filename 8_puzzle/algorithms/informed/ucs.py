import heapq
from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, GOAL, format_state_matrix

class UCS(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        root_node = Node(self.start_state, cost=0, depth=0)
        pq = [(root_node.cost, id(root_node), root_node)]
        
        while pq:
            if cancel_event and cancel_event.is_set():
                break
            
            cost, _, node = heapq.heappop(pq)
            if log_callback: log_callback(f"Expanded: {node.name}")
            
            if node.state == GOAL:
                self.result_node = node
                break
                
            if node.state not in self.explored:
                self.explored.add(node.state)
                if node.depth < self.param_val:
                    for state, action in get_neighbors(node.state):
                        if state not in self.explored:
                            child = Node(state, node, action, node.cost + 1, node.depth + 1)
                            heapq.heappush(pq, (child.cost, id(child), child))
                            if log_callback:
                                log_callback(f"Node: {child.name} | parent={node.name} | action={action} | cost={child.cost}\n{format_state_matrix(state)}")
        
        self.frontier = [n for _, _, n in pq]
        return self.result_node, self.frontier, self.explored
