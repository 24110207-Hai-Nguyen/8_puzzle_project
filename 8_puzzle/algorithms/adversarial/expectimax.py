from .adversarial_search import AdversarialSearchBase, expectimax_search

class Expectimax(AdversarialSearchBase):
    def solve(self, log_callback=None, cancel_event=None):
        max_depth = self.param_val if self.param_val else 5
        if log_callback: log_callback(f"StepLog: Running Expectimax (MAX vs CHANCE) with max_depth={max_depth}...")
        pv = expectimax_search(self.start_state, max_depth, cancel_event)
        return self._process_pv(pv, log_callback)
