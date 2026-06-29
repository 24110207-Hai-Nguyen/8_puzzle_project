import random
from map_generator import GOAL, get_neighbors

def get_action_result(state, action):
    if action == 'Stay':
        return state
    for n_state, n_action in get_neighbors(state):
        if n_action == action:
            return n_state
    return None

class CSP:
    def __init__(self, start_state, max_steps):
        self.start_state = start_state
        self.variables = list(range(max_steps))
        self.domains = {var: ['Up', 'Down', 'Left', 'Right', 'Stay'] for var in self.variables}
        self.max_steps = max_steps
        self.log_callback = None
        self.cancel_event = None

    def log(self, text):
        if self.log_callback:
            self.log_callback(text)

    def is_cancelled(self):
        return self.cancel_event and self.cancel_event.is_set()

    def get_state(self, assignment):
        state = self.start_state
        for i in range(len(assignment)):
            if i not in assignment:
                break
            action = assignment[i]
            next_state = get_action_result(state, action)
            if next_state is None:
                return None
            state = next_state
        return state

    def check_constraints(self, var, value, assignment):
        temp = assignment.copy()
        temp[var] = value
        
        # Binary constraint: no reverse
        if var > 0 and (var - 1) in assignment:
            prev_val = assignment[var - 1]
            opposites = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
            if value == opposites.get(prev_val):
                return False
            if prev_val == 'Stay' and value != 'Stay':
                return False

        # Validity constraint (Sequential)
        is_contiguous = all(i in temp for i in range(var + 1))
        if is_contiguous:
            state = self.start_state
            for i in range(var + 1):
                act = temp[i]
                if act == 'Stay' and state != GOAL:
                    return False
                if act != 'Stay' and state == GOAL:
                    return False
                    
                n_state = get_action_result(state, act)
                if n_state is None:
                    return False
                state = n_state
                
        # Global constraint
        if len(temp) == self.max_steps:
            if self.get_state(temp) != GOAL:
                return False
                
        return True


# 1. Backtracking Search
def select_unassigned_variable(assignment, csp):
    for var in csp.variables:
        if var not in assignment:
            return var
    return None

def backtracking_search(csp):
    return recursive_backtracking({}, csp)

def recursive_backtracking(assignment, csp):
    if csp.is_cancelled(): return "failure"
    if len(assignment) == csp.max_steps:
        return assignment
    
    var = select_unassigned_variable(assignment, csp)
    for value in csp.domains[var]:
        if csp.check_constraints(var, value, assignment):
            assignment[var] = value
            csp.log(f"StepLog: [Backtracking] Assign var {var} = {value}")
            result = recursive_backtracking(assignment, csp)
            if result != "failure":
                return result
            del assignment[var]
    return "failure"


# 2. Forward Checking Search
def forward_checking_search(csp):
    return fc_recursive({}, csp)

def fc_recursive(assignment, csp):
    if csp.is_cancelled(): return "failure"
    if len(assignment) == csp.max_steps:
        return assignment
        
    var = select_unassigned_variable(assignment, csp)
    for value in list(csp.domains[var]):
        if csp.check_constraints(var, value, assignment):
            assignment[var] = value
            csp.log(f"StepLog: [FC] Assign var {var} = {value}")
            
            removals = []
            failed = False
            for unassigned in csp.variables:
                if unassigned not in assignment:
                    for val in list(csp.domains[unassigned]):
                        if not csp.check_constraints(unassigned, val, assignment):
                            csp.domains[unassigned].remove(val)
                            removals.append((unassigned, val))
                            csp.log(f"StepLog: [FC] Pruned var {unassigned} = {val}")
                    
                    if len(csp.domains[unassigned]) == 0:
                        failed = True
                        break
            
            if not failed:
                result = fc_recursive(assignment, csp)
                if result != "failure":
                    return result
            
            del assignment[var]
            for u, val in removals:
                csp.domains[u].append(val)
                
    return "failure"


# 3. AC-3
def check_binary(xi, x, xj, y):
    opposites = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
    if xi == xj - 1 or xj == xi - 1:
        if x == opposites.get(y):
            return False
        
        if xi == xj - 1:
            if x == 'Stay' and y != 'Stay': return False
        if xj == xi - 1:
            if y == 'Stay' and x != 'Stay': return False
            
    return True

def rm_inconsistent_values(xi, xj, csp):
    removed = False
    for x in list(csp.domains[xi]):
        has_support = False
        for y in csp.domains[xj]:
            if check_binary(xi, x, xj, y):
                has_support = True
                break
        if not has_support:
            csp.domains[xi].remove(x)
            removed = True
            csp.log(f"StepLog: [AC-3] Pruned var {xi} = {x}")
    return removed

def ac3(csp):
    queue = []
    for i in range(csp.max_steps - 1):
        queue.append((i, i+1))
        queue.append((i+1, i))
        
    while queue:
        if csp.is_cancelled(): return False
        xi, xj = queue.pop(0)
        if rm_inconsistent_values(xi, xj, csp):
            if len(csp.domains[xi]) == 0:
                return False
            for xk in csp.variables:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))
    return True

def ac3_search(csp):
    csp.log("StepLog: Running AC-3 to filter domains...")
    success = ac3(csp)
    if not success:
        csp.log("StepLog: AC-3 found no consistent domains.")
        return "failure"
    csp.log("StepLog: AC-3 finished. Proceeding with Backtracking...")
    return backtracking_search(csp)


# 4. Min-Conflicts
def count_conflicts(var, val, assignment, csp):
    temp = assignment.copy()
    temp[var] = val
    
    state = csp.start_state
    illegal_moves = 0
    reverses = 0
    
    for i in range(csp.max_steps):
        action = temp[i]
        if i > 0 and action == {'Up':'Down','Down':'Up','Left':'Right','Right':'Left'}.get(temp[i-1]):
            reverses += 1
            
        if state is not None:
            if action == 'Stay' and state != GOAL:
                illegal_moves += 1
            elif action != 'Stay' and state == GOAL:
                illegal_moves += 1
                
            n_state = get_action_result(state, action)
            if n_state is None:
                illegal_moves += 1
                state = None
            else:
                state = n_state
        else:
            illegal_moves += 1
            
    dist = 0
    if state is not None:
        for i in range(9):
            if state[i] != 0:
                gx, gy = divmod(GOAL.index(state[i]), 3)
                sx, sy = divmod(i, 3)
                dist += abs(gx - sx) + abs(gy - sy)
    else:
        dist = 100
        
    return illegal_moves * 50 + reverses * 10 + dist

def get_conflicted_vars(assignment, csp):
    conflicts = set()
    state = csp.start_state
    
    for i in range(csp.max_steps):
        action = assignment[i]
        if i > 0 and action == {'Up':'Down','Down':'Up','Left':'Right','Right':'Left'}.get(assignment[i-1]):
            conflicts.add(i)
            conflicts.add(i-1)
            
        if state is not None:
            if action == 'Stay' and state != GOAL:
                conflicts.add(i)
            elif action != 'Stay' and state == GOAL:
                conflicts.add(i)
                
            n_state = get_action_result(state, action)
            if n_state is None:
                conflicts.add(i)
                state = None
            else:
                state = n_state
        else:
            conflicts.add(i)
            
    if state != GOAL:
        if not conflicts:
            return list(range(csp.max_steps))
            
    return list(conflicts)

def min_conflicts(csp, max_steps=2000):
    current = {}
    for var in csp.variables:
        current[var] = random.choice(csp.domains[var])
        
    for i in range(max_steps):
        if csp.is_cancelled(): return "failure"
        
        conflicted_vars = get_conflicted_vars(current, csp)
        if not conflicted_vars and csp.get_state(current) == GOAL:
            return current
            
        if not conflicted_vars:
            conflicted_vars = list(range(csp.max_steps))
            
        var = random.choice(conflicted_vars)
        
        min_c = float('inf')
        best_vals = []
        for val in csp.domains[var]:
            c = count_conflicts(var, val, current, csp)
            if c < min_c:
                min_c = c
                best_vals = [val]
            elif c == min_c:
                best_vals.append(val)
                
        val = random.choice(best_vals)
        current[var] = val
        if i % 100 == 0:
            csp.log(f"StepLog: [Min-Conflicts] Iteration {i}, Var {var} -> {val}, Conflicts/Cost -> {min_c}")
            
    return "failure"

from algorithms.base import PuzzleSearchBase, Node

class CSPSearchBase(PuzzleSearchBase):
    def _process_result(self, assignment, max_steps, log_callback):
        if assignment == "failure" or not assignment:
            if log_callback: log_callback("StepLog: CSP failed to find a valid assignment of actions.")
            return None, [], set()
            
        curr = Node(self.start_state)
        curr.depth = 0
        curr.cost = 0
        
        for i in range(max_steps):
            action = assignment[i]
            if action == 'Stay':
                continue
            n_state = get_action_result(curr.state, action)
            child = Node(n_state, curr, action, curr.cost + 1)
            child.depth = curr.depth + 1
            curr = child
            
        if log_callback: log_callback("StepLog: CSP successfully found a valid assignment!")
        return curr, [], set()
