from core.rules.filter_rule import FilterRule
from core.rules.drop_column_rule import DropColumnRule
from core.rules.sort_rule import SortRule
from core.rules.rename_column_rule import RenameColumnRule

def create_rule_from_dict(data):
    rule_type = data.get("type")

    if rule_type == "filter":
        return FilterRule.from_dict(data)

    elif rule_type == "drop_column":
        return DropColumnRule.from_dict(data)

    elif rule_type == "sort":
        return SortRule.from_dict(data)

    elif rule_type == "rename":
        return RenameColumnRule.from_dict(data)

    else:
        raise ValueError(f"未知のルールタイプ: {rule_type}")
