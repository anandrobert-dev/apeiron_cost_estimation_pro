#!/usr/bin/env python3
"""
Apeiron CostEstimation Pro – Entry Point
=========================================
Launch the PyQt6 desktop application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from app.database import init_database
from app.main_ui import MainWindow
from app.ui_theme import build_stylesheet


def main():
    # Initialize database (create tables + seed defaults)
    init_database()

    app = QApplication(sys.argv)
    app.setApplicationName("Apeiron CostEstimation Pro")
    app.setOrganizationName("TechLogix")
    app.setStyleSheet(build_stylesheet("dark"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
