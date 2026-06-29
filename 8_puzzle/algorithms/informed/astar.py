import heapq
from algorithms.base import PuzzleSearchBase, Node
from map_generator import get_neighbors, format_state_matrix, heuristic, GOAL

class AStar(PuzzleSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        h = heuristic(self.start_state)
        root_node = Node(self.start_state, cost=0, depth=0, h_cost=h)
        frontier = [(root_node.f_cost, id(root_node), root_node)]
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
                g_new = node.cost + 1
                h_val = heuristic(state)
                
                if state in reached:
                    old_node = reached[state]
                    if g_new < old_node.cost:
                        old_node.cost = g_new
                        old_node.h_cost = h_val
                        old_node.f_cost = g_new + h_val
                        old_node.parent = node
                        old_node.action = action
                        old_node.depth = node.depth + 1
                        heapq.heappush(frontier, (old_node.f_cost, id(old_node), old_node))
                else:
                    child = Node(state, node, action, g_new, node.depth + 1, h_cost=h_val)
                    reached[state] = child
                    heapq.heappush(frontier, (child.f_cost, id(child), child))
                    if log_callback:
                        log_callback(f"Node: {child.name} | g={child.cost} h={child.h_cost} f={child.f_cost}\n{format_state_matrix(state)}")
        
        self.frontier = [n for _, _, n in frontier]
        self.explored = set(reached.keys())
        return self.result_node, self.frontier, self.explored
