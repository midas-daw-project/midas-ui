from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QFrame,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class DawOnboardingDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to MIDAS")
        self.setModal(False)
        self.setMinimumWidth(620)
        self.resize(720, 680)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        heading = QLabel("MIDAS DAW Navigation")
        heading.setObjectName("onboardingHeading")
        content_layout.addWidget(heading)

        intro = QLabel(
            "Start with the top bar: choose a workspace, set tempo, choose key, then build tracks in the arrangement."
        )
        intro.setWordWrap(True)
        intro.setObjectName("onboardingIntro")
        content_layout.addWidget(intro)

        feature_box = QGroupBox("Workspace Map")
        feature_grid = QGridLayout(feature_box)
        feature_grid.setColumnStretch(1, 1)
        rows = [
            ("Start", "Create, open, save, and resume sessions."),
            ("Arrange", "Build tracks, clips, buses, sends, markers, and song sections."),
            ("Record", "Open the drum and capture workspace for rhythm and take building."),
            ("MIDI", "Open the piano roll for notes, scale-aware ideas, and pattern edits."),
            ("Mix", "Show the mixer and plugin insert workflow."),
            ("Browse", "Open the browser for plugins, instruments, loops, and samples."),
            ("Tempo / Key", "Set BPM directly, or open the key wheel to choose a scale."),
        ]
        for row, (name, description) in enumerate(rows):
            name_label = QLabel(name)
            name_label.setObjectName("onboardingFeatureName")
            description_label = QLabel(description)
            description_label.setWordWrap(True)
            feature_grid.addWidget(name_label, row, 0)
            feature_grid.addWidget(description_label, row, 1)
        content_layout.addWidget(feature_box)

        source_box = QGroupBox("Plugin / Source Families")
        source_grid = QGridLayout(source_box)
        source_grid.setColumnStretch(1, 1)
        source_rows = [
            ("Mount Olympus Signal Forge", "MIDAS insert effects for EQ, compression, and core mix shaping."),
            ("Poseidon Wave Harbor", "Waves Central, WaveShells, and Head Tracker sources for Waves installs, plugin shells, and spatial tools."),
            ("Hephaestus Interface Forge", "Focusrite Control and Scarlett setup utilities for routing, monitoring, firmware, and beginner interface checks."),
            ("Delphi Instrument Temple", "Playable instrument sources such as Sitala drums and Splice Instrument."),
            ("Pactolus Sample River", "Sample and loop sources such as Splice and Cymatics-style packs."),
            ("Phrygia Host Gates", "DAW host references such as REAPER and GarageBand."),
            ("Gordium Action Forge", "REAPER stock FX and SWS-style action extensions."),
            ("Daedalus Automation Labyrinth", "Automation workflow sources for repeatable local actions."),
            ("Rhodes Performance Harbor", "Deck, live set, sampler, and performance-host references."),
            ("Tartarus Manager Vault", "Plugin manager apps for Melda, FL Cloud, IK, and other install/update flows."),
            ("Athena Type Foundry", "Font Book and skin typography tools used to shape the visual language of MIDAS."),
            ("Mnemosyne Idea Garden", "Freeform boards for skin moodboards, arrangement maps, and creative planning."),
            ("Oracle Reference Hall", "Metering and reference tools for checking clarity, balance, and loudness."),
        ]
        for row, (name, description) in enumerate(source_rows):
            name_label = QLabel(name)
            name_label.setObjectName("onboardingFeatureName")
            description_label = QLabel(description)
            description_label.setWordWrap(True)
            source_grid.addWidget(name_label, row, 0)
            source_grid.addWidget(description_label, row, 1)
        content_layout.addWidget(source_box)

        workflow_box = QGroupBox("Plugin Browser Workflow")
        workflow_grid = QGridLayout(workflow_box)
        workflow_grid.setColumnStretch(1, 1)
        workflow_rows = [
            ("Search", "Type a plugin, source, vendor, function, or mythical group name to filter the browser."),
            ("Selection Wheel", "Click a wheel segment to select a plugin/source and read the explanation bubble."),
            ("Queued Chain", "Ready insert effects queue as you select them; setup tools and installers only explain themselves."),
            ("Add FX", "Use Insert or Ctrl+Shift+F to choose an insert effect for the selected mixer slot."),
        ]
        for row, (name, description) in enumerate(workflow_rows):
            name_label = QLabel(name)
            name_label.setObjectName("onboardingFeatureName")
            description_label = QLabel(description)
            description_label.setWordWrap(True)
            workflow_grid.addWidget(name_label, row, 0)
            workflow_grid.addWidget(description_label, row, 1)
        content_layout.addWidget(workflow_box)

        shortcut_box = QGroupBox("Key Commands")
        shortcut_grid = QGridLayout(shortcut_box)
        shortcuts = [
            ("Space", "Play"),
            ("Shift+Space", "Stop"),
            ("Ctrl+Shift+B", "Edit BPM"),
            ("Ctrl+K", "Open key wheel"),
            ("Ctrl+T", "Add track"),
            ("Ctrl+1", "Arrange"),
            ("Ctrl+2", "Record / Drum Machine"),
            ("Ctrl+3", "Piano Roll"),
            ("Ctrl+4", "Mix"),
            ("Ctrl+5", "Browse"),
            ("Ctrl+M", "Toggle mixer"),
            ("Ctrl+B", "Toggle browser"),
            ("Ctrl+Shift+F", "Add FX"),
            ("Ctrl+/", "Show this help"),
        ]
        for row, (keys, action) in enumerate(shortcuts):
            key_label = QLabel(keys)
            key_label.setObjectName("shortcutKey")
            action_label = QLabel(action)
            action_label.setObjectName("shortcutAction")
            shortcut_grid.addWidget(key_label, row // 2, (row % 2) * 2)
            shortcut_grid.addWidget(action_label, row // 2, (row % 2) * 2 + 1)
        shortcut_grid.setAlignment(Qt.AlignTop)
        content_layout.addWidget(shortcut_box)
        layout.addWidget(scroll_area, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
