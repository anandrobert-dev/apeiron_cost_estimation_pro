"""Estimation Tab – Project estimation workflow"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QSplitter,
    QScrollArea,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QLabel,
)
from PyQt6.QtCore import Qt

from app.persistence.models import (
    RegionMultiplier,
    Employee,
    InfraCost,
    StackCost,
    Project,
    ProjectModule,
    Estimate,
    MaintenanceRecord,
    AppTypeMultiplier,
    ComplexityMultiplier,
    PricingStrategy,
    IndustryPreset,
)
from app.utils.formatting import format_inr
from app.ui.components.helpers import card, section_label
from app.ui.components.charts import (
    create_stage_pie_chart,
    create_module_cost_bar_chart,
)


class EstimationTab(QWidget):
    """Tab for running and managing project estimations."""

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.session = main_window.session
        self.audit_repo = main_window.audit_repo
        self.estimation_service = main_window.estimation_service
        self._estimation_result = None
        self._build_ui()

    def _build_ui(self):
        """Build estimation tab with left input panel and right results panel."""
        sp = QSplitter(Qt.Orientation.Horizontal)

        # LEFT PANEL - Inputs
        left = QScrollArea()
        left.setWidgetResizable(True)
        lw = QWidget()
        ll = QVBoxLayout(lw)

        # Project details
        pg = QGroupBox("Project Details")
        pgl = QFormLayout(pg)
        self.est_name = QLineEdit()
        self.est_name.setPlaceholderText("Project Name")
        self.est_client = QLineEdit()
        self.est_client.setPlaceholderText("Client Name")
        self.est_desc = QTextEdit()
        self.est_desc.setPlaceholderText("Description...")
        self.est_desc.setMaximumHeight(70)
        self.est_app = QComboBox()
        self.est_cx = QComboBox()
        self.est_region = QComboBox()

        for r in self.session.query(RegionMultiplier).all():
            self.est_region.addItem(f"{r.region_name} (x{r.multiplier})", r.id)

        self.est_fp = QSpinBox()
        self.est_fp.setRange(0, 100_000)
        self.est_fp.setSpecialValueText("N/A")
        self.est_dur = QDoubleSpinBox()
        self.est_dur.setRange(0.5, 120)
        self.est_dur.setValue(6)
        self.est_dur.setSuffix(" months")

        pgl.addRow("Project:", self.est_name)
        pgl.addRow("Client:", self.est_client)
        pgl.addRow("Description:", self.est_desc)
        pgl.addRow("App Type:", self.est_app)
        pgl.addRow("Complexity:", self.est_cx)
        pgl.addRow("Region:", self.est_region)
        pgl.addRow("Function Points:", self.est_fp)
        pgl.addRow("Duration:", self.est_dur)
        ll.addWidget(pg)

        # Industry Preset
        ipg = QGroupBox("Industry Preset")
        ipl = QHBoxLayout(ipg)
        self.preset_combo = QComboBox()
        apply_preset_btn = QPushButton("Apply Preset")
        apply_preset_btn.setProperty("cssClass", "warning")
        apply_preset_btn.clicked.connect(self._apply_preset)
        ipl.addWidget(self.preset_combo, 1)
        ipl.addWidget(apply_preset_btn)
        ll.addWidget(ipg)

        # Pricing Strategy
        psg = QGroupBox("Pricing Strategy")
        psgl = QHBoxLayout(psg)
        self.pricing_combo = QComboBox()
        self.pricing_combo.currentIndexChanged.connect(self._apply_pricing_mode)
        psgl.addWidget(self.pricing_combo, 1)
        ll.addWidget(psg)

        self._refresh_estimation_combos()

        # Module Hours
        mg = QGroupBox("Module Hours")
        mgl = QVBoxLayout(mg)
        mir = QHBoxLayout()
        self.mod_name = QLineEdit()
        self.mod_name.setPlaceholderText("Module Name")
        self.mod_emp = QComboBox()
        self.mod_hrs = QDoubleSpinBox()
        self.mod_hrs.setRange(0, 100_000)
        self.mod_hrs.setSuffix(" hrs")
        amb = QPushButton("Add")
        amb.clicked.connect(self._add_mod)
        mir.addWidget(self.mod_name, 3)
        mir.addWidget(self.mod_emp, 2)
        mir.addWidget(self.mod_hrs, 1)
        mir.addWidget(amb, 1)
        mgl.addLayout(mir)

        self.mod_table = QTableWidget()
        self.mod_table.setColumnCount(4)
        self.mod_table.setHorizontalHeaderLabels(
            ["Module", "Employee", "Hours", "Remove"]
        )
        self.mod_table.horizontalHeader().setStretchLastSection(False)
        self.mod_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.mod_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.mod_table.setMinimumHeight(180)
        mgl.addWidget(self.mod_table)
        ll.addWidget(mg)

        # Risk & Profit
        rg = QGroupBox("Risk and Margin")
        rgl = QFormLayout(rg)
        self.est_mb = QDoubleSpinBox()
        self.est_mb.setRange(0, 50)
        self.est_mb.setValue(15)
        self.est_mb.setSuffix(" %")
        self.est_rk = QDoubleSpinBox()
        self.est_rk.setRange(0, 50)
        self.est_rk.setValue(10)
        self.est_rk.setSuffix(" %")
        self.est_pf = QDoubleSpinBox()
        self.est_pf.setRange(0, 100)
        self.est_pf.setValue(20)
        self.est_pf.setSuffix(" %")
        rgl.addRow("Maintenance Buffer:", self.est_mb)
        rgl.addRow("Risk Contingency:", self.est_rk)
        rgl.addRow("Profit Margin:", self.est_pf)
        ll.addWidget(rg)

        # Calculate button
        t = self.main._theme
        cb = QPushButton("Calculate Estimation")
        cb.setStyleSheet(
            f"padding:12px;font-size:14px;background-color:{t['success']};"
        )
        cb.clicked.connect(self._run_estimation)
        ll.addWidget(cb)

        # Save button
        sb = QPushButton("Save Estimation")
        sb.setStyleSheet(
            f"padding:12px;font-size:14px;background-color:{t['warning']};"
        )
        sb.clicked.connect(self._save_estimation)
        ll.addWidget(sb)

        ll.addStretch()
        left.setWidget(lw)
        sp.addWidget(left)

        # RIGHT PANEL - Results
        right = QScrollArea()
        right.setWidgetResizable(True)
        rw = QWidget()
        self.est_right_layout = QVBoxLayout(rw)
        self.est_right_layout.addWidget(
            section_label("Live Estimation Results", self.main._theme)
        )

        cl = QHBoxLayout()
        self.c_gross = card("Gross Cost", "₹0", t["success"], t)
        self.c_safe = card("Safe Cost", "₹0", t["warning"], t)
        self.c_final = card("Final Price", "₹0", t["accent"], t)
        self.c_margin = card("Revenue Margin", "0%", t["success"], t)
        cl.addWidget(self.c_gross)
        cl.addWidget(self.c_safe)
        cl.addWidget(self.c_final)
        cl.addWidget(self.c_margin)
        self.est_right_layout.addLayout(cl)

        self.est_chart_holder = QVBoxLayout()
        self.est_right_layout.addLayout(self.est_chart_holder)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.est_right_layout.addWidget(self.results_text)
        self.est_right_layout.addStretch()

        right.setWidget(rw)
        sp.addWidget(right)
        sp.setSizes([480, 600])

        QVBoxLayout(self).addWidget(sp)

    def _refresh_estimation_combos(self):
        """Load app types, complexity, presets, and pricing strategies."""
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

    def _add_mod(self):
        """Add a module to the estimation."""
        n = self.mod_name.text().strip()
        if not n:
            QMessageBox.warning(self, "Validation", "Module name required.")
            return

        row = self.mod_table.rowCount()
        self.mod_table.insertRow(row)
        self.mod_table.setItem(row, 0, QTableWidgetItem(n))

        it = QTableWidgetItem(self.mod_emp.currentText())
        it.setData(Qt.ItemDataRole.UserRole, self.mod_emp.currentData())
        self.mod_table.setItem(row, 1, it)
        self.mod_table.setItem(row, 2, QTableWidgetItem(str(self.mod_hrs.value())))

        rb = QPushButton("X")
        rb.setProperty("cssClass", "danger")
        rb.clicked.connect(lambda _, r=row: self.mod_table.removeRow(r))
        self.mod_table.setCellWidget(row, 3, rb)
        self.mod_table.resizeRowsToContents()

        self.mod_name.clear()
        self.mod_hrs.setValue(0)

    def _apply_preset(self):
        """Load modules from selected industry preset."""
        pid = self.preset_combo.currentData()
        if not pid:
            return

        preset = self.session.query(IndustryPreset).get(pid)
        if not preset:
            return

        self.mod_table.setRowCount(0)
        for m in preset.modules:
            row = self.mod_table.rowCount()
            self.mod_table.insertRow(row)
            self.mod_table.setItem(row, 0, QTableWidgetItem(m.name))

            it = QTableWidgetItem(
                self.mod_emp.currentText() if self.mod_emp.count() > 0 else "N/A"
            )
            it.setData(
                Qt.ItemDataRole.UserRole,
                self.mod_emp.currentData() if self.mod_emp.count() > 0 else None,
            )
            self.mod_table.setItem(row, 1, it)
            self.mod_table.setItem(
                row, 2, QTableWidgetItem(str(float(m.default_hours)))
            )

            rb = QPushButton("X")
            rb.setProperty("cssClass", "danger")
            rb.clicked.connect(lambda _, r=row: self.mod_table.removeRow(r))
            self.mod_table.setCellWidget(row, 3, rb)

        self.mod_table.resizeRowsToContents()
        self.main.statusBar().showMessage(f"Preset '{preset.name}' applied.", 3000)

    def _apply_pricing_mode(self):
        """Apply pricing strategy values to form."""
        pid = self.pricing_combo.currentData()
        if not pid:
            return

        pm = self.session.query(PricingStrategy).get(pid)
        if not pm:
            return

        self.est_mb.setValue(pm.risk_contingency_pct)
        self.est_rk.setValue(pm.risk_contingency_pct)
        self.est_pf.setValue(pm.profit_margin_pct)

    def _run_estimation(self):
        """Run the estimation with current inputs."""
        if self.mod_table.rowCount() == 0:
            QMessageBox.warning(self, "No Modules", "Add at least one module.")
            return

        # Gather module data
        module_dicts = []
        for row in range(self.mod_table.rowCount()):
            name = self.mod_table.item(row, 0).text()
            estimated_hours = float(self.mod_table.item(row, 2).text())
            eid = self.mod_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            emp = self.session.query(Employee).get(eid) if eid else None
            hourly_rate = float(emp.hourly_cost) if emp else 0.0
            module_dicts.append(
                {
                    "name": name,
                    "hourly_rate": hourly_rate,
                    "estimated_hours": estimated_hours,
                }
            )

        # Get region multiplier
        rid = self.est_region.currentData()
        reg = self.session.query(RegionMultiplier).get(rid) if rid else None
        rm = float(reg.multiplier) if reg else 1.0

        # Get costs
        infra_costs = [float(i.cost) for i in self.session.query(InfraCost).all()]
        stack_costs = [float(s.cost) for s in self.session.query(StackCost).all()]

        # Run estimation
        result = self.estimation_service.run_estimation(
            modules=module_dicts,
            complexity=self.est_cx.currentText(),
            app_type=self.est_app.currentText(),
            region_multiplier=rm,
            infra_costs=infra_costs,
            stack_costs=stack_costs,
            maintenance_buffer_pct=self.est_mb.value(),
            risk_contingency_pct=self.est_rk.value(),
            profit_margin_pct=self.est_pf.value(),
            function_points=self.est_fp.value(),
            estimated_duration_months=self.est_dur.value(),
        )

        self._estimation_result = result
        self._show_estimation(result)

    def _show_estimation(self, r):
        """Display estimation results in cards and charts."""
        t = self.main._theme
        self._upd_card(self.c_gross, "Gross Cost", format_inr(r["gross_cost"]))
        self._upd_card(
            self.c_safe, "Safe Cost", format_inr(r["risk_buffer"]["safe_cost"])
        )
        self._upd_card(
            self.c_final, "Final Price", format_inr(r["final_pricing"]["final_price"])
        )
        self._upd_card(
            self.c_margin, "Revenue Margin", f"{r['analytics']['revenue_margin_pct']}%"
        )

        # Clear old charts
        while self.est_chart_holder.count():
            w = self.est_chart_holder.takeAt(0).widget()
            if w:
                w.deleteLater()

        # Create charts
        ch = QHBoxLayout()
        pie = create_stage_pie_chart(r["stage_distribution"], t)
        mod_bar = create_module_cost_bar_chart(r["labor"]["module_costs"], t)
        cw = QWidget()
        cwl = QHBoxLayout(cw)
        cwl.addWidget(pie)
        cwl.addWidget(mod_bar)
        self.est_chart_holder.addWidget(cw)

        # Text report
        L = []
        L.append("=" * 50)
        L.append("  ESTIMATION BREAKDOWN")
        L.append("=" * 50)
        L.append("")
        L.append("--- LABOR ---")
        for mc in r["labor"]["module_costs"]:
            L.append(
                f"  {mc['name']:28s} {mc['hours']:7.1f}h  "
                f"{format_inr(mc['cost']):>13s}"
            )
        L.append(
            f"  Complexity: x{r['labor']['complexity_multiplier']}  |  "
            f"App-Type: x{r['labor']['app_type_adjustment']}"
        )
        L.append(
            f"  ADJUSTED LABOR: {format_inr(r['labor']['adjusted_labor_total']):>13s}"
        )
        L.append("")
        L.append("--- COST SUMMARY ---")
        L.append(f"  Gross:       {format_inr(r['gross_cost']):>13s}")
        L.append(
            f"  Maint Buf:   {format_inr(r['risk_buffer']['maintenance_buffer']):>13s}"
        )
        L.append(
            f"  Risk:        {format_inr(r['risk_buffer']['risk_contingency']):>13s}"
        )
        L.append(f"  Safe Cost:   {format_inr(r['risk_buffer']['safe_cost']):>13s}")
        L.append(
            f"  Profit:      {format_inr(r['final_pricing']['profit_amount']):>13s}"
        )
        L.append(f"  FINAL PRICE: {format_inr(r['final_pricing']['final_price']):>13s}")
        L.append("")
        L.append("--- ANALYTICS ---")
        a = r["analytics"]
        L.append(
            f"  Hours: {a['total_hours']:.0f}  |  Person-Months: {a['person_months']:.1f}"
        )
        L.append(
            f"  Burn Rate/mo: {format_inr(a['burn_rate_monthly'])}  |  Margin: {a['revenue_margin_pct']}%"
        )
        L.append("")
        L.append("--- MAINTENANCE ---")
        for mf in r["maintenance_forecast"]:
            L.append(
                f"  Year {mf['year']}: {format_inr(mf['annual_cost'])}  "
                f"(Cumul: {format_inr(mf['cumulative_cost'])})"
            )
        self.results_text.setPlainText("\n".join(L))

    def _upd_card(self, card_widget, title, value):
        """Update card widget value and title."""
        labels = card_widget.findChildren(QLabel)
        if len(labels) >= 2:
            labels[0].setText(value)
            labels[1].setText(title)

    def _save_estimation(self):
        """Save estimation as a project."""
        if not self._estimation_result:
            QMessageBox.warning(self, "Error", "Run estimation first.")
            return

        pn = self.est_name.text().strip()
        if not pn:
            QMessageBox.warning(self, "Error", "Project name required.")
            return

        r = self._estimation_result
        p = Project(
            name=pn,
            client_name=self.est_client.text().strip(),
            description=self.est_desc.toPlainText().strip(),
            app_type=self.est_app.currentText(),
            complexity=self.est_cx.currentText(),
            function_points=self.est_fp.value(),
            region_id=self.est_region.currentData(),
            maintenance_buffer_pct=self.est_mb.value(),
            risk_contingency_pct=self.est_rk.value(),
            profit_margin_pct=self.est_pf.value(),
            estimated_duration_months=self.est_dur.value(),
            status="active",
        )
        self.session.add(p)
        self.session.flush()

        # Save modules
        for row in range(self.mod_table.rowCount()):
            mod = ProjectModule(
                project_id=p.id,
                name=self.mod_table.item(row, 0).text(),
                estimated_hours=float(self.mod_table.item(row, 2).text()),
                employee_id=self.mod_table.item(row, 1).data(Qt.ItemDataRole.UserRole),
            )
            for mc in r["labor"]["module_costs"]:
                if mc["name"] == mod.name:
                    mod.cost = mc["cost"]
                    break
            self.session.add(mod)

        # Save estimate
        est = Estimate(
            project_id=p.id,
            total_labor_cost=r["labor"]["adjusted_labor_total"],
            total_infra_cost=r["infra_stack"]["infra_total"],
            total_stack_cost=r["infra_stack"]["stack_total"],
            gross_cost=r["gross_cost"],
            maintenance_buffer=r["risk_buffer"]["maintenance_buffer"],
            risk_contingency=r["risk_buffer"]["risk_contingency"],
            safe_cost=r["risk_buffer"]["safe_cost"],
            profit_amount=r["final_pricing"]["profit_amount"],
            final_price=r["final_pricing"]["final_price"],
            cost_per_function_point=r["analytics"]["cost_per_function_point"],
            burn_rate_monthly=r["analytics"]["burn_rate_monthly"],
        )
        self.session.add(est)

        # Save maintenance forecast
        for mf in r["maintenance_forecast"]:
            self.session.add(
                MaintenanceRecord(
                    project_id=p.id, year=mf["year"], annual_cost=mf["annual_cost"]
                )
            )

        self.session.commit()
        self.audit_repo.log("projects", p.id, "CREATE")
        self.main._refresh_proj_combos()
        QMessageBox.information(self, "Saved", f"Project '{pn}' saved!")
