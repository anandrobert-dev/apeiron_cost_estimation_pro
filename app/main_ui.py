"""
Apeiron CostEstimation Pro – Main PyQt6 UI (Level 2)
=====================================================
Tabs: Master Data | Estimation | Analysis Dashboard | Proposal Export
Features: Charts, Industry Presets, Pricing Modes, Light/Dark Theme
"""
import sys, os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QSplitter, QFileDialog,
    QMessageBox, QScrollArea, QFrame, QSizePolicy,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from app.database import get_session, init_database
from app.models import (
    Employee, Project, ProjectModule, StackCost, InfraCost,
    Estimate, Actual, MaintenanceRecord, RegionMultiplier, AuditLog,
    SystemLookup, AppTypeMultiplier, ComplexityMultiplier,
    PricingStrategy, IndustryPreset, IndustryPresetModule
)
from app.logic import (
    calculate_employee_costs, run_full_estimation, calculate_variance,
    format_inr, create_audit_entry, DEFAULT_STAGES
)
from app.proposal_generator import generate_proposal_pdf
from app.ui_theme import THEMES, build_stylesheet
from app.ui_charts import (
    create_stage_pie_chart, create_variance_bar_chart,
    create_maintenance_line_chart, create_module_cost_bar_chart,
)
from app.ui_sop import SOPWindow
from app.ui_sysconfig import SysConfigTab


def _card(title, value, color="#3ddc84", theme=None):
    t = theme or THEMES["dark"]
    f = QFrame()
    f.setStyleSheet(f"background-color:{t['card']};border:1px solid {t['border']};border-radius:8px;padding:10px;")
    ly = QVBoxLayout(f)
    ly.setContentsMargins(10, 8, 10, 8)
    v = QLabel(value)
    v.setStyleSheet(f"font-size:18px;font-weight:bold;color:{color};background:transparent;")
    v.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tl = QLabel(title)
    tl.setStyleSheet(f"font-size:10px;color:{t['text_secondary']};background:transparent;")
    tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ly.addWidget(v)
    ly.addWidget(tl)
    return f


def _section(text, theme=None):
    t = theme or THEMES["dark"]
    lb = QLabel(text)
    lb.setStyleSheet(f"font-size:14px;font-weight:bold;color:{t['accent']};padding:4px 0;")
    return lb


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apeiron CostEstimation Pro")
        self.setMinimumSize(1024, 700)
        self._theme_name = "dark"
        self._theme = THEMES["dark"]
        self.session = get_session()
        self._estimation_result = None

        central = QWidget()
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(6, 6, 6, 6)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Apeiron CostEstimation Pro")
        title.setStyleSheet(f"font-size:18px;font-weight:bold;color:{self._theme['accent']};padding:6px;")
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

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_master_tab(), "Master Data")
        self.tabs.addTab(self._build_estimation_tab(), "New Estimation")
        self.tabs.addTab(self._build_analysis_tab(), "Analysis")
        self.tabs.addTab(self._build_proposal_tab(), "Proposal Export")
        ml.addWidget(self.tabs)
        
        footer = QLabel("© 2026 Koinonia Technologies. All rights reserved.\nProprietary Software | Independent Development")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #757575; font-size: 11px; padding: 4px;")
        ml.addWidget(footer)

        self.statusBar().showMessage("Ready")
        self._refresh_all()

    def _open_sop(self):
        if not hasattr(self, "sop_window") or self.sop_window is None:
            self.sop_window = SOPWindow(self)
        self.sop_window.show()

    def _toggle_theme(self):
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        self._theme = THEMES[self._theme_name]
        QApplication.instance().setStyleSheet(build_stylesheet(self._theme_name))
        self.theme_btn.setText("Switch to Dark" if self._theme_name == "light" else "Switch to Light")

    # ═══════════════ TAB 1 – MASTER DATA ═══════════════
    def _build_master_tab(self):
        tab = QWidget()
        ly = QVBoxLayout(tab)
        mt = QTabWidget()

        # Employee
        ew = QWidget(); el = QVBoxLayout(ew)
        el.addWidget(_section("Employee Master", self._theme))
        ef = QGroupBox("Add Employee"); efl = QFormLayout(ef)
        self.emp_name = QLineEdit(); self.emp_name.setPlaceholderText("Name")
        self.emp_role = QComboBox(); self.emp_role.setEditable(True)
        self.emp_role.addItems(["Project Manager","UI/UX Designer","Frontend Developer",
            "Backend Developer","Full Stack Developer","QA Engineer","DevOps Engineer",
            "Data Engineer","AI/ML Engineer","Business Analyst","Technical Lead"])
        self.emp_salary = QDoubleSpinBox(); self.emp_salary.setRange(0,10_000_000)
        self.emp_salary.setPrefix("₹ "); self.emp_salary.setDecimals(0)
        self.emp_pf = QDoubleSpinBox(); self.emp_pf.setRange(0,100); self.emp_pf.setValue(12); self.emp_pf.setSuffix(" %")
        self.emp_bonus = QDoubleSpinBox(); self.emp_bonus.setRange(0,100); self.emp_bonus.setValue(8.33); self.emp_bonus.setSuffix(" %")
        self.emp_leave = QDoubleSpinBox(); self.emp_leave.setRange(0,100); self.emp_leave.setValue(4); self.emp_leave.setSuffix(" %")
        self.emp_infra = QDoubleSpinBox(); self.emp_infra.setRange(0,100); self.emp_infra.setValue(5); self.emp_infra.setSuffix(" %")
        self.emp_admin = QDoubleSpinBox(); self.emp_admin.setRange(0,100); self.emp_admin.setValue(3); self.emp_admin.setSuffix(" %")
        for lbl, w in [("Name:",self.emp_name),("Role:",self.emp_role),("Base Salary:",self.emp_salary),
            ("PF:",self.emp_pf),("Bonus:",self.emp_bonus),("Leave:",self.emp_leave),
            ("Infra:",self.emp_infra),("Admin:",self.emp_admin)]:
            efl.addRow(lbl, w)
        br = QHBoxLayout()
        ab = QPushButton("Add Employee"); ab.clicked.connect(self._add_employee); br.addWidget(ab)
        db = QPushButton("Delete Selected"); db.setProperty("cssClass","danger"); db.clicked.connect(self._del_employee); br.addWidget(db)
        el.addWidget(ef); el.addLayout(br)
        self.emp_table = QTableWidget(); self.emp_table.setColumnCount(6)
        self.emp_table.setHorizontalHeaderLabels(["ID","Name","Role","Base Salary","Real Monthly","Hourly Rate"])
        self.emp_table.horizontalHeader().setStretchLastSection(True)
        self.emp_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        el.addWidget(self.emp_table)
        mt.addTab(ew, "Employees")

        # Stack
        sw = QWidget(); sl = QVBoxLayout(sw)
        sl.addWidget(_section("Stack Cost Master", self._theme))
        sf = QGroupBox("Add Stack Cost"); sfl = QFormLayout(sf)
        self.stack_name = QLineEdit(); self.stack_name.setPlaceholderText("Tool/License")
        self.stack_cat = QComboBox(); self.stack_cat.setEditable(True)
        self.stack_cat.addItems(["IDE","Cloud","CI/CD","Monitoring","Database","Other"])
        self.stack_cost = QDoubleSpinBox(); self.stack_cost.setRange(0,10_000_000); self.stack_cost.setPrefix("₹ "); self.stack_cost.setDecimals(0)
        self.stack_bill = QComboBox(); self.stack_bill.addItems(["one_time","monthly","yearly","usage_based"])
        for lbl,w in [("Name:",self.stack_name),("Category:",self.stack_cat),("Cost:",self.stack_cost),("Billing:",self.stack_bill)]:
            sfl.addRow(lbl,w)
        sbr = QHBoxLayout()
        sab = QPushButton("Add Stack Cost"); sab.clicked.connect(self._add_stack); sbr.addWidget(sab)
        sdb = QPushButton("Delete Selected"); sdb.setProperty("cssClass","danger"); sdb.clicked.connect(self._del_stack); sbr.addWidget(sdb)
        sl.addWidget(sf); sl.addLayout(sbr)
        self.stack_table = QTableWidget(); self.stack_table.setColumnCount(4)
        self.stack_table.setHorizontalHeaderLabels(["ID","Name","Cost","Billing"])
        self.stack_table.horizontalHeader().setStretchLastSection(True)
        self.stack_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        sl.addWidget(self.stack_table)
        mt.addTab(sw, "Stack Costs")

        # Infra
        iw = QWidget(); il = QVBoxLayout(iw)
        il.addWidget(_section("Infrastructure Cost Master", self._theme))
        inf = QGroupBox("Add Infra Cost"); ifl = QFormLayout(inf)
        self.infra_name = QLineEdit(); self.infra_name.setPlaceholderText("Item")
        self.infra_cat = QComboBox(); self.infra_cat.setEditable(True)
        self.infra_cat.addItems(["Hosting","Database","API Integration","Security","App Store Fees","Marketing","DevOps","Other"])
        self.infra_cost_in = QDoubleSpinBox(); self.infra_cost_in.setRange(0,10_000_000); self.infra_cost_in.setPrefix("₹ "); self.infra_cost_in.setDecimals(0)
        self.infra_bill = QComboBox(); self.infra_bill.addItems(["one_time","monthly","yearly","usage_based"])
        for lbl,w in [("Name:",self.infra_name),("Category:",self.infra_cat),("Cost:",self.infra_cost_in),("Billing:",self.infra_bill)]:
            ifl.addRow(lbl,w)
        ibr = QHBoxLayout()
        iab = QPushButton("Add Infra Cost"); iab.clicked.connect(self._add_infra); ibr.addWidget(iab)
        idb = QPushButton("Delete Selected"); idb.setProperty("cssClass","danger"); idb.clicked.connect(self._del_infra); ibr.addWidget(idb)
        il.addWidget(inf); il.addLayout(ibr)
        self.infra_table = QTableWidget(); self.infra_table.setColumnCount(4)
        self.infra_table.setHorizontalHeaderLabels(["ID","Name","Cost","Billing"])
        self.infra_table.horizontalHeader().setStretchLastSection(True)
        self.infra_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        il.addWidget(self.infra_table)
        mt.addTab(iw, "Infrastructure")

        # System Configuration Tab
        self.sysconfig_tab = SysConfigTab(self)
        mt.addTab(self.sysconfig_tab, "System Config")

        ly.addWidget(mt)
        return tab

    # ═══════════════ TAB 2 – ESTIMATION ═══════════════
    def _build_estimation_tab(self):
        tab = QWidget()
        sp = QSplitter(Qt.Orientation.Horizontal)

        # LEFT
        left = QScrollArea(); left.setWidgetResizable(True)
        lw = QWidget(); ll = QVBoxLayout(lw)

        pg = QGroupBox("Project Details"); pgl = QFormLayout(pg)
        self.est_name = QLineEdit(); self.est_name.setPlaceholderText("Project Name")
        self.est_client = QLineEdit(); self.est_client.setPlaceholderText("Client Name")
        self.est_desc = QTextEdit(); self.est_desc.setPlaceholderText("Description..."); self.est_desc.setMaximumHeight(70)
        self.est_app = QComboBox()
        self.est_cx = QComboBox()
        self.est_region = QComboBox()
        for r in self.session.query(RegionMultiplier).all():
            self.est_region.addItem(f"{r.region_name} (x{r.multiplier})", r.id)
        self.est_fp = QSpinBox(); self.est_fp.setRange(0,100_000); self.est_fp.setSpecialValueText("N/A")
        self.est_dur = QDoubleSpinBox(); self.est_dur.setRange(0.5,120); self.est_dur.setValue(6); self.est_dur.setSuffix(" months")
        for lbl,w in [("Project:",self.est_name),("Client:",self.est_client),("Description:",self.est_desc),
            ("App Type:",self.est_app),("Complexity:",self.est_cx),("Region:",self.est_region),
            ("Function Points:",self.est_fp),("Duration:",self.est_dur)]:
            pgl.addRow(lbl, w)
        ll.addWidget(pg)

        # Industry Preset
        ipg = QGroupBox("Industry Preset"); ipl = QHBoxLayout(ipg)
        self.preset_combo = QComboBox()
        apply_preset_btn = QPushButton("Apply Preset")
        apply_preset_btn.setProperty("cssClass", "warning")
        apply_preset_btn.clicked.connect(self._apply_preset)
        ipl.addWidget(self.preset_combo, 1)
        ipl.addWidget(apply_preset_btn)
        ll.addWidget(ipg)

        # Pricing Strategy
        psg = QGroupBox("Pricing Strategy"); psgl = QHBoxLayout(psg)
        self.pricing_combo = QComboBox()
        self.pricing_combo.currentIndexChanged.connect(self._apply_pricing_mode)
        psgl.addWidget(self.pricing_combo, 1)
        ll.addWidget(psg)
        
        self._refresh_estimation_combos()

        # Module Hours
        mg = QGroupBox("Module Hours"); mgl = QVBoxLayout(mg)
        mir = QHBoxLayout()
        self.mod_name = QLineEdit(); self.mod_name.setPlaceholderText("Module Name")
        self.mod_emp = QComboBox(); self._refresh_emp_combo()
        self.mod_hrs = QDoubleSpinBox(); self.mod_hrs.setRange(0,100_000); self.mod_hrs.setSuffix(" hrs")
        amb = QPushButton("Add"); amb.clicked.connect(self._add_mod)
        mir.addWidget(self.mod_name, 3); mir.addWidget(self.mod_emp, 2)
        mir.addWidget(self.mod_hrs, 1); mir.addWidget(amb, 1)
        mgl.addLayout(mir)
        self.mod_table = QTableWidget(); self.mod_table.setColumnCount(4)
        self.mod_table.setHorizontalHeaderLabels(["Module","Employee","Hours","Remove"])
        self.mod_table.horizontalHeader().setStretchLastSection(True)
        self.mod_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        mgl.addWidget(self.mod_table)
        ll.addWidget(mg)

        # Risk & Profit
        rg = QGroupBox("Risk and Margin"); rgl = QFormLayout(rg)
        self.est_mb = QDoubleSpinBox(); self.est_mb.setRange(0,50); self.est_mb.setValue(15); self.est_mb.setSuffix(" %")
        self.est_rk = QDoubleSpinBox(); self.est_rk.setRange(0,50); self.est_rk.setValue(10); self.est_rk.setSuffix(" %")
        self.est_pf = QDoubleSpinBox(); self.est_pf.setRange(0,100); self.est_pf.setValue(20); self.est_pf.setSuffix(" %")
        rgl.addRow("Maintenance Buffer:", self.est_mb)
        rgl.addRow("Risk Contingency:", self.est_rk)
        rgl.addRow("Profit Margin:", self.est_pf)
        ll.addWidget(rg)

        t = self._theme
        cb = QPushButton("Calculate Estimation")
        cb.setStyleSheet(f"padding:12px;font-size:14px;background-color:{t['success']};")
        cb.clicked.connect(self._run_estimation)
        ll.addWidget(cb)
        sb = QPushButton("Save Estimation")
        sb.setStyleSheet(f"padding:12px;font-size:14px;background-color:{t['warning']};")
        sb.clicked.connect(self._save_estimation)
        ll.addWidget(sb)
        ll.addStretch()
        left.setWidget(lw)
        sp.addWidget(left)

        # RIGHT
        right = QScrollArea(); right.setWidgetResizable(True)
        rw = QWidget(); self.est_right_layout = QVBoxLayout(rw)
        self.est_right_layout.addWidget(_section("Live Estimation Results", self._theme))
        cl = QHBoxLayout()
        self.c_gross = _card("Gross Cost","₹0",t['success'],t)
        self.c_safe = _card("Safe Cost","₹0",t['warning'],t)
        self.c_final = _card("Final Price","₹0",t['accent'],t)
        self.c_margin = _card("Revenue Margin","0%",t['success'],t)
        cl.addWidget(self.c_gross); cl.addWidget(self.c_safe)
        cl.addWidget(self.c_final); cl.addWidget(self.c_margin)
        self.est_right_layout.addLayout(cl)
        self.est_chart_holder = QVBoxLayout()
        self.est_right_layout.addLayout(self.est_chart_holder)
        self.results_text = QTextEdit(); self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet(f"background-color:{t['card']};border:1px solid {t['border']};border-radius:6px;padding:10px;font-family:monospace;font-size:11px;")
        self.est_right_layout.addWidget(self.results_text)
        self.est_right_layout.addStretch()
        right.setWidget(rw)
        sp.addWidget(right)
        sp.setSizes([480, 600])
        QVBoxLayout(tab).addWidget(sp)
        return tab

    # ═══════════════ TAB 3 – ANALYSIS ═══════════════
    def _build_analysis_tab(self):
        tab = QWidget(); ly = QVBoxLayout(tab)
        ly.addWidget(_section("Analysis Dashboard", self._theme))
        pr = QHBoxLayout()
        pr.addWidget(QLabel("Project:"))
        self.an_proj = QComboBox()
        pr.addWidget(self.an_proj, 1)
        rb = QPushButton("Load Analysis"); rb.clicked.connect(self._load_analysis)
        pr.addWidget(rb)
        ly.addLayout(pr)

        ag = QGroupBox("Enter Actual Cost (Post-Completion)"); agl = QHBoxLayout(ag)
        self.actual_in = QDoubleSpinBox(); self.actual_in.setRange(0,1_000_000_000)
        self.actual_in.setPrefix("₹ "); self.actual_in.setDecimals(0)
        sab = QPushButton("Save Actual"); sab.clicked.connect(self._save_actual)
        agl.addWidget(QLabel("Actual Cost:")); agl.addWidget(self.actual_in,1); agl.addWidget(sab)
        ly.addWidget(ag)

        # Metric cards row
        self.an_cards = QHBoxLayout()
        t = self._theme
        self.an_c_est = _card("Estimated","--",t['accent'],t)
        self.an_c_act = _card("Actual","--",t['success'],t)
        self.an_c_var = _card("Variance","--",t['warning'],t)
        self.an_c_cls = _card("Classification","--",t['danger'],t)
        self.an_cards.addWidget(self.an_c_est); self.an_cards.addWidget(self.an_c_act)
        self.an_cards.addWidget(self.an_c_var); self.an_cards.addWidget(self.an_c_cls)
        ly.addLayout(self.an_cards)

        self.an_charts = QHBoxLayout()
        ly.addLayout(self.an_charts)
        self.an_text = QTextEdit(); self.an_text.setReadOnly(True)
        self.an_text.setStyleSheet(f"background-color:{t['card']};border:1px solid {t['border']};border-radius:6px;padding:10px;font-family:monospace;font-size:11px;")
        ly.addWidget(self.an_text)
        return tab

    # ═══════════════ TAB 4 – PROPOSAL ═══════════════
    def _build_proposal_tab(self):
        tab = QWidget(); ly = QVBoxLayout(tab)
        ly.addWidget(_section("Client Proposal Export", self._theme))
        pr = QHBoxLayout(); pr.addWidget(QLabel("Project:"))
        self.prop_proj = QComboBox(); pr.addWidget(self.prop_proj, 1)
        ly.addLayout(pr)
        og = QGroupBox("Options"); ogl = QFormLayout(og)
        self.prop_terms = QTextEdit()
        self.prop_terms.setPlaceholderText("e.g., 40% advance, 30% milestone, 30% delivery")
        self.prop_terms.setMaximumHeight(70)
        self.prop_maint = QComboBox(); self.prop_maint.addItems(["Yes","No"])
        self.prop_yrs = QSpinBox(); self.prop_yrs.setRange(0,5); self.prop_yrs.setValue(1)
        ogl.addRow("Payment Terms:", self.prop_terms)
        ogl.addRow("Include Maintenance:", self.prop_maint)
        ogl.addRow("Maintenance Years:", self.prop_yrs)
        ly.addWidget(og)
        self.prop_preview = QTextEdit(); self.prop_preview.setReadOnly(True)
        t = self._theme
        self.prop_preview.setStyleSheet(f"background-color:{t['card']};border:1px solid {t['border']};border-radius:6px;padding:10px;font-size:12px;")
        ly.addWidget(QLabel("Preview:")); ly.addWidget(self.prop_preview)
        br = QHBoxLayout()
        pvb = QPushButton("Preview"); pvb.clicked.connect(self._preview_prop)
        exb = QPushButton("Export PDF"); exb.setProperty("cssClass","success"); exb.clicked.connect(self._export_pdf)
        br.addWidget(pvb); br.addWidget(exb)
        ly.addLayout(br)
        return tab

    # ═══════════════ EMPLOYEE CRUD ═══════════════
    def _add_employee(self):
        name = self.emp_name.text().strip()
        if not name: QMessageBox.warning(self,"Validation","Name required."); return
        emp = Employee(name=name, role=self.emp_role.currentText(), base_salary=self.emp_salary.value(),
            pf_pct=self.emp_pf.value(), bonus_pct=self.emp_bonus.value(),
            leave_pct=self.emp_leave.value(), infra_pct=self.emp_infra.value(), admin_pct=self.emp_admin.value())
        calculate_employee_costs(emp)
        self.session.add(emp); self.session.commit()
        create_audit_entry(self.session,"employees",emp.id,"CREATE")
        self._refresh_emp_table(); self._refresh_emp_combo()
        self.emp_name.clear(); self.emp_salary.setValue(0)
        self.statusBar().showMessage(f"Employee '{name}' added.",3000)

    def _del_employee(self):
        r = self.emp_table.currentRow()
        if r < 0: return
        eid = int(self.emp_table.item(r,0).text())
        e = self.session.query(Employee).get(eid)
        if e:
            create_audit_entry(self.session,"employees",eid,"DELETE")
            self.session.delete(e); self.session.commit()
            self._refresh_emp_table(); self._refresh_emp_combo()

    def _refresh_emp_table(self):
        emps = self.session.query(Employee).filter_by(is_active=True).all()
        self.emp_table.setRowCount(len(emps))
        for i,e in enumerate(emps):
            for j,v in enumerate([str(e.id),e.name,e.role,format_inr(e.base_salary),format_inr(e.real_monthly_cost),format_inr(e.hourly_cost)]):
                self.emp_table.setItem(i,j,QTableWidgetItem(v))
        self.emp_table.resizeColumnsToContents()

    def _refresh_emp_combo(self):
        self.mod_emp.clear()
        for e in self.session.query(Employee).filter_by(is_active=True).all():
            self.mod_emp.addItem(f"{e.name} ({e.role}) – {format_inr(e.hourly_cost)}/hr", e.id)

    def _refresh_estimation_combos(self):
        self.est_app.clear()
        for x in self.session.query(AppTypeMultiplier).all():
            self.est_app.addItem(x.name)
            
        self.est_cx.clear()
        for x in self.session.query(ComplexityMultiplier).all():
            self.est_cx.addItem(x.name)
        self.est_cx.setCurrentText("Medium")
        
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem("-- Select Preset --")
        for x in self.session.query(IndustryPreset).all():
            self.preset_combo.addItem(x.name, x.id)
        self.preset_combo.blockSignals(False)
            
        self.pricing_combo.blockSignals(True)
        self.pricing_combo.clear()
        self.pricing_combo.addItem("-- Custom --")
        for x in self.session.query(PricingStrategy).all():
            self.pricing_combo.addItem(f"{x.name} – {x.description}", x.id)
        self.pricing_combo.blockSignals(False)

    def _refresh_system_lookups(self):
        """Update Employee Role, Stack Category, Infra Category, and Billing Type combos from SystemLookup."""
        def populate(combo, category_name):
            combo.blockSignals(True)
            current = combo.currentText()
            combo.clear()
            items = self.session.query(SystemLookup).filter_by(category=category_name).all()
            for x in items:
                combo.addItem(x.value)
            # Try to preserve previous selection if it still exists
            idx = combo.findText(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.blockSignals(False)

        populate(self.emp_role, "role")
        populate(self.stack_cat, "stack_category")
        populate(self.infra_cat, "infra_category")
        populate(self.stack_bill, "billing_type")
        populate(self.infra_bill, "billing_type")

    # ═══════════════ STACK CRUD ═══════════════
    def _add_stack(self):
        n = self.stack_name.text().strip()
        if not n: QMessageBox.warning(self,"Validation","Name required."); return
        sc = StackCost(name=n, category=self.stack_cat.currentText(), cost=self.stack_cost.value(), billing_type=self.stack_bill.currentText())
        self.session.add(sc); self.session.commit()
        self._refresh_stack_table(); self.stack_name.clear(); self.stack_cost.setValue(0)

    def _del_stack(self):
        r = self.stack_table.currentRow()
        if r < 0: return
        sc = self.session.query(StackCost).get(int(self.stack_table.item(r,0).text()))
        if sc: self.session.delete(sc); self.session.commit(); self._refresh_stack_table()

    def _refresh_stack_table(self):
        items = self.session.query(StackCost).all()
        self.stack_table.setRowCount(len(items))
        for i,s in enumerate(items):
            for j,v in enumerate([str(s.id),s.name,format_inr(s.cost),s.billing_type]):
                self.stack_table.setItem(i,j,QTableWidgetItem(v))
        self.stack_table.resizeColumnsToContents()

    # ═══════════════ INFRA CRUD ═══════════════
    def _add_infra(self):
        n = self.infra_name.text().strip()
        if not n: QMessageBox.warning(self,"Validation","Name required."); return
        ic = InfraCost(name=n, category=self.infra_cat.currentText(), cost=self.infra_cost_in.value(), billing_type=self.infra_bill.currentText())
        self.session.add(ic); self.session.commit()
        self._refresh_infra_table(); self.infra_name.clear(); self.infra_cost_in.setValue(0)

    def _del_infra(self):
        r = self.infra_table.currentRow()
        if r < 0: return
        ic = self.session.query(InfraCost).get(int(self.infra_table.item(r,0).text()))
        if ic: self.session.delete(ic); self.session.commit(); self._refresh_infra_table()

    def _refresh_infra_table(self):
        items = self.session.query(InfraCost).all()
        self.infra_table.setRowCount(len(items))
        for i,item in enumerate(items):
            for j,v in enumerate([str(item.id),item.name,format_inr(item.cost),item.billing_type]):
                self.infra_table.setItem(i,j,QTableWidgetItem(v))
        self.infra_table.resizeColumnsToContents()

    # ═══════════════ MODULES ═══════════════
    def _add_mod(self):
        n = self.mod_name.text().strip()
        if not n: QMessageBox.warning(self,"Validation","Module name required."); return
        row = self.mod_table.rowCount(); self.mod_table.insertRow(row)
        self.mod_table.setItem(row,0,QTableWidgetItem(n))
        it = QTableWidgetItem(self.mod_emp.currentText())
        it.setData(Qt.ItemDataRole.UserRole, self.mod_emp.currentData())
        self.mod_table.setItem(row,1,it)
        self.mod_table.setItem(row,2,QTableWidgetItem(str(self.mod_hrs.value())))
        rb = QPushButton("X"); rb.setProperty("cssClass","danger")
        rb.clicked.connect(lambda _,r=row: self.mod_table.removeRow(r))
        self.mod_table.setCellWidget(row,3,rb)
        self.mod_name.clear(); self.mod_hrs.setValue(0)

    # ═══════════════ PRESETS ═══════════════
    def _apply_preset(self):
        pid = self.preset_combo.currentData()
        if not pid: return
        preset = self.session.query(IndustryPreset).get(pid)
        if not preset: return
        # By default we don't have app type / complexity stored in the preset model anymore!
        # Wait, didn't I just say "groups of predefined modules"? Yes.
        # But wait, old INDUSTRY_PRESETS had "app_type" and "complexity".
        # Let me just set the modules and skip app_type/complexity for now.
        
        self.mod_table.setRowCount(0)
        for m in preset.modules:
            row = self.mod_table.rowCount(); self.mod_table.insertRow(row)
            self.mod_table.setItem(row,0,QTableWidgetItem(m.name))
            it = QTableWidgetItem(self.mod_emp.currentText() if self.mod_emp.count() > 0 else "N/A")
            it.setData(Qt.ItemDataRole.UserRole, self.mod_emp.currentData() if self.mod_emp.count() > 0 else None)
            self.mod_table.setItem(row,1,it)
            self.mod_table.setItem(row,2,QTableWidgetItem(str(float(m.default_hours))))
            rb = QPushButton("X"); rb.setProperty("cssClass","danger")
            rb.clicked.connect(lambda _,r=row: self.mod_table.removeRow(r))
            self.mod_table.setCellWidget(row,3,rb)
        self.statusBar().showMessage(f"Preset '{preset.name}' applied.",3000)

    def _apply_pricing_mode(self):
        pid = self.pricing_combo.currentData()
        if not pid: return
        pm = self.session.query(PricingStrategy).get(pid)
        if not pm: return
        self.est_mb.setValue(pm.risk_contingency_pct) # Actually, the model has profit_margin_pct and risk_contingency_pct. In logic PRICING_MODES, it was also maintenance_buffer_pct. Let's just set risk and profit, and leave maintainance buffer alone. Or set maintenance_buffer to risk too.
        # Looking at PRICING_MODES logic, there was maintenance_buffer_pct, risk_pct, profit_pct. The model doesn't have maintenance buffer explicitly, let's just keep old behaviour or use risk.
        self.est_mb.setValue(pm.risk_contingency_pct)
        self.est_rk.setValue(pm.risk_contingency_pct)
        self.est_pf.setValue(pm.profit_margin_pct)

    # ═══════════════ ESTIMATION ═══════════════
    def _run_estimation(self):
        if self.mod_table.rowCount() == 0:
            QMessageBox.warning(self,"No Modules","Add at least one module."); return
        modules = []
        for row in range(self.mod_table.rowCount()):
            mod = ProjectModule(name=self.mod_table.item(row,0).text(),
                estimated_hours=float(self.mod_table.item(row,2).text()))
            eid = self.mod_table.item(row,1).data(Qt.ItemDataRole.UserRole)
            if eid: mod.employee = self.session.query(Employee).get(eid)
            modules.append(mod)
        rid = self.est_region.currentData()
        reg = self.session.query(RegionMultiplier).get(rid) if rid else None
        rm = reg.multiplier if reg else 1.0
        result = run_full_estimation(
            session=self.session,
            modules=modules, complexity=self.est_cx.currentText(),
            app_type=self.est_app.currentText(), region_multiplier=rm,
            infra_items=self.session.query(InfraCost).all(),
            stack_items=self.session.query(StackCost).all(),
            maintenance_buffer_pct=self.est_mb.value(),
            risk_contingency_pct=self.est_rk.value(),
            profit_margin_pct=self.est_pf.value(),
            function_points=self.est_fp.value(),
            estimated_duration_months=self.est_dur.value())
        self._estimation_result = result
        self._show_estimation(result)

    def _show_estimation(self, r):
        t = self._theme
        self._upd_card(self.c_gross,"Gross Cost",format_inr(r["gross_cost"]))
        self._upd_card(self.c_safe,"Safe Cost",format_inr(r["risk_buffer"]["safe_cost"]))
        self._upd_card(self.c_final,"Final Price",format_inr(r["final_pricing"]["final_price"]))
        self._upd_card(self.c_margin,"Revenue Margin",f"{r['analytics']['revenue_margin_pct']}%")

        # Clear old charts
        while self.est_chart_holder.count():
            w = self.est_chart_holder.takeAt(0).widget()
            if w: w.deleteLater()

        # Stage pie chart
        ch = QHBoxLayout()
        pie = create_stage_pie_chart(r["stage_distribution"], t)
        mod_bar = create_module_cost_bar_chart(r["labor"]["module_costs"], t)
        cw = QWidget(); cwl = QHBoxLayout(cw); cwl.addWidget(pie); cwl.addWidget(mod_bar)
        self.est_chart_holder.addWidget(cw)

        # Text report
        L = []
        L.append("=" * 50)
        L.append("  ESTIMATION BREAKDOWN")
        L.append("=" * 50)
        L.append("")
        L.append("--- LABOR ---")
        for mc in r["labor"]["module_costs"]:
            L.append(f"  {mc['name']:28s} {mc['hours']:7.1f}h  {format_inr(mc['cost']):>13s}")
        L.append(f"  Complexity: x{r['labor']['complexity_multiplier']}  |  App-Type: x{r['labor']['app_type_adjustment']}")
        L.append(f"  ADJUSTED LABOR: {format_inr(r['labor']['adjusted_labor_total']):>13s}")
        L.append("")
        L.append("--- COST SUMMARY ---")
        L.append(f"  Gross:       {format_inr(r['gross_cost']):>13s}")
        L.append(f"  Maint Buf:   {format_inr(r['risk_buffer']['maintenance_buffer']):>13s}")
        L.append(f"  Risk:        {format_inr(r['risk_buffer']['risk_contingency']):>13s}")
        L.append(f"  Safe Cost:   {format_inr(r['risk_buffer']['safe_cost']):>13s}")
        L.append(f"  Profit:      {format_inr(r['final_pricing']['profit_amount']):>13s}")
        L.append(f"  FINAL PRICE: {format_inr(r['final_pricing']['final_price']):>13s}")
        L.append("")
        L.append("--- ANALYTICS ---")
        a = r["analytics"]
        L.append(f"  Hours: {a['total_hours']:.0f}  |  Person-Months: {a['person_months']:.1f}")
        L.append(f"  Burn Rate/mo: {format_inr(a['burn_rate_monthly'])}  |  Margin: {a['revenue_margin_pct']}%")
        L.append("")
        L.append("--- MAINTENANCE ---")
        for mf in r["maintenance_forecast"]:
            L.append(f"  Year {mf['year']}: {format_inr(mf['annual_cost'])}  (Cumul: {format_inr(mf['cumulative_cost'])})")
        self.results_text.setPlainText("\n".join(L))

    def _upd_card(self, card, title, value):
        labels = card.findChildren(QLabel)
        if len(labels) >= 2: labels[0].setText(value); labels[1].setText(title)

    # ═══════════════ SAVE ═══════════════
    def _save_estimation(self):
        if not self._estimation_result:
            QMessageBox.warning(self,"Error","Run estimation first."); return
        pn = self.est_name.text().strip()
        if not pn: QMessageBox.warning(self,"Error","Project name required."); return
        r = self._estimation_result
        p = Project(name=pn, client_name=self.est_client.text().strip(),
            description=self.est_desc.toPlainText().strip(),
            app_type=self.est_app.currentText(), complexity=self.est_cx.currentText(),
            function_points=self.est_fp.value(), region_id=self.est_region.currentData(),
            maintenance_buffer_pct=self.est_mb.value(), risk_contingency_pct=self.est_rk.value(),
            profit_margin_pct=self.est_pf.value(), estimated_duration_months=self.est_dur.value(),
            status="active")
        self.session.add(p); self.session.flush()
        for row in range(self.mod_table.rowCount()):
            mod = ProjectModule(project_id=p.id, name=self.mod_table.item(row,0).text(),
                estimated_hours=float(self.mod_table.item(row,2).text()),
                employee_id=self.mod_table.item(row,1).data(Qt.ItemDataRole.UserRole))
            for mc in r["labor"]["module_costs"]:
                if mc["name"] == mod.name: mod.cost = mc["cost"]; break
            self.session.add(mod)
        est = Estimate(project_id=p.id, total_labor_cost=r["labor"]["adjusted_labor_total"],
            total_infra_cost=r["infra_stack"]["infra_total"], total_stack_cost=r["infra_stack"]["stack_total"],
            gross_cost=r["gross_cost"], maintenance_buffer=r["risk_buffer"]["maintenance_buffer"],
            risk_contingency=r["risk_buffer"]["risk_contingency"], safe_cost=r["risk_buffer"]["safe_cost"],
            profit_amount=r["final_pricing"]["profit_amount"], final_price=r["final_pricing"]["final_price"],
            cost_per_function_point=r["analytics"]["cost_per_function_point"],
            burn_rate_monthly=r["analytics"]["burn_rate_monthly"])
        self.session.add(est)
        for mf in r["maintenance_forecast"]:
            self.session.add(MaintenanceRecord(project_id=p.id, year=mf["year"], annual_cost=mf["annual_cost"]))
        self.session.commit()
        create_audit_entry(self.session,"projects",p.id,"CREATE")
        self._refresh_proj_combos()
        QMessageBox.information(self,"Saved",f"Project '{pn}' saved!")

    # ═══════════════ ANALYSIS ═══════════════
    def _refresh_proj_combos(self):
        for cb in [self.an_proj, self.prop_proj]:
            cb.clear()
            for p in self.session.query(Project).all():
                cb.addItem(f"{p.name} ({p.client_name})", p.id)

    def _load_analysis(self):
        pid = self.an_proj.currentData()
        if not pid: return
        p = self.session.query(Project).get(pid)
        est = p.estimate; act = p.actual; t = self._theme

        # Clear old charts
        while self.an_charts.count():
            w = self.an_charts.takeAt(0).widget()
            if w: w.deleteLater()

        if est:
            self._upd_card(self.an_c_est,"Estimated",format_inr(est.final_price))

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
                fc = [{"year": m.year, "annual_cost": m.annual_cost,
                       "cumulative_cost": m.annual_cost * m.year} for m in sorted(maint, key=lambda x: x.year)]
                self.an_charts.addWidget(create_maintenance_line_chart(fc, t))

        if act:
            self._upd_card(self.an_c_act,"Actual",format_inr(act.actual_cost))
            if est:
                v = calculate_variance(est.final_price, act.actual_cost)
                self._upd_card(self.an_c_var,"Variance",f"{v['variance_pct']}%")
                self._upd_card(self.an_c_cls,"Classification",v["classification"])
                self.an_charts.addWidget(create_variance_bar_chart(est.final_price, act.actual_cost, t))
        else:
            self._upd_card(self.an_c_act,"Actual","--")
            self._upd_card(self.an_c_var,"Variance","--")
            self._upd_card(self.an_c_cls,"Classification","--")

        # Text
        L = []
        if est:
            L.append(f"Project: {p.name}")
            L.append(f"Labor: {format_inr(est.total_labor_cost)}  |  Infra: {format_inr(est.total_infra_cost)}  |  Stack: {format_inr(est.total_stack_cost)}")
            L.append(f"Gross: {format_inr(est.gross_cost)}  |  Safe: {format_inr(est.safe_cost)}  |  Final: {format_inr(est.final_price)}")
            L.append(f"Burn Rate/mo: {format_inr(est.burn_rate_monthly)}")
        if p.modules:
            L.append("\nModules:")
            for m in p.modules:
                en = m.employee.name if m.employee else "N/A"
                L.append(f"  {m.name:28s} {m.estimated_hours:7.1f}h  {format_inr(m.cost):>13s}  ({en})")
        self.an_text.setPlainText("\n".join(L))

    def _save_actual(self):
        pid = self.an_proj.currentData()
        if not pid: return
        cost = self.actual_in.value()
        p = self.session.query(Project).get(pid)
        if p.actual:
            old = p.actual.actual_cost; p.actual.actual_cost = cost
            create_audit_entry(self.session,"actuals",p.actual.id,"UPDATE","actual_cost",str(old),str(cost))
        else:
            a = Actual(project_id=pid, actual_cost=cost)
            self.session.add(a); self.session.flush()
            create_audit_entry(self.session,"actuals",a.id,"CREATE")
        self.session.commit(); self._load_analysis()
        QMessageBox.information(self,"Saved","Actual cost saved.")

    # ═══════════════ PROPOSAL ═══════════════
    def _preview_prop(self):
        pid = self.prop_proj.currentData()
        if not pid: return
        p = self.session.query(Project).get(pid); est = p.estimate
        L = [f"PROJECT: {p.name}", f"CLIENT: {p.client_name}", f"TYPE: {p.app_type}",
             f"COMPLEXITY: {p.complexity}", f"TIMELINE: {p.estimated_duration_months} months",""]
        if est: L.append(f"TOTAL INVESTMENT: {format_inr(est.final_price)}")
        L.append("\nMODULES:")
        for m in p.modules: L.append(f"  - {m.name}")
        L.append(f"\nPAYMENT TERMS: {self.prop_terms.toPlainText()}")
        self.prop_preview.setPlainText("\n".join(L))

    def _export_pdf(self):
        pid = self.prop_proj.currentData()
        if not pid: QMessageBox.warning(self,"Error","Select a project."); return
        p = self.session.query(Project).get(pid)
        if not p.estimate: QMessageBox.warning(self,"Error","No estimation for project."); return
        fp, _ = QFileDialog.getSaveFileName(self,"Save PDF",f"{p.name}_Proposal.pdf","PDF (*.pdf)")
        if not fp: return
        est = p.estimate; maint = p.maintenance_records
        sd = {s: est.gross_cost * getattr(p, f"stage_{s.lower()}_pct") / 100
              for s in ["Planning","Design","Development","Testing","Deployment"]}
        generate_proposal_pdf(filepath=fp, project_name=p.name, client_name=p.client_name,
            app_type=p.app_type, complexity=p.complexity, description=p.description,
            timeline_months=p.estimated_duration_months, scope_modules=[m.name for m in p.modules],
            final_price=est.final_price, stage_distribution=sd,
            maintenance_annual=maint[0].annual_cost if maint else 0,
            maintenance_years=self.prop_yrs.value(),
            payment_terms=self.prop_terms.toPlainText(),
            include_maintenance=self.prop_maint.currentText() == "Yes")
        QMessageBox.information(self,"Exported",f"PDF saved:\n{fp}")

    # ═══════════════ REFRESH ═══════════════
    def _refresh_all(self):
        self._refresh_emp_table()
        self._refresh_stack_table()
        self._refresh_infra_table()
        self._refresh_system_lookups()
        self._refresh_proj_combos()
