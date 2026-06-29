from algorithms.csp.csp_solver import CSP, min_conflicts, CSPSearchBase

class MinConflicts(CSPSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        max_steps = self.param_val if self.param_val else 3
        csp = CSP(self.start_state, max_steps)
        csp.log_callback = log_callback
        csp.cancel_event = cancel_event
        
        assignment = min_conflicts(csp, max_steps=1000)
        return self._process_result(assignment, max_steps, log_callback)
