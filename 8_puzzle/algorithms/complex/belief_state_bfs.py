import time
from collections import deque
from map_generator import GOAL, get_neighbors

class Node:
    def __init__(self, state, parent=None, action=None, cost=0):
        self.state = state  # state is a tuple of 8-puzzle states (belief state)
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = 0 if parent is None else parent.depth + 1

def apply_action(single_state, action):
    # Standard actions: Up, Down, Left, Right
    for n_state, n_action in get_neighbors(single_state):
        if n_action == action:
            return n_state
    
    # If action is illegal, return the same state (wall-bumping semantics)
    return single_state

class BeliefStateBFS:
    def __init__(self, start_belief_state, param_val=None):
        # Keep duplicates so the UI shows a constant number of boards
        self.start_belief_state = tuple(sorted(start_belief_state))

    def solve(self, log_callback=None, cancel_event=None):
        start_node = Node(self.start_belief_state)
        
        # Check if goal is achieved for ALL states in the initial belief state
        if all(s == GOAL for s in self.start_belief_state):
            return start_node, [], set()

        frontier = deque([start_node])
        explored = set()
        explored.add(self.start_belief_state)
        
        actions = ['Up', 'Down', 'Left', 'Right']
        
        nodes_expanded = 0
        
        while frontier:
            if cancel_event and cancel_event.is_set():
                return None, list(frontier), explored
                
            node = frontier.popleft()
            nodes_expanded += 1
            
            if log_callback and nodes_expanded % 100 == 0:
                log_callback(f"StepLog: Expanded {nodes_expanded} belief states...")
            
            for action in actions:
                # Apply action without removing duplicates to maintain board count in UI
                next_belief_list = [apply_action(s, action) for s in node.state]
                next_belief = tuple(sorted(next_belief_list))
                
                if next_belief not in explored:
                    # Collapse to 1 state only when reaching the goal
                    if all(s == GOAL for s in next_belief):
                        child = Node((GOAL,), node, action, node.cost + 1)
                        if log_callback:
                            log_callback(f"StepLog: Goal found after {nodes_expanded} expansions!")
                        return child, list(frontier), explored
                        
                    child = Node(next_belief, node, action, node.cost + 1)
                    explored.add(next_belief)
                    frontier.append(child)
                    
        return None, list(frontier), explored
