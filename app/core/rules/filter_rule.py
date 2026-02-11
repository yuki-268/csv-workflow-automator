from .base_rule import BaseRule

class FilterRule(BaseRule):

    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value

    def apply(self, df):
        if self.operator == "==":
            return df[df[self.column] == self.value]
        elif self.operator == "!=":
            return df[df[self.column] != self.value]
        elif self.operator == ">":
            return df[df[self.column] > self.value]
        elif self.operator == "<":
            return df[df[self.column] < self.value]
        elif self.operator == "contains":
            return df[df[self.column].astype(str).str.contains(str(self.value), na=False)]
        else:
            return df

    def description(self):
        return f"フィルタ: {self.column} {self.operator} {self.value}"

    def to_dict(self):
        return {
            "type": "filter",
            "column": self.column,
            "operator": self.operator,
            "value": self.value
        }

    @staticmethod
    def from_dict(data):
        return FilterRule(
            data["column"],
            data["operator"],
            data["value"]
        )

    def _get_mask(self, df):
        if self.operator == "==":
            return df[self.column] == self.value
        elif self.operator == "!=":
            return df[self.column] != self.value
        elif self.operator == ">":
            return df[self.column] > self.value
        elif self.operator == "<":
            return df[self.column] < self.value
        elif self.operator == ">=":
            return df[self.column] >= self.value
        elif self.operator == "<=":
            return df[self.column] <= self.value
        elif self.operator == "contains":
            return df[self.column].astype(str).str.contains(str(self.value))
        else:
            raise ValueError(f"不明な演算子: {self.operator}")

    def apply(self, df):
        mask = self._get_mask(df)
        return df[mask].copy()