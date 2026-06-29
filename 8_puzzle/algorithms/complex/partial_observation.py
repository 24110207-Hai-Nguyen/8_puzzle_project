import itertools
from .belief_state_bfs import BeliefStateBFS
from map_generator import is_solvable

def generate_belief_state(partial_state):
    # partial_state is a tuple where unknown tiles are -1
    # Example: (1, 2, 3, 4, 5, 6, -1, -1, 0)
    
    missing_tiles = set(range(9)) - set(partial_state)
    missing_tiles.discard(-1)
    
    missing_tiles = list(missing_tiles)
    unknown_indices = [i for i, val in enumerate(partial_state) if val == -1]
    
    belief_state = []
    
    for perm in itertools.permutations(missing_tiles):
        state = list(partial_state)
        for idx, val in zip(unknown_indices, perm):
            state[idx] = val
        if is_solvable(state):
            belief_state.append(tuple(state))
        
    return tuple(belief_state)

class PartialObservationSearch:
    def __init__(self, partial_state, param_val=None):
        self.start_belief_state = generate_belief_state(partial_state)
        self.bfs_solver = BeliefStateBFS(self.start_belief_state, param_val)
        
    def solve(self, log_callback=None, cancel_event=None):
        if log_callback:
            log_callback(f"StepLog: Initial partial state: {self.start_belief_state}")
        return self.bfs_solver.solve(log_callback, cancel_event)
