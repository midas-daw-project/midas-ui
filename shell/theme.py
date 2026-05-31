from __future__ import annotations

from PySide6.QtWidgets import QApplication


MIDAS_THEME = """
QMainWindow, QWidget {
    background-color: #130a24;
    color: #f3eaff;
    font-size: 13px;
}

QMainWindow {
    border: 1px solid #5c2ca0;
}

QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    background-color: #180d2f;
    color: #f7edff;
}

QDockWidget::title {
    background-color: #251245;
    padding: 6px;
    border: 1px solid #4f2687;
}

QToolBar#midasHeader {
    background-color: rgba(32, 14, 60, 230);
    border-bottom: 1px solid #6c35ad;
    spacing: 8px;
}

QMenuBar {
    background-color: #180d2f;
    color: #f7edff;
}

QMenuBar::item:selected, QMenu::item:selected {
    background-color: #533094;
}

QMenu {
    background-color: #180d2f;
    border: 1px solid #5b2e93;
    color: #f7edff;
}

QLabel#headerProjectTitle {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    min-width: 130px;
}

QLineEdit#headerSearch {
    background-color: #1b0d35;
    border: 1px solid #7540bb;
    border-radius: 8px;
    padding: 7px 10px;
    color: #ffffff;
}

QGroupBox {
    background-color: rgba(35, 18, 66, 210);
    border: 1px solid #5b2e93;
    border-radius: 7px;
    margin-top: 12px;
    padding: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 7px;
    color: #f7dfff;
}

QTabWidget::pane {
    border: 1px solid #5b2e93;
    border-radius: 6px;
    background-color: rgba(29, 15, 55, 190);
    top: -1px;
}

QTabBar::tab {
    background-color: #21113f;
    border: 1px solid #4f2687;
    color: #d9c7ff;
    padding: 7px 12px;
    min-width: 76px;
}

QTabBar::tab:selected {
    background-color: #533094;
    color: #ffffff;
}

QPushButton {
    background-color: #38205f;
    border: 1px solid #7d48c6;
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
    background-color: #170c2e;
    border: 1px solid #50307f;
    border-radius: 6px;
    color: #f6eaff;
    selection-background-color: #824ee6;
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
    font-size: 22px;
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
    background-color: rgba(23, 12, 46, 190);
    border: 1px solid #4e2a84;
    border-radius: 6px;
    padding: 7px;
}

QLabel#browserHeading {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
}

QLabel[mixerStrip="true"] {
    background-color: rgba(21, 11, 43, 220);
    border: 1px solid #5e329a;
    border-radius: 6px;
    color: #f7edff;
    font-weight: 600;
    min-width: 54px;
    padding: 8px;
}

QFrame#beatCanvas {
    background-color: rgba(19, 10, 36, 210);
    border: 1px solid #533094;
    border-radius: 7px;
}

QLabel[beatLane="true"] {
    color: #d9c7ff;
    font-weight: 600;
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
    min-width: 12px;
    min-height: 16px;
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
