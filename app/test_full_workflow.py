# test_full_workflow.py
import pandas as pd
import json
from core.processor import CsvProcessor
from core.rule_factory import create_rule_from_dict

# --- CSVデータ準備 ---
data = [
    {"名前": "田中太郎", "年齢": 25, "部署": "営業", "給与": 300},
    {"名前": "鈴木花子", "年齢": 30, "部署": "開発", "給与": 400},
    {"名前": "佐藤次郎", "年齢": 28, "部署": "営業", "給与": 350},
    {"名前": "高橋美咲", "年齢": 35, "部署": "開発", "給与": 450},
    {"名前": "山田健", "年齢": 40, "部署": "管理", "給与": 500},
]
df = pd.DataFrame(data)
print("初期データ (5件):")
print(df)
print("----------------------------------------")

# --- 保存済みワークフローをロード ---
workflow_file = "app/test_workflow.json"
with open(workflow_file, "r", encoding="utf-8") as f:
    workflow_data = json.load(f)

# --- ルール生成 ---
rules_data = workflow_data.get("rules", workflow_data)  # バージョン1/0対応
rules = [create_rule_from_dict(r) for r in rules_data]

print(f"ワークフロー読み込み: {workflow_file}")
print(f"適用ルール数: {len(rules)}")
print("----------------------------------------")

# --- CsvProcessorで実行 ---
def logger(msg):
    print(msg)

processor = CsvProcessor(rules, logger=logger)
result_df = processor.execute(df)

print("----------------------------------------")
print(f"最終データ ({len(result_df)}件):")
print(result_df)
