from .uninformed.bfs import BFS
from .uninformed.dfs import DFS
from .uninformed.ids import IDS
from .informed.gbfs import GreedyBestFirstSearch
from .informed.astar import AStar
from .informed.ucs import UCS
from .local_search.simple_hill_climbing import SimpleHillClimbing
from .local_search.steepest_ascent_hill_climbing import SteepestAscentHillClimbing
from .local_search.stochastic_hill_climbing import StochasticHillClimbing
from .local_search.simulated_annealing import SimulatedAnnealing
from .local_search.local_beam import LocalBeamSearch
from .complex.belief_state_bfs import BeliefStateBFS
from .complex.partial_observation import PartialObservationSearch
from .complex.and_or_search import AndOrGraphSearch
from .csp.backtracking import Backtracking
from .csp.forward_checking import ForwardChecking
from .csp.ac3 import AC3
from .csp.min_conflicts import MinConflicts
from .adversarial.minimax import Minimax
from .adversarial.alpha_beta import AlphaBeta
from .adversarial.expectimax import Expectimax

ALGORITHMS = {
    "BFS": BFS,
    "DFS": DFS,
    "IDS": IDS,
    "Greedy Best-First": GreedyBestFirstSearch,
    "A*": AStar,
    "UCS": UCS,
    "Simple Hill Climbing": SimpleHillClimbing,
    "Steepest-Ascent Hill Climbing": SteepestAscentHillClimbing,
    "Stochastic Hill Climbing": StochasticHillClimbing,
    "Simulated Annealing": SimulatedAnnealing,
    "Local Beam Search (k=3)": LocalBeamSearch,
    "Belief-State BFS": BeliefStateBFS,
    "Partial Observation": PartialObservationSearch,
    "AND-OR Graph Search": AndOrGraphSearch,
    "CSP: Backtracking": Backtracking,
    "CSP: Forward Checking": ForwardChecking,
    "CSP: AC-3": AC3,
    "CSP: Min-Conflicts": MinConflicts,
    "Backtracking": Backtracking, # Legacy alias
    "Forward Checking": ForwardChecking, # Legacy alias
    "Minimax (Tic-Tac-Toe)": Minimax, # Legacy alias
    "Alpha-Beta (Tic-Tac-Toe)": AlphaBeta, # Legacy alias
    "Minimax": Minimax,
    "Alpha-Beta Pruning": AlphaBeta,
    "Expectimax": Expectimax
}
