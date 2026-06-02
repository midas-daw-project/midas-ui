from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


MAJOR_SCALES: dict[str, list[str]] = {
    "C Major": ["C", "D", "E", "F", "G", "A", "B", "C"],
    "G Major": ["G", "A", "B", "C", "D", "E", "F#", "G"],
    "D Major": ["D", "E", "F#", "G", "A", "B", "C#", "D"],
    "A Major": ["A", "B", "C#", "D", "E", "F#", "G#", "A"],
    "E Major": ["E", "F#", "G#", "A", "B", "C#", "D#", "E"],
    "B Major": ["B", "C#", "D#", "E", "F#", "G#", "A#", "B"],
    "F# Major": ["F#", "G#", "A#", "B", "C#", "D#", "E#", "F#"],
    "Gb Major": ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F", "Gb"],
    "Db Major": ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C", "Db"],
    "Ab Major": ["Ab", "Bb", "C", "Db", "Eb", "F", "G", "Ab"],
    "Eb Major": ["Eb", "F", "G", "Ab", "Bb", "C", "D", "Eb"],
    "Bb Major": ["Bb", "C", "D", "Eb", "F", "G", "A", "Bb"],
    "F Major": ["F", "G", "A", "Bb", "C", "D", "E", "F"],
}

RELATIVE_MINORS: dict[str, str] = {
    "C Major": "A Minor",
    "G Major": "E Minor",
    "D Major": "B Minor",
    "A Major": "F# Minor",
    "E Major": "C# Minor",
    "B Major": "G# Minor",
    "F# Major": "D# Minor",
    "Gb Major": "Eb Minor",
    "Db Major": "Bb Minor",
    "Ab Major": "F Minor",
    "Eb Major": "C Minor",
    "Bb Major": "G Minor",
    "F Major": "D Minor",
}

KEY_ALIASES: dict[str, str] = {
    "C": "C Major",
    "G": "G Major",
    "D": "D Major",
    "A": "A Major",
    "E": "E Major",
    "B": "B Major",
    "F#": "F# Major",
    "GB": "Gb Major",
    "DB": "Db Major",
    "AB": "Ab Major",
    "EB": "Eb Major",
    "BB": "Bb Major",
    "F": "F Major",
    "C#": "Db Major",
}


def normalize_project_key(value: str) -> str | None:
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None
    title_cleaned = cleaned.title().replace("#", "#")
    if title_cleaned in MAJOR_SCALES:
        return title_cleaned
    if cleaned in MAJOR_SCALES:
        return cleaned
    upper = cleaned.upper().replace(" MAJOR", "").replace(" MINOR", "")
    return KEY_ALIASES.get(upper)


class KeySelectionWheelDialog(QDialog):
    def __init__(self, selected_key: str = "C Major", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Choose Project Key")
        self.setModal(True)
        self._selected_key = normalize_project_key(selected_key) or "C Major"
        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        heading = QLabel("Key Selection Wheel")
        heading.setObjectName("keyWheelHeading")
        layout.addWidget(heading)

        content_row = QHBoxLayout()
        content_row.setSpacing(12)
        layout.addLayout(content_row)

        wheel_box = QGroupBox("Circle of Fifths")
        wheel_grid = QGridLayout(wheel_box)
        wheel_grid.setContentsMargins(12, 12, 12, 12)
        wheel_grid.setSpacing(8)
        content_row.addWidget(wheel_box, 2)

        slots = [
            ("C Major", "C", 0, 2),
            ("G Major", "G", 1, 3),
            ("D Major", "D", 2, 4),
            ("A Major", "A", 3, 4),
            ("E Major", "E", 4, 4),
            ("B Major", "B", 5, 3),
            ("F# Major", "F# / Gb", 6, 2),
            ("Db Major", "C# / Db", 5, 1),
            ("Ab Major", "Ab", 4, 0),
            ("Eb Major", "Eb", 3, 0),
            ("Bb Major", "Bb", 2, 0),
            ("F Major", "F", 1, 1),
        ]
        for key_name, label, row, column in slots:
            button = QPushButton(f"{label}\n{RELATIVE_MINORS[key_name].replace(' Minor', 'm')}")
            button.setObjectName("keyWheelButton")
            button.setCheckable(True)
            button.setMinimumSize(82, 58)
            button.clicked.connect(lambda _checked=False, key=key_name: self._select_key(key))
            self._buttons[key_name] = button
            wheel_grid.addWidget(button, row, column)

        self.selected_key_label = QLabel("")
        self.selected_key_label.setObjectName("keyWheelSelected")
        self.selected_key_label.setAlignment(Qt.AlignCenter)
        self.scale_notes_label = QLabel("")
        self.scale_notes_label.setObjectName("keyWheelNotes")
        self.scale_notes_label.setAlignment(Qt.AlignCenter)
        self.scale_notes_label.setWordWrap(True)
        wheel_grid.addWidget(self.selected_key_label, 2, 1, 2, 3)
        wheel_grid.addWidget(self.scale_notes_label, 4, 1, 1, 3)

        details_box = QGroupBox("Scale Notes")
        details_layout = QVBoxLayout(details_box)
        self.detail_key_label = QLabel("")
        self.detail_key_label.setObjectName("keyWheelDetailKey")
        self.detail_notes_label = QLabel("")
        self.detail_notes_label.setWordWrap(True)
        self.detail_relative_label = QLabel("")
        self.detail_relative_label.setWordWrap(True)
        details_layout.addWidget(self.detail_key_label)
        details_layout.addWidget(self.detail_notes_label)
        details_layout.addWidget(self.detail_relative_label)
        details_layout.addStretch(1)
        content_row.addWidget(details_box, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._select_key(self._selected_key)

    def selected_key(self) -> str:
        return self._selected_key

    def selected_scale_notes(self) -> list[str]:
        return list(MAJOR_SCALES[self._selected_key])

    def _select_key(self, key_name: str) -> None:
        self._selected_key = key_name
        notes = "  ".join(MAJOR_SCALES[key_name])
        relative = RELATIVE_MINORS[key_name]
        for candidate_key, button in self._buttons.items():
            button.setChecked(candidate_key == key_name)
        self.selected_key_label.setText(key_name)
        self.scale_notes_label.setText(notes)
        self.detail_key_label.setText(key_name)
        self.detail_notes_label.setText(f"Scale: {notes}")
        self.detail_relative_label.setText(f"Relative minor: {relative}")
