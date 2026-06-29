from map_generator import GOAL, get_neighbors

class DummyNode:
    def __init__(self, state):
        self.state = state
        self.parent = None
        self.action = "Conditional Plan (See Tab)"
        self.cost = 0
        self.depth = 0

def results(state, action):
    # Non-deterministic action:
    # 1. Action succeeds
    # 2. Action fails (slippery, state remains the same)
    for n_state, n_action in get_neighbors(state):
        if n_action == action:
            return {"success": n_state, "fail": state}
    return {"fail": state}

class AndOrGraphSearch:
    def __init__(self, start_state, param_val=None):
        self.start_state = start_state
        if isinstance(start_state[0], (list, tuple)):
            self.start_state = start_state[0] # Take first if it's a belief state
        self.max_depth = param_val if param_val else 5
        self.log = None

    def solve(self, log_callback=None, cancel_event=None):
        self.log = log_callback
        
        plan = self.or_search(self.start_state, [], 0, cancel_event)
        
        if plan == "failure":
            if log_callback: log_callback("Conditional Plan: FAILURE (Depth limit reached or no path)")
            return None, [], []
            
        # Format the plan
        plan_str = self.format_plan(plan)
        if log_callback:
            log_callback(f"Conditional Plan:\n{plan_str}")
            
        dummy = DummyNode(GOAL)
        dummy.action = "Plan Generated (See Conditional Plan tab)"
        return dummy, [], []

    def or_search(self, state, path, depth, cancel_event):
        if cancel_event and cancel_event.is_set():
            return "failure"
        if state == GOAL:
            return []
        if state in path:
            return f"LOOP (Retry action)"
        if depth >= self.max_depth:
            return "failure"
            
        for action in ['Up', 'Down', 'Left', 'Right']:
            next_states_dict = results(state, action)
            
            # If the action is illegal, it only returns fail, which is a guaranteed infinite loop.
            if len(next_states_dict) == 1 and "fail" in next_states_dict:
                continue
                
            plan = self.and_search(next_states_dict, path + [state], depth + 1, cancel_event)
            if plan != "failure":
                return [action, plan]
        return "failure"
        
    def and_search(self, states_dict, path, depth, cancel_event):
        if cancel_event and cancel_event.is_set():
            return "failure"
        plan_dict = {}
        for outcome, s in states_dict.items():
            plan = self.or_search(s, path, depth, cancel_event)
            if plan == "failure":
                return "failure"
            plan_dict[outcome] = plan
        return plan_dict

    def format_plan(self, plan, indent=""):
        if not plan:
            return indent + "Goal Reached!\n"
        if isinstance(plan, str):
            # This handles "LOOP (Retry action)"
            return indent + plan + "\n"
        if isinstance(plan, list):
            action, and_plan = plan
            res = indent + f"Action: {action}\n"
            res += self.format_plan(and_plan, indent + "  ")
            return res
        if isinstance(plan, dict):
            res = ""
            for outcome, subplan in plan.items():
                if outcome == "success":
                    res += indent + f"If tile moves successfully:\n"
                else:
                    res += indent + f"If state remains unchanged:\n"
                res += self.format_plan(subplan, indent + "  ")
            return res
        return ""
