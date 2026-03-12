from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from viewmodels.browser_viewmodel import BrowserViewModel


class BrowserPanel(QWidget):
    def __init__(
        self,
        on_refresh_registry: Callable[[], None],
        on_select_plugin: Callable[[str], None],
        on_insert_plugin: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_refresh_registry = on_refresh_registry
        self._on_select_plugin = on_select_plugin
        self._on_insert_plugin = on_insert_plugin

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.refresh_button = QPushButton("Refresh Registry")
        self.insert_button = QPushButton("Insert To Selected Mixer Slot")
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.insert_button)

        self.plugin_list = QListWidget()
        layout.addWidget(self.plugin_list)

        details_box = QGroupBox("Plugin Details")
        details_form = QFormLayout(details_box)
        self.id_label = QLabel("-")
        self.name_label = QLabel("-")
        self.category_label = QLabel("-")
        self.vendor_label = QLabel("-")
        self.source_label = QLabel("-")
        self.available_label = QLabel("-")
        self.status_label = QLabel("Refresh: -")
        self.insert_status_label = QLabel("Insert: -")
        self.error_label = QLabel("Error: ")
        details_form.addRow("ID", self.id_label)
        details_form.addRow("Name", self.name_label)
        details_form.addRow("Category", self.category_label)
        details_form.addRow("Vendor", self.vendor_label)
        details_form.addRow("Source", self.source_label)
        details_form.addRow("Available", self.available_label)
        details_form.addRow(self.status_label)
        details_form.addRow(self.insert_status_label)
        details_form.addRow(self.error_label)
        layout.addWidget(details_box)

        self.refresh_button.clicked.connect(self._on_refresh_registry)
        self.insert_button.clicked.connect(self._on_insert_plugin)
        self.plugin_list.currentTextChanged.connect(self._emit_selection)

    def _emit_selection(self, value: str) -> None:
        plugin_id = value.split(" ", 1)[0].strip() if value else ""
        if plugin_id:
            self._on_select_plugin(plugin_id)

    def render(self, vm: BrowserViewModel) -> None:
        self.plugin_list.blockSignals(True)
        self.plugin_list.clear()
        for plugin in vm.plugins:
            status = "ready" if plugin.available else "unavailable"
            self.plugin_list.addItem(f"{plugin.plugin_id}  ({plugin.name} | {status})")
        if vm.selected_plugin_id:
            for i in range(self.plugin_list.count()):
                if self.plugin_list.item(i).text().startswith(vm.selected_plugin_id):
                    self.plugin_list.setCurrentRow(i)
                    break
        self.plugin_list.blockSignals(False)

        self.id_label.setText(vm.selected_plugin_id or "-")
        self.name_label.setText(vm.selected_name or "-")
        self.category_label.setText(vm.selected_category or "-")
        self.vendor_label.setText(vm.selected_vendor or "-")
        self.source_label.setText(vm.selected_source or "-")
        self.available_label.setText("yes" if vm.selected_available else "no")
        self.status_label.setText(f"Refresh: {vm.last_refresh_status or '-'}")
        self.insert_status_label.setText(f"Insert: {vm.last_insert_status or '-'}")
        self.error_label.setText(f"Error: {vm.last_error}")
