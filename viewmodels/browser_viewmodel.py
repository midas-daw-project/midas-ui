from __future__ import annotations

from dataclasses import dataclass, field

from bridge.protocol import PluginRegistryEntry


@dataclass(slots=True)
class BrowserViewModel:
    plugins: list[PluginRegistryEntry] = field(default_factory=list)
    selected_plugin_id: str = ""
    selected_name: str = ""
    selected_category: str = ""
    selected_vendor: str = ""
    selected_source: str = ""
    selected_available: bool = False
    last_refresh_status: str = ""
    last_error: str = ""
