from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from bridge.protocol import DiscoverableSessionEntry


class OpenExistingSessionDialog(QDialog):
    def __init__(
        self,
        sessions: list[DiscoverableSessionEntry],
        active_session_ref: str,
        recent_session_refs: list[str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._active_session_ref = active_session_ref.strip()
        self._recent_session_refs = {ref.strip() for ref in recent_session_refs if ref.strip()}
        self._browse_requested = False

        self.setWindowTitle("Open Existing Session")
        self.resize(760, 420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose a discovered session or browse for a .session file."))

        self.session_list = QListWidget()
        self.session_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.session_list)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.open_button = QPushButton("Open")
        self.browse_button = QPushButton("Browse...")
        self.button_box.addButton(self.open_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.browse_button, QDialogButtonBox.ActionRole)
        layout.addWidget(self.button_box)

        self.open_button.clicked.connect(self._accept_selected)
        self.browse_button.clicked.connect(self._request_browse)
        self.button_box.rejected.connect(self.reject)
        self.session_list.itemDoubleClicked.connect(lambda _: self._accept_selected())
        self.session_list.currentItemChanged.connect(lambda *_: self._sync_open_button())

        self._populate_sessions(sessions)
        self._sync_open_button()

    def selected_session_ref(self) -> str:
        item = self.session_list.currentItem()
        if item is None:
            return ""
        return str(item.data(Qt.UserRole) or "")

    def browse_requested(self) -> bool:
        return self._browse_requested

    def _populate_sessions(self, sessions: list[DiscoverableSessionEntry]) -> None:
        ordered = sorted(
            sessions,
            key=lambda entry: (-int(entry.last_modified_epoch), entry.session_ref.lower(), entry.storage_path.lower()),
        )
        for entry in ordered:
            label = self._build_label(entry)
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, entry.session_ref)
            if entry.session_ref == self._active_session_ref:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                item.setToolTip("Already active")
            self.session_list.addItem(item)
        self._select_first_openable()

    def _build_label(self, entry: DiscoverableSessionEntry) -> str:
        markers: list[str] = []
        if entry.session_ref == self._active_session_ref:
            markers.append("current")
        if entry.session_ref in self._recent_session_refs:
            markers.append("recent")
        marker_text = f" [{' / '.join(markers)}]" if markers else ""
        modified = self._format_timestamp(entry.last_modified_epoch)
        return f"{entry.session_ref}{marker_text}\n{entry.storage_path}\nLast Modified: {modified}"

    def _format_timestamp(self, epoch: int) -> str:
        if epoch <= 0:
            return "-"
        return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")

    def _select_first_openable(self) -> None:
        for index in range(self.session_list.count()):
            item = self.session_list.item(index)
            if item.flags() & Qt.ItemIsEnabled:
                self.session_list.setCurrentRow(index)
                return

    def _sync_open_button(self) -> None:
        session_ref = self.selected_session_ref()
        self.open_button.setEnabled(bool(session_ref) and session_ref != self._active_session_ref)

    def _accept_selected(self) -> None:
        if not self.open_button.isEnabled():
            return
        self._browse_requested = False
        self.accept()

    def _request_browse(self) -> None:
        self._browse_requested = True
        self.accept()
