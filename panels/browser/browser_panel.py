from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from viewmodels.browser_viewmodel import BrowserViewModel
from bridge.plugin_catalog import (
    NON_INSERT_CATEGORIES,
    PLUGIN_GROUP_ORDER,
    plugin_feature_status,
    plugin_function_label,
    plugin_group,
    plugin_purpose,
)


CATEGORY_FILTERS = {
    "All Sources": set(),
    "Insert FX": {
        "Delay",
        "Dynamics",
        "EQ",
        "Filter",
        "Imaging",
        "LoFi",
        "MIDI Effect",
        "Modulation",
        "Reverb",
        "Saturation",
        "Utility",
    },
    "Drum Instruments": {"Drum Instrument"},
    "Instruments": {"Instrument Source"},
    "Sample Libraries": {"Sample Library", "Sample Pack"},
    "Host Apps": {"Host App"},
    "Host Extensions": {"Host Extension", "REAPER FX"},
    "Plugin Shells": {"Plugin Shell"},
    "Plugin Managers": {"Plugin Manager"},
    "Interface Setup": {"Audio Interface Utility"},
    "Spatial Tools": {"Spatial Utility"},
    "Automation": {"Automation Source"},
    "Performance": {"Performance Host"},
    "Skin Tools": {"Skin Design Tool"},
    "Reference": {"Reference Suite"},
    "Reference Sources": {"Reference Source"},
}


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
        self._last_vm: BrowserViewModel | None = None
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        library_box = QGroupBox("Library")
        library_layout = QVBoxLayout(library_box)
        self.browser_heading_label = QLabel("Browser")
        self.browser_heading_label.setObjectName("browserHeading")
        self.browser_hint_label = QLabel("Library, plugins, loops, and setup sources.")
        self.browser_hint_label.setObjectName("browserHint")
        self.browser_hint_label.setWordWrap(True)
        self.browser_search_input = QLineEdit()
        self.browser_search_input.setPlaceholderText("Search sounds, plugins, presets")
        library_layout.addWidget(self.browser_heading_label)
        library_layout.addWidget(self.browser_hint_label)
        library_layout.addWidget(self.browser_search_input)
        self.category_list = QListWidget()
        for category in CATEGORY_FILTERS:
            self.category_list.addItem(category)
        self.category_list.setCurrentRow(0)
        self.category_list.setMaximumHeight(106)
        library_layout.addWidget(self.category_list)
        layout.addWidget(library_box)

        marketplace_box = QGroupBox("Packs / Sounds")
        marketplace_box.setMaximumHeight(138)
        marketplace_layout = QVBoxLayout(marketplace_box)
        self.pack_list = QListWidget()
        self.pack_list.setWordWrap(True)
        self.pack_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for title, subtitle in [
            ("Starter Kit", "Drums and one-shots"),
            ("Drum Pack", "Machine kits"),
            ("MIDI Pack", "Chords and patterns"),
        ]:
            item = QListWidgetItem(f"{title}\n{subtitle}")
            self.pack_list.addItem(item)
        self.pack_list.setCurrentRow(0)
        self.pack_list.setMaximumHeight(82)
        marketplace_layout.addWidget(self.pack_list)
        pack_actions = QHBoxLayout()
        self.preview_pack_button = QPushButton("Preview")
        self.install_pack_button = QPushButton("Install")
        pack_actions.addWidget(self.preview_pack_button)
        pack_actions.addWidget(self.install_pack_button)
        marketplace_layout.addLayout(pack_actions)
        layout.addWidget(marketplace_box)

        registry_box = QGroupBox("Plugin Browser")
        registry_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        registry_layout = QVBoxLayout(registry_box)
        registry_actions = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.insert_button = QPushButton("Insert")
        registry_actions.addWidget(self.refresh_button)
        registry_actions.addWidget(self.insert_button)
        registry_layout.addLayout(registry_actions)
        self.queue_label = QLabel("Queued Chain: empty")
        self.queue_label.setObjectName("pluginQueueLabel")
        self.queue_label.setWordWrap(True)
        registry_layout.addWidget(self.queue_label)

        self.plugin_browser_tabs = QTabWidget()
        self.plugin_browser_tabs.setObjectName("pluginBrowserTabs")
        self.plugin_browser_tabs.setMinimumHeight(300)
        self.plugin_browser_tabs.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        list_tab = QWidget()
        list_layout = QVBoxLayout(list_tab)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(6)

        self.plugin_wheel_box = QGroupBox("Selection Wheel")
        self.plugin_wheel_box.setMinimumHeight(260)
        self.plugin_wheel_layout = QGridLayout(self.plugin_wheel_box)
        self.plugin_wheel_layout.setContentsMargins(10, 10, 10, 10)
        self.plugin_wheel_layout.setHorizontalSpacing(8)
        self.plugin_wheel_layout.setVerticalSpacing(8)
        self.plugin_explanation_bubble = QLabel("Select a plugin or source to see what it does.")
        self.plugin_explanation_bubble.setObjectName("pluginExplanationBubble")
        self.plugin_explanation_bubble.setAlignment(Qt.AlignCenter)
        self.plugin_explanation_bubble.setWordWrap(True)
        self.plugin_explanation_bubble.setMinimumSize(132, 102)
        self.plugin_wheel_buttons: list[QPushButton] = []
        wheel_tab = QWidget()
        wheel_layout = QVBoxLayout(wheel_tab)
        wheel_layout.setContentsMargins(0, 0, 0, 0)
        wheel_layout.addWidget(self.plugin_wheel_box)

        self.plugin_list = QListWidget()
        self.plugin_list.setWordWrap(True)
        self.plugin_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plugin_list.setMinimumHeight(220)
        list_layout.addWidget(self.plugin_list)
        self.plugin_browser_tabs.addTab(list_tab, "List")
        self.plugin_browser_tabs.addTab(wheel_tab, "Wheel")
        registry_layout.addWidget(self.plugin_browser_tabs)
        layout.addWidget(registry_box)

        self.details_box = QGroupBox("Selected Source")
        self.details_box.setMaximumHeight(224)
        details_form = QFormLayout(self.details_box)
        self.id_label = QLabel("-")
        self.name_label = QLabel("-")
        self.category_label = QLabel("-")
        self.vendor_label = QLabel("-")
        self.source_label = QLabel("-")
        self.group_label = QLabel("-")
        self.feature_status_label = QLabel("-")
        self.purpose_label = QLabel("-")
        self.purpose_label.setWordWrap(True)
        self.available_label = QLabel("-")
        self.works_label = QLabel("-")
        self.works_label.setWordWrap(True)
        self.status_label = QLabel("Refresh: -")
        self.insert_status_label = QLabel("Insert: -")
        self.error_label = QLabel("Error: ")
        details_form.addRow("ID", self.id_label)
        details_form.addRow("Name", self.name_label)
        details_form.addRow("Category", self.category_label)
        details_form.addRow("Vendor", self.vendor_label)
        details_form.addRow("Source", self.source_label)
        details_form.addRow("Group", self.group_label)
        details_form.addRow("Feature Status", self.feature_status_label)
        details_form.addRow("Purpose", self.purpose_label)
        details_form.addRow("Available", self.available_label)
        details_form.addRow("Works in MIDAS", self.works_label)
        details_form.addRow(self.status_label)
        details_form.addRow(self.insert_status_label)
        details_form.addRow(self.error_label)
        layout.addWidget(self.details_box)

        self.refresh_button.clicked.connect(self._on_refresh_registry)
        self.insert_button.clicked.connect(self._on_insert_plugin)
        self.browser_search_input.textChanged.connect(self._rerender_from_current_vm)
        self.category_list.currentItemChanged.connect(lambda _current, _previous: self._rerender_from_current_vm())
        self.plugin_list.currentItemChanged.connect(self._emit_selection)

    def _emit_selection(self, item: QListWidgetItem | None, _previous: QListWidgetItem | None = None) -> None:
        plugin_id = str(item.data(Qt.UserRole) or "") if item is not None else ""
        if plugin_id:
            self._on_select_plugin(plugin_id)

    def render(self, vm: BrowserViewModel) -> None:
        self._last_vm = vm
        self._render_plugin_list(vm)

        self.id_label.setText(vm.selected_plugin_id or "-")
        self.name_label.setText(vm.selected_name or "-")
        self.category_label.setText(vm.selected_category or "-")
        self.vendor_label.setText(vm.selected_vendor or "-")
        self.source_label.setText(vm.selected_source or "-")
        self.group_label.setText(plugin_group(vm.selected_plugin_id) if vm.selected_plugin_id else "-")
        self.purpose_label.setText(plugin_purpose(vm.selected_plugin_id) if vm.selected_plugin_id else "-")
        self.feature_status_label.setText(
            plugin_feature_status(vm.selected_plugin_id, vm.selected_category, vm.selected_available)
            if vm.selected_plugin_id
            else "-"
        )
        if vm.selected_category in NON_INSERT_CATEGORIES:
            self.available_label.setText("detected source, not a mixer insert")
            self.works_label.setText("No. This is used for setup, discovery, or reference, not audio processing inside MIDAS.")
        elif vm.selected_available:
            self.available_label.setText("yes")
            self.works_label.setText("Yes. This can be selected and queued as a MIDAS insert effect.")
        else:
            self.available_label.setText("registered, not currently loadable")
            self.works_label.setText("Not yet. It is listed as a planned/demo insert but cannot currently process audio.")
        self.status_label.setText(f"Refresh: {vm.last_refresh_status or '-'}")
        self.insert_status_label.setText(f"Insert: {vm.last_insert_status or '-'}")
        self.error_label.setText(f"Error: {vm.last_error}")
        self.plugin_explanation_bubble.setText(self._selected_explanation(vm))
        self.queue_label.setText(self._queue_summary(vm))

    def _rerender_from_current_vm(self) -> None:
        if self._last_vm is not None:
            self._render_plugin_list(self._last_vm)

    def _render_plugin_list(self, vm: BrowserViewModel) -> None:
        self.plugin_list.blockSignals(True)
        self.plugin_list.clear()
        filtered_plugins = self._filtered_plugins(vm)
        current_group = ""
        for plugin in filtered_plugins:
            group = plugin_group(plugin.plugin_id)
            if group != current_group:
                current_group = group
                header = QListWidgetItem(group)
                header.setFlags(header.flags() & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)
                self.plugin_list.addItem(header)
            if plugin.category in NON_INSERT_CATEGORIES:
                status = "detected" if plugin.source.startswith("detected:") else "not installed"
            else:
                status = "ready" if plugin.available else "unavailable"
            feature_status = plugin_feature_status(plugin.plugin_id, plugin.category, plugin.available)
            function_label = plugin_function_label(plugin.plugin_id, plugin.category)
            item = QListWidgetItem(
                f"{plugin.name}\n{function_label} | {feature_status} | {plugin.vendor or 'Unknown'} | {status}\n"
                f"{plugin_purpose(plugin.plugin_id)}"
            )
            item.setData(Qt.UserRole, plugin.plugin_id)
            item.setToolTip(f"{plugin.plugin_id}\n{plugin.source}")
            self.plugin_list.addItem(item)
        if self.plugin_list.count() == 0:
            item = QListWidgetItem("No matching plugins or sources")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.plugin_list.addItem(item)
        if vm.selected_plugin_id:
            for i in range(self.plugin_list.count()):
                if self.plugin_list.item(i).data(Qt.UserRole) == vm.selected_plugin_id:
                    self.plugin_list.setCurrentRow(i)
                    break
        self.plugin_list.blockSignals(False)
        self._render_plugin_wheel(vm, filtered_plugins[:8])

    def _render_plugin_wheel(self, vm: BrowserViewModel, plugins) -> None:
        while self.plugin_wheel_layout.count():
            item = self.plugin_wheel_layout.takeAt(0)
            widget = item.widget()
            if widget is self.plugin_explanation_bubble:
                continue
            if widget is not None:
                widget.deleteLater()
        self.plugin_wheel_buttons.clear()
        positions = [(0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0)]
        for index in range(3):
            self.plugin_wheel_layout.setRowStretch(index, 1)
            self.plugin_wheel_layout.setColumnStretch(index, 1)
        self.plugin_wheel_layout.addWidget(self.plugin_explanation_bubble, 1, 1)
        for index, plugin in enumerate(plugins):
            button = QPushButton(plugin_function_label(plugin.plugin_id, plugin.category))
            button.setObjectName("pluginWheelButton")
            button.setCheckable(True)
            button.setChecked(plugin.plugin_id == vm.selected_plugin_id)
            button.setMinimumSize(72, 44)
            button.setToolTip(f"{plugin.name}\n{plugin_purpose(plugin.plugin_id)}")
            button.clicked.connect(lambda _checked=False, selected_id=plugin.plugin_id: self._on_select_plugin(selected_id))
            row, column = positions[index]
            self.plugin_wheel_layout.addWidget(button, row, column)
            self.plugin_wheel_buttons.append(button)
        if not plugins:
            empty_button = QPushButton("No Match")
            empty_button.setObjectName("pluginWheelButton")
            empty_button.setEnabled(False)
            self.plugin_wheel_layout.addWidget(empty_button, 0, 1)

    def _selected_explanation(self, vm: BrowserViewModel) -> str:
        if not vm.selected_plugin_id:
            return "Select a plugin or source to see what it does."
        role = "Queued for the mixer" if vm.selected_plugin_id in vm.queued_plugin_ids else "Reference source"
        if vm.selected_category in NON_INSERT_CATEGORIES:
            role = "Setup/reference source"
        elif not vm.selected_available:
            role = "Unavailable insert"
        return (
            f"{vm.selected_name}\n"
            f"{plugin_function_label(vm.selected_plugin_id, vm.selected_category)} | "
            f"{plugin_feature_status(vm.selected_plugin_id, vm.selected_category, vm.selected_available)} | "
            f"{plugin_group(vm.selected_plugin_id)}\n"
            f"{role}: {plugin_purpose(vm.selected_plugin_id)}"
        )

    def _queue_summary(self, vm: BrowserViewModel) -> str:
        if not vm.queued_plugin_ids:
            return "Queued Chain: empty"
        plugin_names = {plugin.plugin_id: plugin.name for plugin in vm.plugins}
        queued = " -> ".join(plugin_names.get(plugin_id, plugin_id) for plugin_id in vm.queued_plugin_ids)
        return f"Queued Chain: {queued}"

    def _filtered_plugins(self, vm: BrowserViewModel):
        category_item = self.category_list.currentItem()
        selected_category = category_item.text() if category_item is not None else "All Sources"
        allowed_categories = CATEGORY_FILTERS.get(selected_category, set())
        query = self.browser_search_input.text().strip().lower()
        group_rank = {group: index for index, group in enumerate(PLUGIN_GROUP_ORDER)}
        plugins = []
        for plugin in vm.plugins:
            if allowed_categories and plugin.category not in allowed_categories:
                continue
            searchable = " ".join(
                [
                    plugin.plugin_id,
                    plugin.name,
                    plugin.category,
                    plugin.vendor,
                    plugin.source,
                    plugin_group(plugin.plugin_id),
                    plugin_function_label(plugin.plugin_id, plugin.category),
                    plugin_purpose(plugin.plugin_id),
                ]
            ).lower()
            if query and query not in searchable:
                continue
            plugins.append(plugin)
        return sorted(
            plugins,
            key=lambda plugin: (
                group_rank.get(plugin_group(plugin.plugin_id), len(group_rank)),
                plugin.category,
                plugin.name,
            ),
        )
