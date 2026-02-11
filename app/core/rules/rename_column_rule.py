from .base_rule import BaseRule

class RenameColumnRule(BaseRule):

    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name

    def apply(self, df):
        return df.rename(columns={self.old_name: self.new_name})

    def description(self):
        return f"列名変更: {self.old_name} → {self.new_name}"

    def to_dict(self):
        return {
            "type": "rename",
            "old_name": self.old_name,
            "new_name": self.new_name
        }

    @staticmethod
    def from_dict(data):
        return RenameColumnRule(
            data["old_name"],
            data["new_name"]
        )
