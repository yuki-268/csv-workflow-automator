# /app/core/ui/main_window.py

import os
import time
import json
import pandas as pd
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtWidgets import (
    QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout,
    QListWidget, QWidget, QListWidgetItem, QFileDialog, 
    QTextEdit, QTableView, QSplitter, QLabel, QProgressBar,
)

from core.processor import CsvProcessor
from core.table_model import DataFrameModel
from core.rule_factory import create_rule_from_dict
from .rule_dialog import RuleDialog

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.rules = []
        self.history = []
        self.future = []
        self.current_df = None

        self._setup_ui()
        self._connect_signals()
        self._auto_load_workflow()
        self._update_undo_button()

    def _setup_ui(self):
        self.setWindowTitle("CSV Workflow Automator")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # ===== 上部ボタン =====
        self.load_button = QPushButton("CSV読み込み")
        self.save_result_button = QPushButton("結果をCSV保存")
        self.save_workflow_button = QPushButton("ワークフロー保存")
        self.load_workflow_button = QPushButton("ワークフロー読込")

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.load_button)
        top_layout.addWidget(self.save_result_button)
        top_layout.addWidget(self.save_workflow_button)
        top_layout.addWidget(self.load_workflow_button)

        # ===== テーブル =====
        self.table_view = QTableView()
        self.table_view_label = QLabel("CSVプレビュー")

        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table_view_label)
        table_layout.addWidget(self.table_view)

        table_widget = QWidget()
        table_widget.setLayout(table_layout)

        # ===== ルール側 =====
        self.rule_list = QListWidget()
        self.rule_list_label = QLabel("処理ルール")

        self.add_rule_button = QPushButton("追加")
        self.edit_rule_button = QPushButton("編集")
        self.remove_rule_button = QPushButton("削除")
        self.move_up_button = QPushButton("↑")
        self.move_down_button = QPushButton("↓")

        rule_button_layout = QHBoxLayout()
        rule_button_layout.addWidget(self.add_rule_button)
        rule_button_layout.addWidget(self.edit_rule_button)
        rule_button_layout.addWidget(self.remove_rule_button)
        rule_button_layout.addWidget(self.move_up_button)
        rule_button_layout.addWidget(self.move_down_button)

        rule_layout = QVBoxLayout()
        rule_layout.addWidget(self.rule_list_label)
        rule_layout.addWidget(self.rule_list)
        rule_layout.addLayout(rule_button_layout)

        rule_widget = QWidget()
        rule_widget.setLayout(rule_layout)

        # ===== Splitter =====
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(table_widget)
        splitter.addWidget(rule_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        # ===== 下部操作 =====
        self.undo_button = QPushButton("元に戻す")
        self.redo_button = QPushButton("やり直す")
        self.execute_button = QPushButton("実行")

        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addWidget(self.undo_button)
        bottom_button_layout.addWidget(self.redo_button)
        bottom_button_layout.addWidget(self.execute_button)

        # ===== ログ =====
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # ===== プログレスバー =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # ===== メインレイアウト =====
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(splitter)
        main_layout.addLayout(bottom_button_layout)
        main_layout.addWidget(self.log_output)
        main_layout.addWidget(self.progress_bar)

        central_widget.setLayout(main_layout)

        self.statusBar().showMessage("準備完了")


    def _connect_signals(self):
        self.load_button.clicked.connect(self.load_csv)
        self.add_rule_button.clicked.connect(self.add_rule)
        self.remove_rule_button.clicked.connect(self.remove_rule)
        self.move_up_button.clicked.connect(self.move_rule_up)
        self.move_down_button.clicked.connect(self.move_rule_down)
        self.undo_button.clicked.connect(self.undo)
        self.edit_rule_button.clicked.connect(self.edit_rule)
        self.rule_list.itemDoubleClicked.connect(self.edit_rule)
        self.redo_button.clicked.connect(self.redo)
        self.execute_button.clicked.connect(self.execute_rules)
        self.save_workflow_button.clicked.connect(self.save_workflow)
        self.load_workflow_button.clicked.connect(self.load_workflow)
        self.save_result_button.clicked.connect(self.save_result_csv)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSV選択", "", "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            self.current_df = pd.read_csv(file_path)
            self.table_view.setModel(DataFrameModel(self.current_df))
            self.table_view.resizeColumnsToContents()
            self.history.clear()
            self.future.clear()
            self._update_undo_button()
            self._update_redo_button()
            self.log(f"CSV loaded: {file_path}")
            self.log(f"列一覧: {list(self.current_df.columns)}")  # 追加
        except Exception as e:
            self.log(f"読み込みエラー: {e}")

        
    def add_rule(self):
        if self.current_df is None:
            self.log("先にCSVを読み込んでください")
            return

        dialog = RuleDialog(list(self.current_df.columns), self)
        if dialog.exec():
            rule = dialog.get_rule()
            if rule:
                item = QListWidgetItem(rule.description())
                item.setData(Qt.UserRole, rule)
                self.rule_list.addItem(item)
                self.log("ルール追加")

    def edit_rule(self):
        current_row = self.rule_list.currentRow()
        if current_row < 0:
            self.log("編集するルールを選択してください")
            return

        item = self.rule_list.item(current_row)
        rule = item.data(Qt.UserRole)

        dialog = RuleDialog(list(self.current_df.columns), self)
        dialog.set_rule(rule)
        if dialog.exec():
            updated_rule = dialog.get_rule()
            if updated_rule:
                item.setText(updated_rule.description())
                item.setData(Qt.UserRole, updated_rule)
                self.log("ルールを更新しました")

    def execute_rules(self):
        if self.current_df is None:
            self.log("CSVが読み込まれていません")
            return

        try:
            self.log("--- 実行開始 ---")
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("実行中...")
            start_time = time.perf_counter()

            # 実行前の状態を保存（Undo用）
            self.history.append(self.current_df.copy())
            self.future.clear()

            # 適用ルールを取得
            rules = [self.rule_list.item(i).data(Qt.UserRole) for i in range(self.rule_list.count())]
            self.log(f"適用ルール数: {len(rules)}")

            if not rules:
                self.log("適用するルールがありません")
                self.statusBar().showMessage("ルール未設定")
                return

            # CsvProcessor で一括実行
            processor = CsvProcessor(rules, logger=self.log)
            result_df = processor.execute(self.current_df)

            # プレビュー更新
            self.table_view.setModel(DataFrameModel(result_df))
            self.current_df = result_df

            self._update_undo_button()
            self._update_redo_button()

            # 経過時間
            elapsed = time.perf_counter() - start_time
            msg = f"実行時間: {elapsed:.4f} 秒"
            self.log(msg)
            self.statusBar().showMessage(msg)
            self.progress_bar.setValue(100)
            self.log("--- 実行完了 ---")

        except Exception as e:
            self.log(f"処理エラー: {e}")



    def log(self, message: str):
        self.log_output.append(message)

    def remove_rule(self):
        current_row = self.rule_list.currentRow()
        if current_row >= 0:
            self.rule_list.takeItem(current_row)

    def move_rule_up(self):
        current_row = self.rule_list.currentRow()
        if current_row > 0:
            item = self.rule_list.takeItem(current_row)
            self.rule_list.insertItem(current_row - 1, item)
            self.rule_list.setCurrentRow(current_row - 1)


    def move_rule_down(self):
        current_row = self.rule_list.currentRow()
        if 0 <= current_row < self.rule_list.count() - 1:
            item = self.rule_list.takeItem(current_row)
            self.rule_list.insertItem(current_row + 1, item)
            self.rule_list.setCurrentRow(current_row + 1)

    def save_workflow(self):
        if self.rule_list.count() == 0:
            self.log("保存するルールがありません")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "ワークフロー保存",
            "",
            "JSON Files (*.json)"
        )

        if not save_path:
            return

        try:
            rules = []
            for i in range(self.rule_list.count()):
                item = self.rule_list.item(i)
                rule = item.data(Qt.UserRole)
                rules.append(rule.to_dict())

            data = {
                "version": 1,
                "rules": rules
            }

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.log(f"保存完了: {save_path}")

        except Exception as e:
            self.log(f"保存エラー: {e}")


    def load_workflow(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ワークフロー読込",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # --- version判定 ---
            if isinstance(data, list):
                # 旧バージョン（versionなし）
                version = 0
                rules_data = data
            else:
                version = data.get("version", 0)
                rules_data = data.get("rules", [])

            self.rule_list.clear()

            # --- version別処理 ---
            for rule_data in rules_data:
                rule = create_rule_from_dict(rule_data)
                # 列が存在しなければスキップ
                if hasattr(rule, "column") and rule.column not in self.current_df.columns:
                    self.log(f"ルール '{rule.description()}' の列が存在しないためスキップ")
                    continue
                item = QListWidgetItem(rule.description())
                item.setData(Qt.UserRole, rule)
                self.rule_list.addItem(item)

            self.log(f"読み込み完了 (version {version})")

        except Exception as e:
            self.log(f"読込エラー: {e}")


    def _get_config_path(self):
        base_path = QStandardPaths.writableLocation(
            QStandardPaths.AppDataLocation
        )

        os.makedirs(base_path, exist_ok=True)

        return os.path.join(base_path, "workflow.json")

    def _auto_save_workflow(self):
        if self.rule_list.count() == 0:
            return

        try:
            path = self._get_config_path()

            rules = []
            for i in range(self.rule_list.count()):
                item = self.rule_list.item(i)
                rule = item.data(Qt.UserRole)
                rules.append(rule.to_dict())

            data = {
                "version": 1,
                "rules": rules
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            self.log(f"自動保存エラー: {e}")


    def _auto_load_workflow(self):
        path = self._get_config_path()

        if not os.path.exists(path):
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                version = 0
                rules_data = data
            else:
                version = data.get("version", 0)
                rules_data = data.get("rules", [])

            self.rule_list.clear()

            for rule_data in rules_data:
                rule = create_rule_from_dict(rule_data)
                item = QListWidgetItem(rule.description())
                item.setData(Qt.UserRole, rule)
                self.rule_list.addItem(item)

            self.log(f"前回のワークフローを復元しました (v{version})")

        except Exception as e:
            self.log(f"自動読込エラー: {e}")

    def undo(self):
        if not self.history:
            self.log("戻せる履歴がありません")
            return

        self.future.append(self.current_df.copy())  # ← 追加
        self.current_df = self.history.pop()
        self.table_view.setModel(DataFrameModel(self.current_df))
        self.log("1つ前の状態に戻しました")

        self._update_undo_button()
        self._update_redo_button()

    def _update_undo_button(self):
        self.undo_button.setEnabled(len(self.history) > 0)

    def redo(self):
        if not self.future:
            self.log("やり直せる履歴がありません")
            return

        self.history.append(self.current_df.copy())
        self.current_df = self.future.pop()
        self.table_view.setModel(DataFrameModel(self.current_df))
        self.log("やり直しました")

        self._update_undo_button()
        self._update_redo_button()

    def _update_redo_button(self):
        self.redo_button.setEnabled(len(self.future) > 0)

    def closeEvent(self, event):
        self._auto_save_workflow()
        event.accept()

    def save_result_csv(self):
        if self.current_df is None:
            self.log("保存するデータがありません")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "結果CSV保存",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            self.current_df.to_csv(file_path, index=False)
            self.log(f"保存完了: {file_path}")
            self.statusBar().showMessage("CSV保存完了")
        except Exception as e:
            self.log(f"保存エラー: {e}")
