# app/core/rules/condition_group_rule.py

from core.rules.filter_rule import FilterRule
import pandas as pd

class ConditionGroupRule:
    def __init__(self, rules=None, operator="AND"):
        """
        rules: FilterRule のリスト
        operator: "AND" または "OR"
        """
        self.rules = rules or []
        self.operator = operator

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.rules:
            return df

        # 各 FilterRule の条件を Series として取得
        masks = [rule._get_mask(df) for rule in self.rules]

        if self.operator == "AND":
            combined_mask = pd.concat(masks, axis=1).all(axis=1)
        else:  # OR
            combined_mask = pd.concat(masks, axis=1).any(axis=1)

        return df[combined_mask].copy()

    def description(self):
        cond_desc = [r.description() for r in self.rules]
        return f"条件グループ ({self.operator}): " + " ; ".join(cond_desc)

    def to_dict(self):
        return {
            "type": "ConditionGroupRule",
            "operator": self.operator,
            "rules": [r.to_dict() for r in self.rules]
        }

    @classmethod
    def from_dict(cls, data):
        from core.rule_factory import create_rule_from_dict
        rules = [create_rule_from_dict(r) for r in data.get("rules", [])]
        return cls(rules=rules, operator=data.get("operator", "AND"))
