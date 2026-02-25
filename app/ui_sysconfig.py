from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QScrollArea, QGroupBox, QLineEdit, QComboBox, 
    QDoubleSpinBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt

from app.models import (
    SystemLookup, AppTypeMultiplier, ComplexityMultiplier, PricingStrategy, IndustryPreset
)

class SysConfigTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.session = main_window.session
        self._build_ui()
        self._refresh_all_tables()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        sw = QWidget()
        sl = QVBoxLayout(sw)

        # 1. Lookups (Roles, Categories)
        lg = QGroupBox("Dynamic Lookups (Roles, Categories)")
        lgl = QFormLayout(lg)
        self.lookup_cat = QComboBox()
        self.lookup_cat.addItems(["role", "infra_category", "stack_category", "billing_type"])
        self.lookup_val = QLineEdit()
        l_btn = QPushButton("Add Lookup")
        l_btn.clicked.connect(self._add_sys_lookup)
        lgl.addRow("Category:", self.lookup_cat)
        lgl.addRow("Value:", self.lookup_val)
        lgl.addRow("", l_btn)
        
        self.lookup_table = QTableWidget(); self.lookup_table.setColumnCount(3)
        self.lookup_table.setHorizontalHeaderLabels(["ID", "Category", "Value"])
        self.lookup_table.horizontalHeader().setStretchLastSection(True)
        self.lookup_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        ld_btn = QPushButton("Delete Selected"); ld_btn.setProperty("cssClass", "danger"); ld_btn.clicked.connect(self._del_sys_lookup)
        lgl.addRow(self.lookup_table)
        lgl.addRow("", ld_btn)
        sl.addWidget(lg)

        # 2. App Type
        ag = QGroupBox("App Type Multipliers")
        agl = QFormLayout(ag)
        self.app_name = QLineEdit()
        self.app_mult = QDoubleSpinBox(); self.app_mult.setRange(0.1, 10.0); self.app_mult.setSingleStep(0.1)
        a_btn = QPushButton("Add App Type")
        a_btn.clicked.connect(self._add_app_type)
        agl.addRow("Name:", self.app_name)
        agl.addRow("Multiplier:", self.app_mult)
        agl.addRow("", a_btn)

        self.app_table = QTableWidget(); self.app_table.setColumnCount(3)
        self.app_table.setHorizontalHeaderLabels(["ID", "Name", "Multiplier"])
        self.app_table.horizontalHeader().setStretchLastSection(True)
        self.app_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        ad_btn = QPushButton("Delete Selected"); ad_btn.setProperty("cssClass", "danger"); ad_btn.clicked.connect(self._del_app_type)
        agl.addRow(self.app_table)
        agl.addRow("", ad_btn)
        sl.addWidget(ag)

        # 3. Complexity
        cg = QGroupBox("Complexity Multipliers")
        cgl = QFormLayout(cg)
        self.cx_name = QLineEdit()
        self.cx_mult = QDoubleSpinBox(); self.cx_mult.setRange(0.1, 10.0); self.cx_mult.setSingleStep(0.1)
        c_btn = QPushButton("Add Complexity")
        c_btn.clicked.connect(self._add_complexity)
        cgl.addRow("Name:", self.cx_name)
        cgl.addRow("Multiplier:", self.cx_mult)
        cgl.addRow("", c_btn)

        self.cx_table = QTableWidget(); self.cx_table.setColumnCount(3)
        self.cx_table.setHorizontalHeaderLabels(["ID", "Name", "Multiplier"])
        self.cx_table.horizontalHeader().setStretchLastSection(True)
        self.cx_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        cd_btn = QPushButton("Delete Selected"); cd_btn.setProperty("cssClass", "danger"); cd_btn.clicked.connect(self._del_complexity)
        cgl.addRow(self.cx_table)
        cgl.addRow("", cd_btn)
        sl.addWidget(cg)
        
        # 4. Pricing Strategies
        pg = QGroupBox("Pricing Strategies")
        pgl = QFormLayout(pg)
        self.ps_name = QLineEdit()
        self.ps_desc = QLineEdit()
        self.ps_prof = QDoubleSpinBox(); self.ps_prof.setRange(0, 100)
        self.ps_risk = QDoubleSpinBox(); self.ps_risk.setRange(0, 100)
        p_btn = QPushButton("Add Pricing Strategy")
        p_btn.clicked.connect(self._add_pricing)
        pgl.addRow("Name:", self.ps_name)
        pgl.addRow("Desc:", self.ps_desc)
        pgl.addRow("Profit %:", self.ps_prof)
        pgl.addRow("Risk %:", self.ps_risk)
        pgl.addRow("", p_btn)

        self.ps_table = QTableWidget(); self.ps_table.setColumnCount(5)
        self.ps_table.setHorizontalHeaderLabels(["ID", "Name", "Profit%", "Risk%", "Desc"])
        self.ps_table.horizontalHeader().setStretchLastSection(True)
        self.ps_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        pd_btn = QPushButton("Delete Selected"); pd_btn.setProperty("cssClass", "danger"); pd_btn.clicked.connect(self._del_pricing)
        pgl.addRow(self.ps_table)
        pgl.addRow("", pd_btn)
        sl.addWidget(pg)

        # 5. Industry Presets
        ipg = QGroupBox("Industry Presets (Blank Templates)")
        ipgl = QFormLayout(ipg)
        self.ip_name = QLineEdit()
        ip_btn = QPushButton("Add Blank Preset")
        ip_btn.clicked.connect(self._add_preset)
        ipgl.addRow("Name:", self.ip_name)
        ipgl.addRow("", ip_btn)

        self.ip_table = QTableWidget(); self.ip_table.setColumnCount(2)
        self.ip_table.setHorizontalHeaderLabels(["ID", "Name"])
        self.ip_table.horizontalHeader().setStretchLastSection(True)
        self.ip_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        ipd_btn = QPushButton("Delete Selected"); ipd_btn.setProperty("cssClass", "danger"); ipd_btn.clicked.connect(self._del_preset)
        ipgl.addRow(self.ip_table)
        ipgl.addRow("", ipd_btn)
        sl.addWidget(ipg)

        scroll.setWidget(sw)
        layout.addWidget(scroll)

    def _refresh_all_tables(self):
        self._refresh_lookup_table()
        self._refresh_app_table()
        self._refresh_cx_table()
        self._refresh_ps_table()
        self._refresh_ip_table()
        
    def _refresh_lookup_table(self):
        items = self.session.query(SystemLookup).all()
        self.lookup_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.lookup_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.lookup_table.setItem(i, 1, QTableWidgetItem(item.category))
            self.lookup_table.setItem(i, 2, QTableWidgetItem(item.value))
        self.lookup_table.resizeColumnsToContents()
        
    def _refresh_app_table(self):
        items = self.session.query(AppTypeMultiplier).all()
        self.app_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.app_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.app_table.setItem(i, 1, QTableWidgetItem(item.name))
            self.app_table.setItem(i, 2, QTableWidgetItem(str(item.multiplier)))
        self.app_table.resizeColumnsToContents()

    def _refresh_cx_table(self):
        items = self.session.query(ComplexityMultiplier).all()
        self.cx_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.cx_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.cx_table.setItem(i, 1, QTableWidgetItem(item.name))
            self.cx_table.setItem(i, 2, QTableWidgetItem(str(item.multiplier)))
        self.cx_table.resizeColumnsToContents()

    def _refresh_ps_table(self):
        items = self.session.query(PricingStrategy).all()
        self.ps_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.ps_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.ps_table.setItem(i, 1, QTableWidgetItem(item.name))
            self.ps_table.setItem(i, 2, QTableWidgetItem(str(item.profit_margin_pct)))
            self.ps_table.setItem(i, 3, QTableWidgetItem(str(item.risk_contingency_pct)))
            self.ps_table.setItem(i, 4, QTableWidgetItem(item.description))
        self.ps_table.resizeColumnsToContents()

    def _refresh_ip_table(self):
        items = self.session.query(IndustryPreset).all()
        self.ip_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.ip_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.ip_table.setItem(i, 1, QTableWidgetItem(item.name))
        self.ip_table.resizeColumnsToContents()

    # --- CRUD ACTIONS ---

    def _add_sys_lookup(self):
        val = self.lookup_val.text().strip()
        if not val:
            return
        cat = self.lookup_cat.currentText()
        item = SystemLookup(category=cat, value=val)
        self.session.add(item)
        self.session.commit()
        self.lookup_val.clear()
        self._refresh_lookup_table()
        self._sync_main_ui()

    def _del_sys_lookup(self):
        r = self.lookup_table.currentRow()
        if r < 0: return
        item_id = int(self.lookup_table.item(r, 0).text())
        item = self.session.query(SystemLookup).get(item_id)
        if item:
            self.session.delete(item)
            self.session.commit()
            self._refresh_lookup_table()
            self._sync_main_ui()

    def _add_app_type(self):
        name = self.app_name.text().strip()
        if not name: return
        item = AppTypeMultiplier(name=name, multiplier=self.app_mult.value())
        self.session.add(item); self.session.commit()
        self.app_name.clear(); self.app_mult.setValue(1.0)
        self._refresh_app_table(); self._sync_main_ui()

    def _del_app_type(self):
        r = self.app_table.currentRow()
        if r < 0: return
        item = self.session.query(AppTypeMultiplier).get(int(self.app_table.item(r, 0).text()))
        if item:
            self.session.delete(item); self.session.commit()
            self._refresh_app_table(); self._sync_main_ui()

    def _add_complexity(self):
        name = self.cx_name.text().strip()
        if not name: return
        item = ComplexityMultiplier(name=name, multiplier=self.cx_mult.value())
        self.session.add(item); self.session.commit()
        self.cx_name.clear(); self.cx_mult.setValue(1.0)
        self._refresh_cx_table(); self._sync_main_ui()

    def _del_complexity(self):
        r = self.cx_table.currentRow()
        if r < 0: return
        item = self.session.query(ComplexityMultiplier).get(int(self.cx_table.item(r, 0).text()))
        if item:
            self.session.delete(item); self.session.commit()
            self._refresh_cx_table(); self._sync_main_ui()

    def _add_pricing(self):
        name = self.ps_name.text().strip()
        if not name: return
        item = PricingStrategy(name=name, description=self.ps_desc.text().strip(),
                               profit_margin_pct=self.ps_prof.value(), 
                               risk_contingency_pct=self.ps_risk.value())
        self.session.add(item); self.session.commit()
        self.ps_name.clear(); self.ps_desc.clear(); self.ps_prof.setValue(0); self.ps_risk.setValue(0)
        self._refresh_ps_table(); self._sync_main_ui()

    def _del_pricing(self):
        r = self.ps_table.currentRow()
        if r < 0: return
        item = self.session.query(PricingStrategy).get(int(self.ps_table.item(r, 0).text()))
        if item:
            self.session.delete(item); self.session.commit()
            self._refresh_ps_table(); self._sync_main_ui()

    def _add_preset(self):
        name = self.ip_name.text().strip()
        if not name: return
        item = IndustryPreset(name=name)
        self.session.add(item); self.session.commit()
        self.ip_name.clear()
        self._refresh_ip_table(); self._sync_main_ui()

    def _del_preset(self):
        r = self.ip_table.currentRow()
        if r < 0: return
        item = self.session.query(IndustryPreset).get(int(self.ip_table.item(r, 0).text()))
        if item:
            self.session.delete(item); self.session.commit()
            self._refresh_ip_table(); self._sync_main_ui()

    def _sync_main_ui(self):
        """Force the Master Tab combo boxes to refresh along with new Estimation dropdowns."""
        self.main._refresh_estimation_combos()
        # You'll also want to update the role & category configs in Emp and Infra combo boxes...
        self.main._refresh_system_lookups()
