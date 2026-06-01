from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from bridge.protocol import PluginRegistryEntry


class PluginInsertDialog(QDialog):
    def __init__(
        self,
        plugins: list[PluginRegistryEntry],
        selected_plugin_id: str = "",
        channel_id: int = 1,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._plugins = list(plugins)
        self._selected_plugin_id = selected_plugin_id
        self.setWindowTitle(f"Add FX to Track {channel_id}")
        self.resize(760, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.title_label = QLabel(f"Add FX to Track {channel_id}")
        self.title_label.setObjectName("pluginDialogTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search available plugins")
        self.clear_filter_button = QPushButton("Clear")
        filter_row.addWidget(self.filter_input, 1)
        filter_row.addWidget(self.clear_filter_button)
        layout.addLayout(filter_row)

        browser_grid = QGridLayout()
        browser_grid.setHorizontalSpacing(8)
        self.category_list = QListWidget()
        self.category_list.setMinimumWidth(170)
        self.category_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plugin_list = QListWidget()
        self.plugin_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plugin_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plugin_list.setWordWrap(True)
        self.plugin_list.setMinimumHeight(320)
        browser_grid.addWidget(self.category_list, 0, 0)
        browser_grid.addWidget(self.plugin_list, 0, 1)
        browser_grid.setColumnStretch(1, 1)
        layout.addLayout(browser_grid, 1)

        action_row = QHBoxLayout()
        action_row.addStretch(1)
        self.add_button = QPushButton("Add")
        self.cancel_button = QPushButton("Cancel")
        action_row.addWidget(self.add_button)
        action_row.addWidget(self.cancel_button)
        layout.addLayout(action_row)

        self.filter_input.textChanged.connect(self._render_plugins)
        self.clear_filter_button.clicked.connect(self.filter_input.clear)
        self.category_list.currentTextChanged.connect(lambda _value: self._render_plugins())
        self.plugin_list.currentItemChanged.connect(lambda _current, _previous: self._update_add_enabled())
        self.plugin_list.itemDoubleClicked.connect(lambda _item: self._accept_if_ready())
        self.add_button.clicked.connect(self._accept_if_ready)
        self.cancel_button.clicked.connect(self.reject)

        self._render_categories()
        self._render_plugins()

    def selected_plugin_id(self) -> str:
        item = self.plugin_list.currentItem()
        if item is None:
            return ""
        return str(item.data(Qt.UserRole) or "")

    def _render_categories(self) -> None:
        self.category_list.blockSignals(True)
        self.category_list.clear()
        categories = ["All Plugins"]
        categories.extend(sorted({plugin.category or "Other" for plugin in self._plugins}))
        for category in categories:
            self.category_list.addItem(category)
        self.category_list.setCurrentRow(0)
        self.category_list.blockSignals(False)

    def _render_plugins(self) -> None:
        category = self.category_list.currentItem().text() if self.category_list.currentItem() else "All Plugins"
        query = self.filter_input.text().strip().lower()
        self.plugin_list.blockSignals(True)
        self.plugin_list.clear()
        first_available_row = -1
        preferred_row = -1
        for plugin in self._plugins:
            searchable = " ".join(
                [plugin.name, plugin.category, plugin.vendor, plugin.source, plugin.plugin_id]
            ).lower()
            if category != "All Plugins" and (plugin.category or "Other") != category:
                continue
            if query and query not in searchable:
                continue
            status = "ready" if plugin.available else "not installed"
            item = QListWidgetItem(f"{plugin.name}\n{plugin.category or 'Other'} | {plugin.vendor or 'Unknown'} | {status}")
            item.setData(Qt.UserRole, plugin.plugin_id)
            if not plugin.available:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.plugin_list.addItem(item)
            row = self.plugin_list.count() - 1
            if plugin.available and first_available_row == -1:
                first_available_row = row
            if plugin.plugin_id == self._selected_plugin_id:
                preferred_row = row
        if self.plugin_list.count() == 0:
            item = QListWidgetItem("No matching plugins")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.plugin_list.addItem(item)
        elif preferred_row >= 0:
            self.plugin_list.setCurrentRow(preferred_row)
        elif first_available_row >= 0:
            self.plugin_list.setCurrentRow(first_available_row)
        self.plugin_list.blockSignals(False)
        self._update_add_enabled()

    def _update_add_enabled(self) -> None:
        item = self.plugin_list.currentItem()
        self.add_button.setEnabled(bool(item and item.flags() & Qt.ItemIsEnabled and item.data(Qt.UserRole)))

    def _accept_if_ready(self) -> None:
        if self.add_button.isEnabled():
            self.accept()
