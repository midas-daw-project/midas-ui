from __future__ import annotations

from bridge.protocol import BridgeClient, BridgeResult
from viewmodels.browser_viewmodel import BrowserViewModel


class BrowserController:
    def __init__(self, bridge: BridgeClient, viewmodel: BrowserViewModel) -> None:
        self._bridge = bridge
        self._vm = viewmodel

    @property
    def viewmodel(self) -> BrowserViewModel:
        return self._vm

    def refresh_registry(self) -> BridgeResult:
        result = self._bridge.refresh_plugin_registry()
        self._vm.last_refresh_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.load_registry()
        return result

    def load_registry(self) -> None:
        self._vm.plugins = self._bridge.get_plugin_registry()
        if self._vm.plugins:
            selected = self._vm.selected_plugin_id or self._vm.plugins[0].plugin_id
            self.select_plugin(selected)
        else:
            self._vm.selected_plugin_id = ""
            self._vm.selected_name = ""
            self._vm.selected_category = ""
            self._vm.selected_vendor = ""
            self._vm.selected_source = ""
            self._vm.selected_available = False

    def select_plugin(self, plugin_id: str) -> None:
        self._vm.selected_plugin_id = plugin_id
        for plugin in self._vm.plugins:
            if plugin.plugin_id != plugin_id:
                continue
            self._vm.selected_name = plugin.name
            self._vm.selected_category = plugin.category
            self._vm.selected_vendor = plugin.vendor
            self._vm.selected_source = plugin.source
            self._vm.selected_available = plugin.available
            return
