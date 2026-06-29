from map_generator import GOAL, heuristic

class Node:
    _id_counter = 65
    def __init__(self, state, parent=None, action=None, cost=0, depth=0, h_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = depth
        self.h_cost = h_cost
        self.f_cost = cost + h_cost
        if parent is None:
            self.name = "A"
        else:
            self.name = chr(Node._id_counter)
            Node._id_counter += 1
            if Node._id_counter > 90:
                Node._id_counter = 65
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost

class PuzzleSearchBase:
    """Base class for puzzle algorithms."""
    def __init__(self, start_state, param_val=35):
        self.start_state = start_state
        self.param_val = param_val
        self.explored = set()
        self.frontier = []
        self.result_node = None
        self.nodes_log = []
        self.step_log = []
        
        Node._id_counter = 65
        
    def solve(self, log_callback=None, cancel_event=None):
        raise NotImplementedError

class ComplexProblem:
    def __init__(self, initial_belief, goal_test, actions_func, results_func):
        self.initial_belief = initial_belief
        self.goal_test = goal_test
        self.actions = actions_func
        self.results = results_func
    
    def is_goal(self, state):
        return self.goal_test(state)
