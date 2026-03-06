"""Proposal Export Tab – PDF proposal generation"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QComboBox, QPushButton, QSpinBox, QTextEdit, QLabel,
    QFileDialog, QMessageBox
)

from app.persistence.models import Project
from app.utils.formatting import format_inr
from app.utils.proposal_generator import generate_proposal_pdf
from app.ui.components.helpers import section_label


class ProposalExportTab(QWidget):
    """Tab for exporting client proposals as PDF."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.session = main_window.session
        self._build_ui()

    def _build_ui(self):
        """Build proposal export tab UI."""
        layout = QVBoxLayout(self)
        layout.addWidget(section_label("Client Proposal Export", self.main._theme))
        
        # Project selector
        pr = QHBoxLayout()
        pr.addWidget(QLabel("Project:"))
        self.prop_proj = QComboBox()
        pr.addWidget(self.prop_proj, 1)
        layout.addLayout(pr)

        # Options groupbox
        og = QGroupBox("Options")
        ogl = QFormLayout(og)
        
        self.prop_terms = QTextEdit()
        self.prop_terms.setPlaceholderText(
            "e.g., 40% advance, 30% milestone, 30% delivery"
        )
        self.prop_terms.setMaximumHeight(70)
        
        self.prop_maint = QComboBox()
        self.prop_maint.addItems(["Yes", "No"])
        
        self.prop_yrs = QSpinBox()
        self.prop_yrs.setRange(0, 5)
        self.prop_yrs.setValue(1)
        
        ogl.addRow("Payment Terms:", self.prop_terms)
        ogl.addRow("Include Maintenance:", self.prop_maint)
        ogl.addRow("Maintenance Years:", self.prop_yrs)
        layout.addWidget(og)

        # Preview
        layout.addWidget(QLabel("Preview:"))
        self.prop_preview = QTextEdit()
        self.prop_preview.setReadOnly(True)
        layout.addWidget(self.prop_preview)

        # Buttons
        br = QHBoxLayout()
        pvb = QPushButton("Preview")
        pvb.clicked.connect(self._preview_prop)
        exb = QPushButton("Export PDF")
        exb.setProperty("cssClass", "success")
        exb.clicked.connect(self._export_pdf)
        br.addWidget(pvb)
        br.addWidget(exb)
        layout.addLayout(br)

    def _preview_prop(self):
        """Show proposal preview text."""
        pid = self.prop_proj.currentData()
        if not pid:
            return
        
        p = self.session.query(Project).get(pid)
        est = p.estimate
        
        L = [
            f"PROJECT: {p.name}",
            f"CLIENT: {p.client_name}",
            f"TYPE: {p.app_type}",
            f"COMPLEXITY: {p.complexity}",
            f"TIMELINE: {p.estimated_duration_months} months",
            ""
        ]
        
        if est:
            L.append(f"TOTAL INVESTMENT: {format_inr(est.final_price)}")
        
        L.append("\nMODULES:")
        for m in p.modules:
            L.append(f"  - {m.name}")
        
        L.append(f"\nPAYMENT TERMS: {self.prop_terms.toPlainText()}")
        
        self.prop_preview.setPlainText("\n".join(L))

    def _export_pdf(self):
        """Export proposal as PDF."""
        pid = self.prop_proj.currentData()
        if not pid:
            QMessageBox.warning(self, "Error", "Select a project.")
            return
        
        p = self.session.query(Project).get(pid)
        if not p.estimate:
            QMessageBox.warning(self, "Error", "No estimation for project.")
            return
        
        fp, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", f"{p.name}_Proposal.pdf", "PDF (*.pdf)"
        )
        if not fp:
            return
        
        est = p.estimate
        maint = p.maintenance_records
        
        sd = {
            s: est.gross_cost * getattr(p, f"stage_{s.lower()}_pct") / 100
            for s in ["Planning", "Design", "Development", "Testing", "Deployment"]
        }
        
        generate_proposal_pdf(
            filepath=fp,
            project_name=p.name,
            client_name=p.client_name,
            app_type=p.app_type,
            complexity=p.complexity,
            description=p.description,
            timeline_months=p.estimated_duration_months,
            scope_modules=[m.name for m in p.modules],
            final_price=est.final_price,
            stage_distribution=sd,
            maintenance_annual=maint[0].annual_cost if maint else 0,
            maintenance_years=self.prop_yrs.value(),
            payment_terms=self.prop_terms.toPlainText(),
            include_maintenance=self.prop_maint.currentText() == "Yes"
        )
        
        QMessageBox.information(self, "Exported", f"PDF saved:\n{fp}")
