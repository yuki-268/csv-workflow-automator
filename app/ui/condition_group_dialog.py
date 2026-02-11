# app/core/ui/condition_group_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QComboBox
)

class ConditionGroupDialog(QDialog):
    def __init__(self, columns, existing_rules=None, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.selected_rules = existing_rules or []
        self.operator = "AND"

        self.setWindowTitle("条件グループ設定")
        self.resize(400, 300)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 条件リスト
        self.rule_list_widget = QListWidget()
        layout.addWidget(QLabel("条件一覧"))
        layout.addWidget(self.rule_list_widget)

        for rule in self.selected_rules:
            item = QListWidgetItem(rule.description())
            item.setData(0x0100, rule)
            self.rule_list_widget.addItem(item)

        # ボタン
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("追加")
        self.edit_btn = QPushButton("編集")
        self.remove_btn = QPushButton("削除")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        # AND / OR
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["AND", "OR"])
        self.operator_combo.setCurrentText(self.operator)
        layout.addWidget(QLabel("条件結合演算子"))
        layout.addWidget(self.operator_combo)

        # OK / Cancel
        ok_cancel_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        ok_cancel_layout.addWidget(self.ok_btn)
        ok_cancel_layout.addWidget(self.cancel_btn)
        layout.addLayout(ok_cancel_layout)

        # シグナル
        self.add_btn.clicked.connect(self.add_rule)
        self.edit_btn.clicked.connect(self.edit_rule)
        self.remove_btn.clicked.connect(self.remove_rule)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # --- 遅延インポート ---
    def add_rule(self):
        from .rule_dialog import RuleDialog  # ここでインポート
        dialog = RuleDialog(self.columns, self)
        dialog.rule_type_combo.setCurrentText("フィルタ")
        dialog._update_config_ui()
        if dialog.exec():
            rule = dialog.get_rule()
            if rule:
                item = QListWidgetItem(rule.description())
                item.setData(0x0100, rule)
                self.rule_list_widget.addItem(item)

    def edit_rule(self):
        row = self.rule_list_widget.currentRow()
        if row < 0:
            return
        item = self.rule_list_widget.item(row)
        rule = item.data(0x0100)
        from .rule_dialog import RuleDialog  # ここも遅延インポート
        dialog = RuleDialog(self.columns, self)
        dialog.set_rule(rule)
        if dialog.exec():
            updated_rule = dialog.get_rule()
            item.setText(updated_rule.description())
            item.setData(0x0100, updated_rule)

    def remove_rule(self):
        row = self.rule_list_widget.currentRow()
        if row >= 0:
            self.rule_list_widget.takeItem(row)

    def get_group_rule(self):
        rules = [self.rule_list_widget.item(i).data(0x0100) for i in range(self.rule_list_widget.count())]
        operator = self.operator_combo.currentText()
        return rules, operator
