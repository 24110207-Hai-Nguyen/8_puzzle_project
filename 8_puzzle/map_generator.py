import random
from itertools import permutations

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

def count_inversions(state):
    inv = 0
    for i in range(9):
        for j in range(i+1, 9):
            if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                inv += 1
    return inv

def is_solvable(state):
    return count_inversions(state) % 2 == 0

def get_neighbors(state):
    idx = state.index(0)
    row, col = divmod(idx, 3)
    moves = [(-1, 0, 'Up'), (1, 0, 'Down'), (0, -1, 'Left'), (0, 1, 'Right')]
    neighbors = []
    for dr, dc, move in moves:
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            new_idx = r * 3 + c
            new_state = list(state)
            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
            neighbors.append((tuple(new_state), move))
    return neighbors

def generate_random_solvable_states(num):
    states = []
    while len(states) < num:
        state = list(GOAL)
        for _ in range(30):
            nbs = get_neighbors(tuple(state))
            state = list(random.choice(nbs)[0])
        if is_solvable(state) and tuple(state) not in states:
            states.append(tuple(state))
    return states

def format_state_matrix(state):
    rows = []
    for i in range(3):
        row = [str(x) if x != 0 else "_" for x in state[i*3:(i+1)*3]]
        rows.append(" " + " ".join(row))
    return "\n".join(rows)

def heuristic(state):
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != GOAL[i])

def value(state):
    return 9 - heuristic(state)
