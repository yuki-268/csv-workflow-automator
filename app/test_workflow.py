# test_workflow.py
import pandas as pd
from core.rules.drop_column_rule import DropColumnRule
from core.rules.filter_rule import FilterRule
from core.rules.sort_rule import SortRule
from core.rules.rename_column_rule import RenameColumnRule

def create_test_df():
    """テスト用のCSVデータを作成"""
    data = {
        "名前": ["田中太郎", "鈴木花子", "佐藤次郎", "高橋美咲", "山田健"],
        "年齢": [25, 30, 28, 35, 40],
        "部署": ["営業", "開発", "営業", "開発", "管理"],
        "給与": [300, 400, 350, 450, 500],
    }
    df = pd.DataFrame(data)
    return df

def run_test_workflow(df):
    """テスト用ルールを順番に適用"""
    rules = [
        DropColumnRule(["給与"]),                 # 列削除
        FilterRule("部署", "==", "営業"),       # フィルタ
        SortRule("年齢", ascending=True),       # 並び替え
        RenameColumnRule("名前", "氏名")        # 列名変更
    ]

    print(f"初期データ ({len(df)}件):\n{df}\n{'-'*40}")
    for idx, rule in enumerate(rules, start=1):
        before_count = len(df)
        df = rule.apply(df)
        after_count = len(df)
        print(f"[{idx}] {rule.description()}")
        print(f"件数: {before_count} → {after_count}")
        print(df.head(), "\n" + "-"*40)
    
    print(f"最終データ ({len(df)}件):\n{df}")
    return df

if __name__ == "__main__":
    df = create_test_df()
    run_test_workflow(df)
