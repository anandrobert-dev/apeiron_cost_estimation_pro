"""Analysis Tab – Project analysis and variance tracking"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QComboBox, QPushButton, QDoubleSpinBox, QTextEdit, QLabel,
    QMessageBox
)
from PyQt6.QtCore import Qt

from app.persistence.models import Project, Actual
from app.domain.variance_calculator import calculate_variance
from app.utils.formatting import format_inr
from app.ui.components.helpers import card, section_label
from app.ui.components.charts import (
    create_stage_pie_chart, create_variance_bar_chart,
    create_maintenance_line_chart
)


class AnalysisTab(QWidget):
    """Tab for viewing project analysis and variance."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.session = main_window.session
        self._build_ui()

    def _build_ui(self):
        """Build analysis tab UI."""
        layout = QVBoxLayout(self)
        layout.addWidget(section_label("Analysis Dashboard", self.main._theme))
        
        # Project selector
        pr = QHBoxLayout()
        pr.addWidget(QLabel("Project:"))
        self.an_proj = QComboBox()
        pr.addWidget(self.an_proj, 1)
        rb = QPushButton("Load Analysis")
        rb.clicked.connect(self._load_analysis)
        pr.addWidget(rb)
        layout.addLayout(pr)

        # Actual cost input
        ag = QGroupBox("Enter Actual Cost (Post-Completion)")
        agl = QHBoxLayout(ag)
        self.actual_in = QDoubleSpinBox()
        self.actual_in.setRange(0, 1_000_000_000)
        self.actual_in.setPrefix("₹ ")
        self.actual_in.setDecimals(0)
        sab = QPushButton("Save Actual")
        sab.clicked.connect(self._save_actual)
        agl.addWidget(QLabel("Actual Cost:"))
        agl.addWidget(self.actual_in, 1)
        agl.addWidget(sab)
        layout.addWidget(ag)

        # Metric cards
        self.an_cards = QHBoxLayout()
        t = self.main._theme
        self.an_c_est = card("Estimated", "--", t['accent'], t)
        self.an_c_act = card("Actual", "--", t['success'], t)
        self.an_c_var = card("Variance", "--", t['warning'], t)
        self.an_c_cls = card("Classification", "--", t['danger'], t)
        self.an_cards.addWidget(self.an_c_est)
        self.an_cards.addWidget(self.an_c_act)
        self.an_cards.addWidget(self.an_c_var)
        self.an_cards.addWidget(self.an_c_cls)
        layout.addLayout(self.an_cards)

        # Charts
        self.an_charts = QHBoxLayout()
        layout.addLayout(self.an_charts)

        # Text report
        self.an_text = QTextEdit()
        self.an_text.setReadOnly(True)
        layout.addWidget(self.an_text)

    def _load_analysis(self):
        """Load analysis for selected project."""
        pid = self.an_proj.currentData()
        if not pid:
            return
        
        p = self.session.query(Project).get(pid)
        est = p.estimate
        act = p.actual
        t = self.main._theme

        # Clear old charts
        while self.an_charts.count():
            w = self.an_charts.takeAt(0).widget()
            if w:
                w.deleteLater()

        if est:
            self._upd_card(self.an_c_est, "Estimated", format_inr(est.final_price))

            # Stage pie
            sd = {
                "Planning": est.gross_cost * p.stage_planning_pct / 100,
                "Design": est.gross_cost * p.stage_design_pct / 100,
                "Development": est.gross_cost * p.stage_development_pct / 100,
                "Testing": est.gross_cost * p.stage_testing_pct / 100,
                "Deployment": est.gross_cost * p.stage_deployment_pct / 100,
            }
            self.an_charts.addWidget(create_stage_pie_chart(sd, t))

            # Maintenance chart
            maint = p.maintenance_records
            if maint:
                fc = [
                    {
                        "year": m.year,
                        "annual_cost": m.annual_cost,
                        "cumulative_cost": m.annual_cost * m.year
                    }
                    for m in sorted(maint, key=lambda x: x.year)
                ]
                self.an_charts.addWidget(create_maintenance_line_chart(fc, t))

        if act:
            self._upd_card(self.an_c_act, "Actual", format_inr(act.actual_cost))
            if est:
                v = calculate_variance(est.final_price, act.actual_cost)
                self._upd_card(self.an_c_var, "Variance", f"{v['variance_pct']}%")
                self._upd_card(self.an_c_cls, "Classification", v["classification"])
                self.an_charts.addWidget(create_variance_bar_chart(est.final_price, act.actual_cost, t))
        else:
            self._upd_card(self.an_c_act, "Actual", "--")
            self._upd_card(self.an_c_var, "Variance", "--")
            self._upd_card(self.an_c_cls, "Classification", "--")

        # Text report
        L = []
        if est:
            L.append(f"Project: {p.name}")
            L.append(
                f"Labor: {format_inr(est.total_labor_cost)}  |  "
                f"Infra: {format_inr(est.total_infra_cost)}  |  "
                f"Stack: {format_inr(est.total_stack_cost)}"
            )
            L.append(
                f"Gross: {format_inr(est.gross_cost)}  |  "
                f"Safe: {format_inr(est.safe_cost)}  |  "
                f"Final: {format_inr(est.final_price)}"
            )
            L.append(f"Burn Rate/mo: {format_inr(est.burn_rate_monthly)}")
        
        if p.modules:
            L.append("\nModules:")
            for m in p.modules:
                en = m.employee.name if m.employee else "N/A"
                L.append(
                    f"  {m.name:28s} {m.estimated_hours:7.1f}h  "
                    f"{format_inr(m.cost):>13s}  ({en})"
                )
        
        self.an_text.setPlainText("\n".join(L))

    def _save_actual(self):
        """Save actual cost for selected project."""
        pid = self.an_proj.currentData()
        if not pid:
            return
        
        cost = self.actual_in.value()
        p = self.session.query(Project).get(pid)
        
        if p.actual:
            old = p.actual.actual_cost
            p.actual.actual_cost = cost
            self.main.audit_repo.log("actuals", p.actual.id, "UPDATE", "actual_cost", str(old), str(cost))
        else:
            a = Actual(project_id=pid, actual_cost=cost)
            self.session.add(a)
            self.session.flush()
            self.main.audit_repo.log("actuals", a.id, "CREATE")
        
        self.session.commit()
        self._load_analysis()
        QMessageBox.information(self, "Saved", "Actual cost saved.")

    def _upd_card(self, card_widget, title, value):
        """Update card widget value and title."""
        labels = card_widget.findChildren(QLabel)
        if len(labels) >= 2:
            labels[0].setText(value)
            labels[1].setText(title)
