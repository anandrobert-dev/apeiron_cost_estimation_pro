"""
Apeiron CostEstimation Pro – Main PyQt6 Application Window
===========================================================
Orchestrates 4 major tabs: Master Data, Estimation, Analysis, Proposal Export
Manages theme, database session, audit, and common state
"""
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt

from app.persistence.database import get_session, init_database
from app.persistence.models import (
    RegionMultiplier, Employee, Project
)
from app.persistence.repositories.audit_repository import AuditRepository
from app.utils.formatting import format_inr
from app.application.estimation_service import EstimationService
from app.persistence.repositories.multiplier_repository import MultiplierRepository
from app.ui.style.theme import THEMES, build_stylesheet
from app.ui.components.dialogs import SOPWindow
from app.ui.tabs.master_data_tab import MasterDataTab
from app.ui.tabs.estimation_tab import EstimationTab
from app.ui.tabs.analysis_tab import AnalysisTab
from app.ui.tabs.proposal_export_tab import ProposalExportTab


class MainWindow(QMainWindow):
    """Main application window orchestrating 4 major tabs."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apeiron CostEstimation Pro")
        self.setMinimumSize(1024, 700)
        
        # Core state
        self._theme_name = "dark"
        self._theme = THEMES["dark"]
        self.session = get_session()
        self.audit_repo = AuditRepository(self.session)
        self.estimation_service = EstimationService(MultiplierRepository(self.session))
        
        # Initialize tab placeholders (will be set in _build_window)
        self.master_tab = None
        self.estimation_tab = None
        self.analysis_tab = None
        self.proposal_tab = None
        
        # Build UI
        self._build_window()
        self._refresh_all()

    def _build_window(self):
        """Build main window layout with header, tabs, and footer."""
        central = QWidget()
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(6, 6, 6, 6)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Apeiron CostEstimation Pro")
        title.setStyleSheet(
            f"font-size:18px;font-weight:bold;color:{self._theme['accent']};padding:6px;"
        )
        hdr.addWidget(title)
        hdr.addStretch()
        
        self.sop_btn = QPushButton("📖 Open SOP Guide")
        self.sop_btn.setFixedWidth(160)
        self.sop_btn.clicked.connect(self._open_sop)
        hdr.addWidget(self.sop_btn)
        
        self.theme_btn = QPushButton("Switch to Light")
        self.theme_btn.setFixedWidth(140)
        self.theme_btn.clicked.connect(self._toggle_theme)
        hdr.addWidget(self.theme_btn)
        
        ml.addLayout(hdr)

        # Tab widget
        self.tabs = QTabWidget()
        self.master_tab = MasterDataTab(self)
        self.estimation_tab = EstimationTab(self)
        self.analysis_tab = AnalysisTab(self)
        self.proposal_tab = ProposalExportTab(self)
        
        self.tabs.addTab(self.master_tab, "Master Data")
        self.tabs.addTab(self.estimation_tab, "New Estimation")
        self.tabs.addTab(self.analysis_tab, "Analysis")
        self.tabs.addTab(self.proposal_tab, "Proposal Export")
        
        ml.addWidget(self.tabs)

        # Footer
        footer = QLabel(
            "© 2026 Koinonia Technologies. All rights reserved.\n"
            "Proprietary Software | Independent Development"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #757575; font-size: 11px; padding: 4px;")
        ml.addWidget(footer)

        self.statusBar().showMessage("Ready")

    def _open_sop(self):
        """Open SOP guide dialog."""
        if not hasattr(self, "sop_window") or self.sop_window is None:
            self.sop_window = SOPWindow(self)
        self.sop_window.show()

    def _toggle_theme(self):
        """Toggle between light and dark theme."""
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        self._theme = THEMES[self._theme_name]
        QApplication.instance().setStyleSheet(build_stylesheet(self._theme_name))
        self.theme_btn.setText(
            "Switch to Dark" if self._theme_name == "light" else "Switch to Light"
        )

    # ═══════════════ REFRESH HELPERS ═══════════════
    
    def _refresh_emp_combo(self):
        """Update employee combobox in Estimation tab."""
        if self.estimation_tab is None:
            return
        self.estimation_tab.mod_emp.clear()
        for e in self.session.query(Employee).filter_by(is_active=True).all():
            self.estimation_tab.mod_emp.addItem(
                f"{e.name} ({e.role}) – {format_inr(e.hourly_cost)}/hr", e.id
            )

    def _refresh_proj_combos(self):
        """Update project comboboxes in Analysis and Proposal tabs."""
        if self.analysis_tab is None or self.proposal_tab is None:
            return
        
        for cb in [self.analysis_tab.an_proj, self.proposal_tab.prop_proj]:
            cb.clear()
            for p in self.session.query(Project).all():
                cb.addItem(f"{p.name} ({p.client_name})", p.id)

    def _refresh_all(self):
        """Refresh all tab data."""
        self._refresh_emp_combo()
        self._refresh_proj_combos()
        self.master_tab._refresh_all()
        self.estimation_tab._refresh_estimation_combos()
