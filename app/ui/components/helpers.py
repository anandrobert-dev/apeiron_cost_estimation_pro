"""UI Helper Components for MainWindow"""
from typing import Optional
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.ui.style.theme import THEMES


def card(title: str, value: str, color: str = "#3ddc84", theme: Optional[dict] = None) -> QFrame:
    """Create a styled card widget displaying a metric."""
    f = QFrame()
    f.setObjectName("card")  # Apply stylesheet via objectName
    ly = QVBoxLayout(f)
    ly.setContentsMargins(10, 8, 10, 8)
    
    v = QLabel(value)
    v.setStyleSheet(f"font-size:18px;font-weight:bold;color:{color};background:transparent;")
    v.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    tl = QLabel(title)
    t = theme or THEMES["dark"]
    tl.setStyleSheet(f"font-size:10px;color:{t['text_secondary']};background:transparent;")
    tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    ly.addWidget(v)
    ly.addWidget(tl)
    return f


def section_label(text: str, theme: Optional[dict] = None) -> QLabel:
    """Create a styled section header label."""
    t = theme or THEMES["dark"]
    lb = QLabel(text)
    lb.setStyleSheet(f"font-size:14px;font-weight:bold;color:{t['accent']};padding:4px 0;")
    return lb
