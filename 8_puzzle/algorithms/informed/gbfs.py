import heapq
from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, heuristic, GOAL

class GreedyBestFirstSearch(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        h = heuristic(self.start_state)
        root_node = Node(self.start_state, cost=0, depth=0, h_cost=h)
        frontier = [(root_node.h_cost, id(root_node), root_node)]
        reached = {self.start_state: root_node}
        
        while frontier:
            if cancel_event and cancel_event.is_set():
                break
            
            _, _, node = heapq.heappop(frontier)
            if log_callback: log_callback(f"Expanded: {node.name}")
            
            if node.state == GOAL:
                self.result_node = node
                break
                
            for state, action in get_neighbors(node.state):
                h_val = heuristic(state)
                child = Node(state, node, action, node.cost + 1, node.depth + 1, h_cost=h_val)
                if state not in reached:
                    reached[state] = child
                    heapq.heappush(frontier, (child.h_cost, id(child), child))
                    if log_callback:
                        log_callback(f"Node: {child.name} | parent={node.name} | h={child.h_cost}\n{format_state_matrix(state)}")
        
        self.frontier = [n for _, _, n in frontier]
        self.explored = set(reached.keys())
        return self.result_node, self.frontier, self.explored
