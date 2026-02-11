# core/processor.py

class CsvProcessor:
    def __init__(self, rules, logger=None):
        self.rules = rules
        self.logger = logger

    def execute(self, df):
        result = df
        for index, rule in enumerate(self.rules, start=1):
            before = len(result)
            if self.logger:
                self.logger(f"[{index}] {rule.description()}")
            result = rule.apply(result)
            after = len(result)
            if self.logger:
                self.logger(f"件数: {before} → {after}\n")
        return result
