import random
from map_generator import GOAL, get_neighbors
from algorithms.base import PuzzleSearchBase, Node

def heuristic(state):
    if state == GOAL:
        return 1000
    dist = 0
    for i in range(9):
        if state[i] != 0:
            gx, gy = divmod(GOAL.index(state[i]), 3)
            sx, sy = divmod(i, 3)
            dist += abs(gx - sx) + abs(gy - sy)
    return -dist

OPPOSITES = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}

# --- MINIMAX ---
def minimax_decision(state, max_depth, cancel_event):
    v, action, pv = max_value(state, 0, max_depth, None, cancel_event)
    return pv

def max_value(state, depth, max_depth, prev_act, cancel_event):
    if cancel_event and cancel_event.is_set(): return -float('inf'), None, []
    if depth == max_depth or state == GOAL:
        return heuristic(state), None, []
        
    v = -float('inf')
    best_act = None
    best_pv = []
    
    for n_state, act in get_neighbors(state):
        if act == OPPOSITES.get(prev_act): continue
        v2, _, pv2 = min_value(n_state, depth + 1, max_depth, act, cancel_event)
        if v2 > v:
            v = v2
            best_act = act
            best_pv = [(act, n_state, 'MAX')] + pv2
            
    return v, best_act, best_pv

def min_value(state, depth, max_depth, prev_act, cancel_event):
    if cancel_event and cancel_event.is_set(): return float('inf'), None, []
    if depth == max_depth or state == GOAL:
        return heuristic(state), None, []
        
    v = float('inf')
    best_act = None
    best_pv = []
    
    for n_state, act in get_neighbors(state):
        if act == OPPOSITES.get(prev_act): continue
        v2, _, pv2 = max_value(n_state, depth + 1, max_depth, act, cancel_event)
        if v2 < v:
            v = v2
            best_act = act
            best_pv = [(act, n_state, 'MIN')] + pv2
            
    return v, best_act, best_pv


# --- ALPHA-BETA ---
def alpha_beta_search(state, max_depth, cancel_event):
    v, action, pv = ab_max_value(state, 0, max_depth, -float('inf'), float('inf'), None, cancel_event)
    return pv

def ab_max_value(state, depth, max_depth, alpha, beta, prev_act, cancel_event):
    if cancel_event and cancel_event.is_set(): return -float('inf'), None, []
    if depth == max_depth or state == GOAL:
        return heuristic(state), None, []
        
    v = -float('inf')
    best_act = None
    best_pv = []
    
    for n_state, act in get_neighbors(state):
        if act == OPPOSITES.get(prev_act): continue
        v2, _, pv2 = ab_min_value(n_state, depth + 1, max_depth, alpha, beta, act, cancel_event)
        if v2 > v:
            v = v2
            best_act = act
            best_pv = [(act, n_state, 'MAX')] + pv2
        if v >= beta:
            return v, best_act, best_pv
        alpha = max(alpha, v)
        
    return v, best_act, best_pv

def ab_min_value(state, depth, max_depth, alpha, beta, prev_act, cancel_event):
    if cancel_event and cancel_event.is_set(): return float('inf'), None, []
    if depth == max_depth or state == GOAL:
        return heuristic(state), None, []
        
    v = float('inf')
    best_act = None
    best_pv = []
    
    for n_state, act in get_neighbors(state):
        if act == OPPOSITES.get(prev_act): continue
        v2, _, pv2 = ab_max_value(n_state, depth + 1, max_depth, alpha, beta, act, cancel_event)
        if v2 < v:
            v = v2
            best_act = act
            best_pv = [(act, n_state, 'MIN')] + pv2
        if v <= alpha:
            return v, best_act, best_pv
        beta = min(beta, v)
        
    return v, best_act, best_pv


# --- EXPECTIMAX ---
def expectimax_search(state, max_depth, cancel_event):
    v, action, pv = exp_max_value(state, 0, max_depth, None, cancel_event)
    return pv

def exp_max_value(state, depth, max_depth, prev_act, cancel_event):
    if cancel_event and cancel_event.is_set(): return -float('inf'), None, []
    if depth == max_depth or state == GOAL:
        return heuristic(state), None, []
        
    v = -float('inf')
    best_act = None
    best_pv = []
    
    for n_state, act in get_neighbors(state):
        if act == OPPOSITES.get(prev_act): continue
        v2, pv2 = exp_value(n_state, depth + 1, max_depth, act, cancel_event)
        if v2 > v:
            v = v2
            best_act = act
            best_pv = [(act, n_state, 'MAX')] + pv2
            
    return v, best_act, best_pv

def exp_value(state, depth, max_depth, prev_act, cancel_event):
    if cancel_event and cancel_event.is_set(): return 0, []
    if depth == max_depth or state == GOAL:
        return heuristic(state), []
        
    neighbors = [(s, a) for s, a in get_neighbors(state) if a != OPPOSITES.get(prev_act)]
    if not neighbors:
        return heuristic(state), []
        
    v = 0
    prob = 1.0 / len(neighbors)
    best_pv = []
    max_v2 = -float('inf')
    
    for n_state, act in neighbors:
        v2, _, pv2 = exp_max_value(n_state, depth + 1, max_depth, act, cancel_event)
        v += prob * v2
        if v2 > max_v2:
            max_v2 = v2
            best_pv = [(act, n_state, 'CHANCE')] + pv2
            
    return v, best_pv


# --- BASE CLASS ---
class AdversarialSearchBase(PuzzleSearchBase):
    def _process_pv(self, pv, log_callback):
        if not pv:
            if log_callback: log_callback("StepLog: No path found or depth limit is 0.")
            return None, [], set()
            
        curr = Node(self.start_state)
        curr.depth = 0
        curr.cost = 0
        
        for act, n_state, player in pv:
            if log_callback: log_callback(f"StepLog: [{player}] predicted action: {act}")
            child = Node(n_state, curr, act, curr.cost + 1)
            child.depth = curr.depth + 1
            child.action = f"[{player}] {act}"
            curr = child
            
        if log_callback: log_callback("StepLog: Principal Variation (PV) extracted successfully.")
        return curr, [], set()
