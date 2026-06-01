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

QLabel#arrangeMarker, QLabel#midiStepMarker, QLabel#midiPitchLabel {
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
