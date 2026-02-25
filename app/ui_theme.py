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
        "bg": "#0A192F",          # True Deep Space Navy
        "surface": "#112240",     # Lighter Navy container
        "card": "#233554",        # Elevated card for high contrast
        "accent": "#3B82F6",      # Bright, unmissable Royal Blue
        "accent_hover": "#60A5FA",
        "success": "#10B981",     # Crisp Emerald
        "warning": "#F59E0B",     # Amber
        "danger": "#EF4444",      # Red
        "text": "#E6F1FF",        # Bright, icy white for readability
        "text_secondary": "#8892B0", # Cool Slate
        "border": "#314264",      # Clearly visible structural borders
        "header_bg": "#0A192F",
        "chart_bg": "#233554",
        "chart_text": "#E6F1FF",
        "chart_palette": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#0EA5E9", "#EC4899", "#14B8A6"]
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
        "border": "#bdc3c7",  # Darkened border for visibility
        "header_bg": "#3d5a99",
        "chart_bg": "#ffffff",
        "chart_text": "#2c3e50",
        "chart_palette": ["#3d5a99", "#27855a", "#c07d20", "#c0392b", "#8e44ad", "#2980b9", "#d35400", "#16a085"]
    },
}


def build_stylesheet(theme_name: str = "dark") -> str:
    t = THEMES.get(theme_name, THEMES["dark"])
    txt_color = t['text']
    btn_text = "#ffffff" if theme_name == "dark" else "#ffffff"
    
    return f"""
    QMainWindow {{ background-color: {t['bg']}; }}
    QWidget {{
        background-color: {t['bg']}; color: {txt_color};
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
        border: 1px solid {t['border']};
        border-bottom: none;
        font-weight: bold; font-size: 13px;
    }}
    QTabBar::tab:selected {{ background-color: {t['accent']}; color: white; border-top: 2px solid {t['accent']}; }}
    QTabBar::tab:hover {{ background-color: {t['accent_hover']}; color: white; }}
    QGroupBox {{
        border: 1px solid {t['border']}; border-radius: 6px;
        margin-top: 3ex; padding-top: 10px;
        font-weight: bold; color: {t['accent']};
        background-color: {t['surface']};
    }}
    QGroupBox::title {{ 
        subcontrol-origin: margin; subcontrol-position: top left; 
        padding: 2px 8px; background-color: {t['surface']};
        border: 1px solid {t['border']}; border-radius: 4px;
        left: 10px;
    }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {t['card']}; border: 1px solid {t['border']};
        border-radius: 4px; padding: 6px 10px; color: {txt_color}; font-size: 13px;
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {t['accent']};
    }}
    QPushButton {{
        background-color: {t['accent']}; color: {btn_text}; border: none;
        border-radius: 5px; padding: 8px 20px; font-weight: bold; font-size: 13px;
    }}
    QPushButton:hover {{ background-color: {t['accent_hover']}; }}
    QPushButton[cssClass="danger"] {{ background-color: {t['danger']}; color: #ffffff; }}
    QPushButton[cssClass="success"] {{ background-color: {t['success']}; color: #ffffff; }}
    QPushButton[cssClass="warning"] {{ background-color: {t['warning']}; color: #ffffff; }}
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
    QScrollArea {{ border: none; background-color: transparent; }}
    QScrollArea > QWidget > QWidget {{ background-color: transparent; }}
    """
