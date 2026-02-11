# app/core/ui/rule_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox,
    QLineEdit, QWidget, QListWidget, QListWidgetItem
)

from core.rules.drop_column_rule import DropColumnRule
from core.rules.filter_rule import FilterRule
from core.rules.sort_rule import SortRule
from core.rules.rename_column_rule import RenameColumnRule

class RuleDialog(QDialog):

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.selected_rule = None

        self.setWindowTitle("ルール設定")
        self.resize(400, 250)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)

        # ルール種類選択
        self.rule_type_combo = QComboBox()
        self.rule_type_combo.addItems(["列削除", "フィルタ", "並び替え", "列名変更"])
        self.layout.addWidget(QLabel("ルール種類"))
        self.layout.addWidget(self.rule_type_combo)

        # 設定エリア
        self.config_widget = QWidget()
        self.config_layout = QVBoxLayout(self.config_widget)
        self.layout.addWidget(self.config_widget)

        # OK / Cancel
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        self._update_config_ui()  # 初期UI構築

    def _update_column_combo(self, df):
        """コンボボックスをCSV列に合わせて更新"""
        self.column_combo.clear()
        self.column_combo.addItems([col for col in self.columns if col in df.columns])

    def _update_column_list(self, df):
        self.column_list_widget.clear()
        self.column_list_widget.addItems([col for col in self.columns if col in df.columns])

    def _connect_signals(self):
        self.rule_type_combo.currentIndexChanged.connect(self._update_config_ui)
        self.ok_button.clicked.connect(self._create_rule)
        self.cancel_button.clicked.connect(self.reject)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _update_config_ui(self):
        self._clear_layout(self.config_layout)
        rule_type = self.rule_type_combo.currentText()

        if rule_type == "列削除":
            self.column_list_widget = QListWidget()
            self.column_list_widget.addItems(self.columns)
            self.column_list_widget.setSelectionMode(QListWidget.MultiSelection)
            self.config_layout.addWidget(QLabel("削除する列（複数選択可）"))
            self.config_layout.addWidget(self.column_list_widget)

        elif rule_type == "フィルタ":
            self.filter_column_combo = QComboBox()
            self.filter_column_combo.addItems(self.columns)
            self.operator_combo = QComboBox()
            self.operator_combo.addItems(["==", "!=", ">", "<", ">=", "<=", "contains"])
            self.value_input = QLineEdit()
            self.config_layout.addWidget(QLabel("列"))
            self.config_layout.addWidget(self.filter_column_combo)
            self.config_layout.addWidget(QLabel("演算子"))
            self.config_layout.addWidget(self.operator_combo)
            self.config_layout.addWidget(QLabel("値"))
            self.config_layout.addWidget(self.value_input)

        elif rule_type == "並び替え":
            self.sort_column_combo = QComboBox()
            self.sort_column_combo.addItems(self.columns)
            self.order_combo = QComboBox()
            self.order_combo.addItems(["昇順", "降順"])
            self.config_layout.addWidget(QLabel("列"))
            self.config_layout.addWidget(self.sort_column_combo)
            self.config_layout.addWidget(QLabel("順序"))
            self.config_layout.addWidget(self.order_combo)

        elif rule_type == "列名変更":
            self.rename_column_combo = QComboBox()
            self.rename_column_combo.addItems(self.columns)
            self.new_name_input = QLineEdit()
            self.config_layout.addWidget(QLabel("変更元列"))
            self.config_layout.addWidget(self.rename_column_combo)
            self.config_layout.addWidget(QLabel("新しい列名"))
            self.config_layout.addWidget(self.new_name_input)

    def _create_rule(self):
        rule_type = self.rule_type_combo.currentText()
        if rule_type == "列削除":
            columns = [item.text() for item in self.column_list_widget.selectedItems()]
            if columns:
                self.selected_rule = DropColumnRule(columns)
        elif rule_type == "フィルタ":
            column = self.filter_column_combo.currentText()
            operator = self.operator_combo.currentText()
            value = self.value_input.text()
            # 数値なら変換
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    pass
            self.selected_rule = FilterRule(column, operator, value)
        elif rule_type == "並び替え":
            column = self.sort_column_combo.currentText()
            ascending = self.order_combo.currentText() == "昇順"
            self.selected_rule = SortRule(column, ascending)
        elif rule_type == "列名変更":
            old = self.rename_column_combo.currentText()
            new = self.new_name_input.text()
            self.selected_rule = RenameColumnRule(old, new)
        self.accept()

    def get_rule(self):
        return self.selected_rule

    def set_rule(self, rule):
        """既存ルールを反映（編集用）"""
        df_columns = self.columns

        if isinstance(rule, DropColumnRule):
            self.rule_type_combo.setCurrentText("列削除")
            self._update_config_ui()
            for i in range(self.column_list_widget.count()):
                item = self.column_list_widget.item(i)
                if item.text() in rule.columns:
                    item.setSelected(True)
        elif isinstance(rule, FilterRule):
            self.rule_type_combo.setCurrentText("フィルタ")
            self._update_config_ui()
            if rule.column in df_columns:
                self.filter_column_combo.setCurrentText(rule.column)
            self.operator_combo.setCurrentText(rule.operator)
            self.value_input.setText(str(rule.value))
        elif isinstance(rule, SortRule):
            self.rule_type_combo.setCurrentText("並び替え")
            self._update_config_ui()
            if rule.column in df_columns:
                self.sort_column_combo.setCurrentText(rule.column)
            self.order_combo.setCurrentText("昇順" if rule.ascending else "降順")
        elif isinstance(rule, RenameColumnRule):
            self.rule_type_combo.setCurrentText("列名変更")
            self._update_config_ui()
            if rule.old_name in df_columns:
                self.rename_column_combo.setCurrentText(rule.old_name)
            self.new_name_input.setText(rule.new_name)

        self.selected_rule = rule

    def update_columns(self, columns):
        """MainWindowから呼ぶ: CSV列更新時にUIも更新"""
        self.columns = columns
        self._update_config_ui()