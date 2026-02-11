from .base_rule import BaseRule

class DropColumnRule(BaseRule):

    def __init__(self, columns):
        self.columns = columns  # ここはリストで受け取る

    def apply(self, df):
        return df.drop(columns=self.columns, errors="ignore")

    def description(self):
        return f"列削除: {', '.join(self.columns)}"

    def to_dict(self):
        return {
            "type": "drop_column",
            "columns": self.columns
        }

    @staticmethod
    def from_dict(data):
        return DropColumnRule(data["columns"])
