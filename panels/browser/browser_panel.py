from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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

        library_box = QGroupBox("Library")
        library_layout = QVBoxLayout(library_box)
        self.browser_heading_label = QLabel("Browser")
        self.browser_heading_label.setObjectName("browserHeading")
        self.browser_search_input = QLineEdit()
        self.browser_search_input.setPlaceholderText("Search sounds, plugins, presets")
        library_layout.addWidget(self.browser_heading_label)
        library_layout.addWidget(self.browser_search_input)
        self.category_list = QListWidget()
        for category in ["Drums", "808s", "Hi Hats", "Melodies", "MIDI", "Loops", "FX"]:
            self.category_list.addItem(category)
        self.category_list.setCurrentRow(1)
        self.category_list.setMaximumHeight(150)
        library_layout.addWidget(self.category_list)
        layout.addWidget(library_box)

        marketplace_box = QGroupBox("Marketplace")
        marketplace_layout = QVBoxLayout(marketplace_box)
        self.pack_list = QListWidget()
        for title, subtitle in [
            ("TRAP STARTER KIT", "Punchy drums and melodic one-shots"),
            ("Analog Drum Pack", "Warm machine kits and percussion"),
            ("Lo-Fi MIDI Pack", "Chord starts and humanized patterns"),
        ]:
            item = QListWidgetItem(f"{title}\n{subtitle}")
            self.pack_list.addItem(item)
        self.pack_list.setCurrentRow(0)
        self.pack_list.setMaximumHeight(150)
        marketplace_layout.addWidget(self.pack_list)
        pack_actions = QHBoxLayout()
        self.preview_pack_button = QPushButton("Preview")
        self.install_pack_button = QPushButton("Install")
        pack_actions.addWidget(self.preview_pack_button)
        pack_actions.addWidget(self.install_pack_button)
        marketplace_layout.addLayout(pack_actions)
        layout.addWidget(marketplace_box)

        registry_box = QGroupBox("Plugins")
        registry_layout = QVBoxLayout(registry_box)
        self.refresh_button = QPushButton("Refresh Registry")
        self.insert_button = QPushButton("Insert To Selected Mixer Slot")
        registry_layout.addWidget(self.refresh_button)
        registry_layout.addWidget(self.insert_button)

        self.plugin_list = QListWidget()
        self.plugin_list.setMinimumHeight(140)
        registry_layout.addWidget(self.plugin_list)
        layout.addWidget(registry_box)

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
