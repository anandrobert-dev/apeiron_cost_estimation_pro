"""
Apeiron CostEstimation Pro – Theme System
==========================================
Corporate light/dark theme with neutral palette.
"""

# ──────────────────────────────────────────────
# CORPORATE COLOR PALETTE
# ──────────────────────────────────────────────

THEMES = {
    "dark": {
        "bg": "#1b1b2f",
        "surface": "#232340",
        "card": "#2c2c4a",
        "accent": "#5b6abf",
        "accent_hover": "#4a59a8",
        "success": "#3ddc84",
        "warning": "#f0a030",
        "danger": "#e05260",
        "text": "#dcdce0",
        "text_secondary": "#8e8ea0",
        "border": "#3a3a55",
        "header_bg": "#5b6abf",
        "chart_bg": "#232340",
        "chart_text": "#dcdce0",
    },
    "light": {
        "bg": "#f4f5f9",
        "surface": "#ffffff",
        "card": "#ffffff",
        "accent": "#3d5a99",
        "accent_hover": "#2e4a80",
        "success": "#27855a",
        "warning": "#c07d20",
        "danger": "#c0392b",
        "text": "#2c3e50",
        "text_secondary": "#7f8c8d",
        "border": "#dcdde1",
        "header_bg": "#3d5a99",
        "chart_bg": "#ffffff",
        "chart_text": "#2c3e50",
    },
}


def build_stylesheet(theme_name: str = "dark") -> str:
    t = THEMES.get(theme_name, THEMES["dark"])
    return f"""
    QMainWindow {{ background-color: {t['bg']}; }}
    QWidget {{
        background-color: {t['bg']}; color: {t['text']};
        font-family: 'Inter', 'Ubuntu', 'Cantarell', sans-serif; font-size: 13px;
    }}
    QTabWidget::pane {{
        border: 1px solid {t['border']}; background-color: {t['surface']};
        border-radius: 4px;
    }}
    QTabBar::tab {{
        background-color: {t['card']}; color: {t['text_secondary']};
        padding: 10px 22px; margin-right: 2px;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
        font-weight: bold; font-size: 13px;
    }}
    QTabBar::tab:selected {{ background-color: {t['accent']}; color: white; }}
    QTabBar::tab:hover {{ background-color: {t['accent_hover']}; color: white; }}
    QGroupBox {{
        border: 1px solid {t['border']}; border-radius: 6px;
        margin-top: 12px; padding-top: 18px;
        font-weight: bold; color: {t['accent']};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 2px 10px; }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {t['card']}; border: 1px solid {t['border']};
        border-radius: 4px; padding: 6px 10px; color: {t['text']}; font-size: 13px;
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {t['accent']};
    }}
    QPushButton {{
        background-color: {t['accent']}; color: white; border: none;
        border-radius: 5px; padding: 8px 20px; font-weight: bold; font-size: 13px;
    }}
    QPushButton:hover {{ background-color: {t['accent_hover']}; }}
    QPushButton[cssClass="danger"] {{ background-color: {t['danger']}; }}
    QPushButton[cssClass="success"] {{ background-color: {t['success']}; }}
    QPushButton[cssClass="warning"] {{ background-color: {t['warning']}; }}
    QTableWidget {{
        background-color: {t['card']}; border: 1px solid {t['border']};
        gridline-color: {t['border']}; border-radius: 4px; font-size: 12px;
    }}
    QTableWidget::item {{ padding: 4px 8px; }}
    QTableWidget::item:selected {{ background-color: {t['accent']}; color: white; }}
    QHeaderView::section {{
        background-color: {t['surface']}; color: {t['accent']};
        border: 1px solid {t['border']}; padding: 6px; font-weight: bold; font-size: 12px;
    }}
    QScrollArea {{ border: none; }}
    """
