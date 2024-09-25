from misc.config import load_cfg
class RegEval:
    def __init__(self, cfg_path):
        self.cfg = load_cfg(cfg_path)

    def evaluate(self):
        pass
    def print_result(self):
        pass