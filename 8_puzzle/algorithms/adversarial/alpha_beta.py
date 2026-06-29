from .adversarial_search import AdversarialSearchBase, alpha_beta_search

class AlphaBeta(AdversarialSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        max_depth = self.param_val if self.param_val else 5
        if log_callback: log_callback(f"StepLog: Running Alpha-Beta Pruning with max_depth={max_depth}...")
        pv = alpha_beta_search(self.start_state, max_depth, cancel_event)
        return self._process_pv(pv, log_callback)
