from .adversarial_search import AdversarialSearchBase, minimax_decision

class Minimax(AdversarialSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        max_depth = self.param_val if self.param_val else 5
        if log_callback: log_callback(f"StepLog: Running Minimax (MAX vs MIN) with max_depth={max_depth}...")
        pv = minimax_decision(self.start_state, max_depth, cancel_event)
        return self._process_pv(pv, log_callback)
