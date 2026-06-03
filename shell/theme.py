from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True, slots=True)
class MidasSkinPreset:
    name: str
    location: str
    font_source: str
    role: str
    background: str
    panel: str
    accent: str
    secondary_accent: str
    text: str


DEFAULT_MIDAS_SKIN = "Midas Night Forge"

MIDAS_SKIN_PRESETS = (
    MidasSkinPreset(
        name="Midas Night Forge",
        location="Mount Olympus Signal Forge",
        font_source="Hack",
        role="Default dark production skin for long DAW sessions.",
        background="#090b10",
        panel="#121722",
        accent="#9a35ff",
        secondary_accent="#36c8ff",
        text="#eef3ff",
    ),
    MidasSkinPreset(
        name="Poseidon Wave Harbor",
        location="Poseidon Wave Harbor",
        font_source="HunDIN1451",
        role="Cool technical skin for audio engine, Waves, routing, and device views.",
        background="#071015",
        panel="#10202a",
        accent="#36c8ff",
        secondary_accent="#8f63df",
        text="#edfaff",
    ),
    MidasSkinPreset(
        name="Athena Type Foundry",
        location="Athena Type Foundry",
        font_source="Font Book",
        role="Typography review skin for choosing and testing future MIDAS fonts.",
        background="#111015",
        panel="#1d1a24",
        accent="#d8b45f",
        secondary_accent="#b48cff",
        text="#fff7e5",
    ),
    MidasSkinPreset(
        name="Mnemosyne Idea Garden",
        location="Mnemosyne Idea Garden",
        font_source="Freeform",
        role="Planning skin for moodboards, arrangement maps, notes, and creative direction.",
        background="#0d1017",
        panel="#161d24",
        accent="#64d6b6",
        secondary_accent="#d8b45f",
        text="#f1fff9",
    ),
)


def available_midas_skins() -> tuple[str, ...]:
    return tuple(skin.name for skin in MIDAS_SKIN_PRESETS)


def get_midas_skin(name: str = DEFAULT_MIDAS_SKIN) -> MidasSkinPreset:
    normalized = name.strip().lower()
    for skin in MIDAS_SKIN_PRESETS:
        if skin.name.lower() == normalized:
            return skin
    return MIDAS_SKIN_PRESETS[0]


MIDAS_THEME = """
QMainWindow, QWidget {
    background-color: #0b0d12;
    color: #eef3ff;
    font-size: 13px;
}

QMainWindow {
    border: 1px solid #222936;
}

QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    background-color: #10141d;
    color: #eef3ff;
}

QDockWidget::title {
    background-color: #151b27;
    padding: 6px;
    border: 1px solid #283244;
}

QToolBar#midasHeader {
    background-color: #080a12;
    border-bottom: 1px solid #23293a;
    spacing: 8px;
}

QFrame#headerSeparator {
    background-color: #1c2130;
    max-height: 1px;
}

QLabel#headerHint {
    background-color: rgba(10, 13, 24, 230);
    border: 1px solid #202840;
    border-radius: 5px;
    color: #aeb9d1;
    padding: 4px 8px;
}

QMenuBar {
    background-color: #111722;
    color: #eef3ff;
}

QMenuBar::item:selected, QMenu::item:selected {
    background-color: #26344d;
}

QMenu {
    background-color: #111722;
    border: 1px solid #2b3651;
    color: #eef3ff;
}

QLabel#headerProjectTitle {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    min-width: 190px;
}

QLineEdit#headerSearch {
    background-color: #0d101b;
    border: 1px solid #263049;
    border-radius: 8px;
    padding: 7px 10px;
    color: #ffffff;
}

QLineEdit#headerSessionRef {
    background-color: #0d101b;
    border: 1px solid #283047;
    border-radius: 6px;
    color: #ffffff;
    padding: 5px 8px;
}

QPushButton#transportPrimary, QPushButton#transportButton, QPushButton#transportRecordButton {
    background-color: #101522;
    border: 1px solid #28324a;
    border-radius: 7px;
    min-width: 58px;
    padding: 7px 10px;
}

QPushButton#transportPrimary:hover, QPushButton#transportButton:hover {
    background-color: #182033;
    border-color: #36c8ff;
}

QPushButton#transportRecordButton {
    background-color: #211016;
    border-color: #5d2531;
    color: #ff7a89;
}

QPushButton#transportRecordButton:hover {
    background-color: #3a1520;
    border-color: #ff4d62;
}

QPushButton#headerModeButton {
    background-color: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    color: #d8deef;
    font-size: 14px;
    min-width: 86px;
    padding: 9px 12px;
}

QPushButton#headerModeButton:checked {
    border-bottom-color: #9a35ff;
    color: #ffffff;
    background-color: rgba(154, 53, 255, 38);
}

QDoubleSpinBox#tempoInput,
QSpinBox#sampleRateInput,
QSpinBox#bufferSizeInput,
QComboBox#meterCombo,
QComboBox#snapCombo,
QComboBox#workspacePresetCombo,
QPushButton#keyButton {
    background-color: #0d101b;
    border: 1px solid #2b3651;
    border-radius: 7px;
    color: #ffffff;
    font-weight: 600;
    min-height: 24px;
    padding: 5px 8px;
}

QDoubleSpinBox#tempoInput {
    min-width: 112px;
}

QSpinBox#sampleRateInput {
    min-width: 102px;
}

QSpinBox#bufferSizeInput {
    min-width: 92px;
}

QPushButton#keyButton {
    color: #efe4ff;
    min-width: 92px;
}

QComboBox#workspacePresetCombo {
    min-width: 108px;
}

QPushButton#panelToggleButton {
    background-color: #101522;
    border: 1px solid #28324a;
    border-radius: 6px;
    color: #d8deef;
    padding: 5px 8px;
}

QPushButton#panelToggleButton:hover {
    border-color: #36c8ff;
}

QPushButton#panelToggleButton:checked {
    background-color: rgba(154, 53, 255, 42);
    border-color: #9a35ff;
    color: #ffffff;
}

QLabel#keyNotesLabel {
    background-color: #0d101b;
    border: 1px solid #202840;
    border-radius: 6px;
    color: #bfc8dc;
    padding: 7px 10px;
}

QLabel#deviceStatusLabel, QLabel#runtimeStatusLabel, QLabel#statusChip {
    color: #bfc8dc;
    padding: 4px 7px;
}

QLabel#statusChip {
    background-color: #25121a;
    border: 1px solid #5b2231;
    border-radius: 11px;
    color: #ff7a89;
}

QLabel#statusChip[online="true"] {
    background-color: #102316;
    border-color: #2c7a40;
    color: #35f071;
}

QGroupBox {
    background-color: rgba(13, 17, 25, 240);
    border: 1px solid #252d3d;
    border-radius: 5px;
    margin-top: 10px;
    padding: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 7px;
    color: #d8e0f2;
}

QTabWidget::pane {
    border: 1px solid #273245;
    border-radius: 5px;
    background-color: rgba(12, 16, 24, 220);
    top: -1px;
}

QTabBar::tab {
    background-color: #141a25;
    border: 1px solid #2b3447;
    color: #c8d2e8;
    padding: 7px 12px;
    min-width: 76px;
}

QTabBar::tab:selected {
    background-color: #26344d;
    color: #ffffff;
}

QPushButton {
    background-color: #111624;
    border: 1px solid #2c3650;
    border-radius: 5px;
    color: #eef3ff;
    padding: 6px 10px;
}

QPushButton:hover {
    background-color: #182033;
    border-color: #36c8ff;
}

QPushButton:pressed {
    background-color: #1e2b40;
}

QLineEdit, QSpinBox, QComboBox, QListWidget, QTextEdit {
    background-color: #0d1119;
    border: 1px solid #293449;
    border-radius: 5px;
    color: #eef3ff;
    selection-background-color: #2f5f85;
}

QDoubleSpinBox {
    background-color: #0d1119;
    border: 1px solid #293449;
    border-radius: 5px;
    color: #eef3ff;
}

QSlider::groove:horizontal {
    background-color: #171d29;
    border: 1px solid #30394c;
    border-radius: 4px;
    height: 8px;
}

QSlider::handle:horizontal {
    background-color: #9a35ff;
    border: 1px solid #d8c2ff;
    border-radius: 7px;
    margin: -4px 0;
    width: 14px;
}

QSlider::sub-page:horizontal {
    background-color: #44306c;
    border-radius: 4px;
}

QDial#effectMacroDial {
    background-color: #111722;
    color: #eef3ff;
}

QLabel#effectMacroLabel {
    color: #c8d2e8;
    font-size: 11px;
}

QListWidget::item {
    border-radius: 5px;
    padding: 5px;
}

QListWidget::item:selected {
    background-color: #26344d;
}

QLabel#workspaceTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}

QLabel#workspaceMode {
    color: #aeb9d1;
}

QFrame#dawControlStrip, QFrame#viewModeStrip, QFrame#projectStatusStrip {
    background-color: #0f141d;
    border: 1px solid #2a3040;
    border-radius: 4px;
}

QLabel#dawStripLabel, QLabel#trackPanelHeaderLabel, QLabel#timelineHeaderLabel {
    color: #d8deef;
    font-weight: 700;
}

QLabel#trackPanelHeaderLabel {
    min-width: 154px;
}

QLabel#timelineHeaderLabel {
    color: #d8b45f;
}

QGroupBox#arrangeView, QGroupBox#workspaceEditorBox {
    background-color: #0f1118;
    border: 1px solid #2b3140;
    border-radius: 4px;
    margin-top: 10px;
}

QFrame#arrangeRuler {
    background-color: #151922;
    border: 1px solid #303745;
    border-radius: 3px;
}

QLabel#rulerTrackLabel {
    color: #c3c9d6;
    font-size: 11px;
    font-weight: 700;
    min-width: 184px;
}

QLabel#rulerMarkerLabel {
    color: #98a2b8;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#modeButton {
    background-color: #151922;
    border: 1px solid #303745;
    border-radius: 4px;
    color: #cbd4e8;
    font-weight: 600;
    padding: 5px 10px;
}

QPushButton#modeButton:checked {
    background-color: #252b36;
    border-color: #9a35ff;
    color: #ffffff;
}

QLabel#keyWheelHeading {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}

QPushButton#keyWheelButton {
    background-color: #0d101b;
    border: 1px solid #2b3651;
    border-radius: 6px;
    color: #f2ecff;
    font-weight: 700;
}

QPushButton#keyWheelButton:checked {
    background-color: #6733c7;
    border-color: #dcb8ff;
    color: #ffffff;
}

QLabel#keyWheelSelected {
    background-color: #101522;
    border: 1px solid #8f63df;
    border-radius: 8px;
    color: #ffffff;
    font-size: 20px;
    font-weight: 800;
    padding: 12px;
}

QLabel#keyWheelNotes {
    color: #d9e2f8;
    font-size: 14px;
    font-weight: 600;
}

QLabel#keyWheelDetailKey {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
}

QLabel#onboardingHeading {
    color: #ffffff;
    font-size: 20px;
    font-weight: 800;
}

QLabel#onboardingIntro {
    color: #c8d2ea;
    font-size: 14px;
}

QLabel#onboardingFeatureName {
    color: #ffffff;
    font-weight: 700;
    min-width: 88px;
}

QLabel#shortcutKey {
    background-color: #0d101b;
    border: 1px solid #2b3651;
    border-radius: 5px;
    color: #fff0c2;
    font-weight: 700;
    min-width: 92px;
    padding: 5px 8px;
}

QLabel#shortcutAction {
    color: #d9e2f8;
    min-width: 130px;
    padding-right: 18px;
}

QLabel#operatorNext {
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
}

QLabel#operatorBridge, QLabel#operatorSession, QLabel#operatorReconcile {
    background-color: rgba(15, 20, 29, 225);
    border: 1px solid #2b3447;
    border-radius: 6px;
    padding: 5px 7px;
}

QLabel#browserHeading {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
}

QLabel#browserHint {
    color: #aeb9d1;
}

QLabel#pluginQueueLabel {
    background-color: #10131b;
    border: 1px solid #2a3040;
    border-radius: 4px;
    color: #d8c2ff;
    font-weight: 700;
    padding: 6px;
}

QLabel#pluginExplanationBubble {
    background-color: #101722;
    border: 1px solid #3a4252;
    border-radius: 8px;
    color: #edf2ff;
    font-weight: 600;
    min-height: 92px;
    padding: 10px;
}

QPushButton#pluginWheelButton {
    background-color: #171f2d;
    border: 1px solid #3d485c;
    border-radius: 24px;
    color: #eef2ff;
    font-weight: 700;
    min-height: 46px;
    min-width: 76px;
    padding: 6px;
}

QPushButton#pluginWheelButton:checked {
    background-color: #3a245e;
    border-color: #9a35ff;
    color: #ffffff;
}

QLabel[sourceChip="true"] {
    background-color: rgba(22, 29, 42, 225);
    border: 1px solid #344057;
    border-radius: 5px;
    color: #c8d2e8;
    padding: 5px;
}

QLabel[mixerStrip="true"] {
    background-color: rgba(20, 25, 34, 238);
    border: 1px solid #354050;
    border-radius: 6px;
    color: #eef3ff;
    font-weight: 600;
    min-width: 54px;
    padding: 8px;
}

QFrame#beatCanvas {
    background-color: #141922;
    border: 1px solid #303745;
    border-radius: 3px;
}

QScrollArea#arrangementScrollArea {
    background-color: #11141b;
    border: 1px solid #303745;
    border-radius: 3px;
}

QFrame#channelRack {
    background-color: rgba(15, 20, 29, 238);
    border: 1px solid #303a4e;
    border-radius: 7px;
}

QFrame#midiNoteGrid {
    background-color: rgba(15, 20, 29, 238);
    border: 1px solid #303a4e;
    border-radius: 7px;
}

QLabel[beatLane="true"], QLabel[rackLane="true"] {
    color: #d8e0f2;
    font-weight: 600;
}

QFrame[arrangementTrackHeader="true"] {
    background-color: #252b34;
    border: 1px solid #465064;
    border-radius: 3px;
}

QFrame[arrangementTrackHeader="true"][masterTrack="true"] {
    background-color: #393321;
    border-color: #8d7437;
}

QLineEdit#arrangementTrackName {
    background-color: #181e28;
    border: 1px solid #465064;
    border-radius: 3px;
    color: #f8f8ff;
    font-weight: 600;
    padding: 3px 5px;
}

QLabel#arrangementTrackKind, QLabel#trackNumberLabel, QLabel#trackMeterLabel {
    color: #d5d2dc;
    font-size: 11px;
}

QPushButton#trackControlButton {
    background-color: #2d333d;
    border: 1px solid #4b5463;
    border-radius: 4px;
    color: #f2f2f5;
    padding: 2px 0;
}

QPushButton#trackControlButton:checked {
    background-color: #386f8f;
}

QPushButton#trackRemoveButton {
    background-color: #2d333d;
    border: 1px solid #4b5463;
    border-radius: 4px;
    color: #f2f2f5;
    padding: 2px 0;
}

QPushButton#trackRemoveButton:hover {
    background-color: #7d3548;
}

QLabel#arrangeMarker, QLabel#arrangeTimeMarker, QLabel#midiStepMarker, QLabel#midiPitchLabel {
    color: #a99abc;
    font-size: 11px;
}

QLabel[beatCell="true"] {
    border-radius: 4px;
    min-height: 22px;
    padding-left: 7px;
    color: #ffffff;
    font-weight: 600;
}

QLabel[stepCell="true"] {
    border-radius: 3px;
    min-width: 10px;
    min-height: 13px;
}

QFrame[mixerChannelStrip="true"] {
    background-color: #252b34;
    border: 1px solid #1b2028;
    border-radius: 3px;
}

QPushButton#mixerInsertButton, QPushButton#mixerRouteButton, QPushButton#mixerReadButton {
    background-color: #313946;
    border: 1px solid #202733;
    border-radius: 4px;
    color: #f1f1f1;
    padding: 4px 2px;
}

QPushButton#mixerSmallButton {
    background-color: #303741;
    border: 1px solid #202733;
    border-radius: 4px;
    color: #f1f1f1;
    padding: 3px 0;
}

QPushButton#mixerSmallButton:checked {
    background-color: #3f8d54;
}

QLabel#mixerStripName {
    background-color: #1b2028;
    border-top: 1px solid #303946;
    color: #ffffff;
    font-weight: 700;
    padding: 5px;
}

QLabel#mixerMeterLabel {
    background-color: #202326;
    border-radius: 3px;
    color: #72e36f;
    font-weight: 700;
    padding: 3px;
}

QLabel#mixerScaleLabel {
    color: #c6c6ca;
    font-size: 10px;
}

QDial#mixerPanDial {
    background-color: #252b34;
}

QLabel[midiCell="true"] {
    border-radius: 3px;
    min-width: 12px;
    min-height: 12px;
}

QScrollBar:vertical {
    background-color: #0b0f16;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #3a465a;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


def apply_midas_theme(app: QApplication, skin_name: str = DEFAULT_MIDAS_SKIN) -> None:
    get_midas_skin(skin_name)
    app.setFont(QFont("Helvetica Neue", 13))
    app.setStyleSheet(MIDAS_THEME)
