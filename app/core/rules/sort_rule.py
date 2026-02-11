from .base_rule import BaseRule

class SortRule(BaseRule):

    def __init__(self, column, ascending=True):
        self.column = column
        self.ascending = ascending

    def apply(self, df):
        return df.sort_values(by=self.column, ascending=self.ascending)

    def description(self):
        order = "昇順" if self.ascending else "降順"
        return f"並び替え: {self.column} ({order})"

    def to_dict(self):
        return {
            "type": "sort",
            "column": self.column,
            "ascending": self.ascending
        }

    @staticmethod
    def from_dict(data):
        return SortRule(data["column"], data["ascending"])
