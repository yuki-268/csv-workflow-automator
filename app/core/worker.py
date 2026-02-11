import pandas as pd
from PySide6.QtCore import QObject, Signal

class Worker(QObject):
    finished = Signal(pd.DataFrame)
    progress = Signal(int)

    def __init__(self, df, rules):
        super().__init__()
        self.df = df
        self.rules = rules

    def run(self):
        result = self.df
        total = len(self.rules)

        for i, rule in enumerate(self.rules):
            result = rule.apply(result)
            percent = int((i+1)/total*100)
            self.progress.emit(percent)

        self.finished.emit(result)
