from __future__ import annotations

from PySide6.QtWidgets import QApplication


MIDAS_THEME = """
QMainWindow, QWidget {
    background-color: #15121c;
    color: #f3eaff;
    font-size: 13px;
}

QMainWindow {
    border: 1px solid #3d3157;
}

QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    background-color: #181522;
    color: #f7edff;
}

QDockWidget::title {
    background-color: #211b31;
    padding: 6px;
    border: 1px solid #3e315a;
}

QToolBar#midasHeader {
    background-color: rgba(28, 24, 41, 242);
    border-bottom: 1px solid #5d4984;
    spacing: 8px;
}

QLabel#headerHint {
    background-color: rgba(20, 17, 29, 220);
    border: 1px solid #403553;
    border-radius: 5px;
    color: #dacdf2;
    padding: 4px 8px;
}

QMenuBar {
    background-color: #181522;
    color: #f7edff;
}

QMenuBar::item:selected, QMenu::item:selected {
    background-color: #533094;
}

QMenu {
    background-color: #181522;
    border: 1px solid #4c3a72;
    color: #f7edff;
}

QLabel#headerProjectTitle {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    min-width: 130px;
}

QLineEdit#headerSearch {
    background-color: #15111f;
    border: 1px solid #6e57a3;
    border-radius: 8px;
    padding: 7px 10px;
    color: #ffffff;
}

QLineEdit#headerSessionRef {
    background-color: #15111f;
    border: 1px solid #54416f;
    border-radius: 6px;
    color: #ffffff;
    padding: 5px 8px;
}

QGroupBox {
    background-color: rgba(27, 23, 39, 232);
    border: 1px solid #413558;
    border-radius: 7px;
    margin-top: 10px;
    padding: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 7px;
    color: #f3e7ff;
}

QTabWidget::pane {
    border: 1px solid #413558;
    border-radius: 6px;
    background-color: rgba(23, 20, 33, 210);
    top: -1px;
}

QTabBar::tab {
    background-color: #1e1a2c;
    border: 1px solid #3c3155;
    color: #d8c9ef;
    padding: 7px 12px;
    min-width: 76px;
}

QTabBar::tab:selected {
    background-color: #533094;
    color: #ffffff;
}

QPushButton {
    background-color: #2d2440;
    border: 1px solid #6e57a3;
    border-radius: 6px;
    color: #f6eaff;
    padding: 6px 10px;
}

QPushButton:hover {
    background-color: #4b2a81;
    border-color: #c37cff;
}

QPushButton:pressed {
    background-color: #2b184d;
}

QLineEdit, QSpinBox, QComboBox, QListWidget, QTextEdit {
    background-color: #14111f;
    border: 1px solid #3d3154;
    border-radius: 6px;
    color: #f6eaff;
    selection-background-color: #824ee6;
}

QDoubleSpinBox {
    background-color: #14111f;
    border: 1px solid #3d3154;
    border-radius: 6px;
    color: #f6eaff;
}

QSlider::groove:horizontal {
    background-color: #211a31;
    border: 1px solid #3d3154;
    border-radius: 4px;
    height: 8px;
}

QSlider::handle:horizontal {
    background-color: #8f63df;
    border: 1px solid #d8c9ef;
    border-radius: 7px;
    margin: -4px 0;
    width: 14px;
}

QSlider::sub-page:horizontal {
    background-color: #5d38a0;
    border-radius: 4px;
}

QDial#effectMacroDial {
    background-color: #181522;
    color: #f6eaff;
}

QLabel#effectMacroLabel {
    color: #d8c9ef;
    font-size: 11px;
}

QListWidget::item {
    border-radius: 5px;
    padding: 5px;
}

QListWidget::item:selected {
    background-color: #533094;
}

QLabel#workspaceTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}

QLabel#workspaceMode {
    color: #cbb5ff;
}

QLabel#operatorNext {
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
}

QLabel#operatorBridge, QLabel#operatorSession, QLabel#operatorReconcile {
    background-color: rgba(20, 17, 29, 220);
    border: 1px solid #3d3154;
    border-radius: 6px;
    padding: 7px;
}

QLabel#browserHeading {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
}

QLabel#browserHint {
    color: #b9adce;
}

QLabel[sourceChip="true"] {
    background-color: rgba(41, 33, 58, 220);
    border: 1px solid #4a3a68;
    border-radius: 5px;
    color: #d8c9ef;
    padding: 5px;
}

QLabel[mixerStrip="true"] {
    background-color: rgba(22, 19, 31, 235);
    border: 1px solid #4d3b70;
    border-radius: 6px;
    color: #f7edff;
    font-weight: 600;
    min-width: 54px;
    padding: 8px;
}

QFrame#beatCanvas {
    background-color: rgba(18, 16, 25, 235);
    border: 1px solid #44365f;
    border-radius: 7px;
}

QScrollArea#arrangementScrollArea {
    background-color: rgba(18, 16, 25, 235);
    border: 1px solid #44365f;
    border-radius: 7px;
}

QFrame#channelRack {
    background-color: rgba(18, 16, 25, 235);
    border: 1px solid #44365f;
    border-radius: 7px;
}

QFrame#midiNoteGrid {
    background-color: rgba(18, 16, 25, 235);
    border: 1px solid #44365f;
    border-radius: 7px;
}

QLabel[beatLane="true"], QLabel[rackLane="true"] {
    color: #d9c7ff;
    font-weight: 600;
}

QFrame[arrangementTrackHeader="true"] {
    background-color: rgba(74, 74, 78, 190);
    border: 1px solid rgba(110, 110, 116, 190);
    border-radius: 4px;
}

QLineEdit#arrangementTrackName {
    background-color: rgba(31, 31, 36, 170);
    border: 1px solid rgba(100, 100, 108, 160);
    border-radius: 4px;
    color: #f8f8ff;
    font-weight: 600;
    padding: 3px 5px;
}

QLabel#arrangementTrackKind, QLabel#trackNumberLabel {
    color: #d5d2dc;
    font-size: 11px;
}

QPushButton#trackControlButton {
    background-color: #3d3d42;
    border: 1px solid #6c6c75;
    border-radius: 4px;
    color: #f2f2f5;
    padding: 2px 0;
}

QPushButton#trackControlButton:checked {
    background-color: #7d55d8;
}

QPushButton#trackRemoveButton {
    background-color: #3d3d42;
    border: 1px solid #6c6c75;
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
    background-color: #505055;
    border: 1px solid #303036;
    border-radius: 3px;
}

QPushButton#mixerInsertButton, QPushButton#mixerRouteButton, QPushButton#mixerReadButton {
    background-color: #5b5b60;
    border: 1px solid #3b3b40;
    border-radius: 4px;
    color: #f1f1f1;
    padding: 4px 2px;
}

QPushButton#mixerSmallButton {
    background-color: #444449;
    border: 1px solid #2c2c31;
    border-radius: 4px;
    color: #f1f1f1;
    padding: 3px 0;
}

QPushButton#mixerSmallButton:checked {
    background-color: #3f8d54;
}

QLabel#mixerStripName {
    background-color: #3f3f44;
    border-top: 1px solid #303036;
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
    background-color: #4d4d53;
}

QLabel[midiCell="true"] {
    border-radius: 3px;
    min-width: 12px;
    min-height: 12px;
}

QScrollBar:vertical {
    background-color: #120821;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #5b2e93;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


def apply_midas_theme(app: QApplication) -> None:
    app.setStyleSheet(MIDAS_THEME)
