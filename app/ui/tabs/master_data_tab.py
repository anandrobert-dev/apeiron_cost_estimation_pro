"""Master Data Tab – Employee, Stack, Infrastructure Management"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTabWidget,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QAbstractItemView,
    QMessageBox,
    QScrollArea,
    QHeaderView,
)
from PyQt6.QtCore import Qt

from app.persistence.models import Employee, StackCost, InfraCost
from app.utils.formatting import format_inr
from app.ui.components.helpers import section_label
from app.ui.tabs.system_config_tab import SysConfigTab


class MasterDataTab(QWidget):
    """Tab for managing employees, stack costs, and infrastructure costs."""

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.session = main_window.session
        self.audit_repo = main_window.audit_repo
        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        """Build the master data UI with 4 sub-tabs."""
        layout = QVBoxLayout(self)

        # Create tab widget for Employee, Stack, Infra, System Config
        self.tabs = QTabWidget()
        self._build_employee_subtab()
        self._build_stack_subtab()
        self._build_infra_subtab()
        self._build_system_config_subtab()

        layout.addWidget(self.tabs)

    def _build_employee_subtab(self):
        """Employee management sub-tab."""
        ew = QWidget()
        outer_layout = QVBoxLayout(ew)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_w = QWidget()
        content_w.setMinimumHeight(650)
        el = QVBoxLayout(content_w)

        el.addWidget(section_label("Employee Master", self.main._theme))

        # Input form
        ef = QGroupBox("Add Employee")
        efl = QFormLayout(ef)

        self.emp_name = QLineEdit()
        self.emp_name.setPlaceholderText("Name")

        self.emp_role = QComboBox()
        self.emp_role.setEditable(True)
        self.emp_role.addItems(
            [
                "Project Manager",
                "UI/UX Designer",
                "Frontend Developer",
                "Backend Developer",
                "Full Stack Developer",
                "QA Engineer",
                "DevOps Engineer",
                "Data Engineer",
                "AI/ML Engineer",
                "Business Analyst",
                "Technical Lead",
            ]
        )

        self.emp_salary = QDoubleSpinBox()
        self.emp_salary.setRange(0, 10_000_000)
        self.emp_salary.setPrefix("₹ ")
        self.emp_salary.setDecimals(0)

        self.emp_pf = QDoubleSpinBox()
        self.emp_pf.setRange(0, 100)
        self.emp_pf.setValue(12)
        self.emp_pf.setSuffix(" %")

        self.emp_bonus = QDoubleSpinBox()
        self.emp_bonus.setRange(0, 100)
        self.emp_bonus.setValue(8.33)
        self.emp_bonus.setSuffix(" %")

        self.emp_leave = QDoubleSpinBox()
        self.emp_leave.setRange(0, 100)
        self.emp_leave.setValue(4)
        self.emp_leave.setSuffix(" %")

        self.emp_infra = QDoubleSpinBox()
        self.emp_infra.setRange(0, 100)
        self.emp_infra.setValue(5)
        self.emp_infra.setSuffix(" %")

        self.emp_admin = QDoubleSpinBox()
        self.emp_admin.setRange(0, 100)
        self.emp_admin.setValue(3)
        self.emp_admin.setSuffix(" %")

        efl.addRow("Name:", self.emp_name)
        efl.addRow("Role:", self.emp_role)
        efl.addRow("Base Salary:", self.emp_salary)
        efl.addRow("PF:", self.emp_pf)
        efl.addRow("Bonus:", self.emp_bonus)
        efl.addRow("Leave:", self.emp_leave)
        efl.addRow("Infra:", self.emp_infra)
        efl.addRow("Admin:", self.emp_admin)

        # Buttons
        br = QHBoxLayout()
        ab = QPushButton("Add Employee")
        ab.clicked.connect(self._add_employee)
        db = QPushButton("Delete Selected")
        db.setProperty("cssClass", "danger")
        db.clicked.connect(self._del_employee)
        br.addWidget(ab)
        br.addWidget(db)

        el.addWidget(ef)
        el.addLayout(br)

        # Table
        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(6)
        self.emp_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Role", "Base Salary", "Real Monthly", "Hourly Rate"]
        )
        self.emp_table.horizontalHeader().setStretchLastSection(False)
        self.emp_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.emp_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.emp_table.setMinimumHeight(200)
        el.addWidget(self.emp_table, stretch=1)

        scroll.setWidget(content_w)
        outer_layout.addWidget(scroll)

        self.tabs.addTab(ew, "Employees")

    def _build_stack_subtab(self):
        """Stack costs management sub-tab."""
        sw = QWidget()
        outer_layout = QVBoxLayout(sw)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_w = QWidget()
        content_w.setMinimumHeight(500)
        sl = QVBoxLayout(content_w)

        sl.addWidget(section_label("Stack Cost Master", self.main._theme))

        # Input form
        sf = QGroupBox("Add Stack Cost")
        sfl = QFormLayout(sf)

        self.stack_name = QLineEdit()
        self.stack_name.setPlaceholderText("Tool/License")

        self.stack_cat = QComboBox()
        self.stack_cat.setEditable(True)
        self.stack_cat.addItems(
            ["IDE", "Cloud", "CI/CD", "Monitoring", "Database", "Other"]
        )

        self.stack_cost = QDoubleSpinBox()
        self.stack_cost.setRange(0, 10_000_000)
        self.stack_cost.setPrefix("₹ ")
        self.stack_cost.setDecimals(0)

        self.stack_bill = QComboBox()
        self.stack_bill.addItems(["one_time", "monthly", "yearly", "usage_based"])

        sfl.addRow("Name:", self.stack_name)
        sfl.addRow("Category:", self.stack_cat)
        sfl.addRow("Cost:", self.stack_cost)
        sfl.addRow("Billing:", self.stack_bill)

        # Buttons
        sbr = QHBoxLayout()
        sab = QPushButton("Add Stack Cost")
        sab.clicked.connect(self._add_stack)
        sdb = QPushButton("Delete Selected")
        sdb.setProperty("cssClass", "danger")
        sdb.clicked.connect(self._del_stack)
        sbr.addWidget(sab)
        sbr.addWidget(sdb)

        sl.addWidget(sf)
        sl.addLayout(sbr)

        # Table
        self.stack_table = QTableWidget()
        self.stack_table.setColumnCount(4)
        self.stack_table.setHorizontalHeaderLabels(["ID", "Name", "Cost", "Billing"])
        self.stack_table.horizontalHeader().setStretchLastSection(False)
        self.stack_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.stack_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.stack_table.setMinimumHeight(200)
        sl.addWidget(self.stack_table, stretch=1)

        scroll.setWidget(content_w)
        outer_layout.addWidget(scroll)

        self.tabs.addTab(sw, "Stack Costs")

    def _build_infra_subtab(self):
        """Infrastructure costs management sub-tab."""
        iw = QWidget()
        outer_layout = QVBoxLayout(iw)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_w = QWidget()
        content_w.setMinimumHeight(500)
        il = QVBoxLayout(content_w)

        il.addWidget(section_label("Infrastructure Cost Master", self.main._theme))

        # Input form
        inf = QGroupBox("Add Infra Cost")
        ifl = QFormLayout(inf)

        self.infra_name = QLineEdit()
        self.infra_name.setPlaceholderText("Item")

        self.infra_cat = QComboBox()
        self.infra_cat.setEditable(True)
        self.infra_cat.addItems(
            [
                "Hosting",
                "Database",
                "API Integration",
                "Security",
                "App Store Fees",
                "Marketing",
                "DevOps",
                "Other",
            ]
        )

        self.infra_cost_in = QDoubleSpinBox()
        self.infra_cost_in.setRange(0, 10_000_000)
        self.infra_cost_in.setPrefix("₹ ")
        self.infra_cost_in.setDecimals(0)

        self.infra_bill = QComboBox()
        self.infra_bill.addItems(["one_time", "monthly", "yearly", "usage_based"])

        ifl.addRow("Name:", self.infra_name)
        ifl.addRow("Category:", self.infra_cat)
        ifl.addRow("Cost:", self.infra_cost_in)
        ifl.addRow("Billing:", self.infra_bill)

        # Buttons
        ibr = QHBoxLayout()
        iab = QPushButton("Add Infra Cost")
        iab.clicked.connect(self._add_infra)
        idb = QPushButton("Delete Selected")
        idb.setProperty("cssClass", "danger")
        idb.clicked.connect(self._del_infra)
        ibr.addWidget(iab)
        ibr.addWidget(idb)

        il.addWidget(inf)
        il.addLayout(ibr)

        # Table
        self.infra_table = QTableWidget()
        self.infra_table.setColumnCount(4)
        self.infra_table.setHorizontalHeaderLabels(["ID", "Name", "Cost", "Billing"])
        self.infra_table.horizontalHeader().setStretchLastSection(False)
        self.infra_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.infra_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.infra_table.setMinimumHeight(200)
        il.addWidget(self.infra_table, stretch=1)

        scroll.setWidget(content_w)
        outer_layout.addWidget(scroll)

        self.tabs.addTab(iw, "Infrastructure")

    def _build_system_config_subtab(self):
        """System configuration management sub-tab."""
        self.sysconfig_tab = SysConfigTab(self.main)
        self.tabs.addTab(self.sysconfig_tab, "System Config")

    # ═══════════════ EMPLOYEE CRUD ═══════════════
    def _add_employee(self):
        name = self.emp_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name required.")
            return

        emp = Employee(
            name=name,
            role=self.emp_role.currentText(),
            base_salary=self.emp_salary.value(),
            pf_pct=self.emp_pf.value(),
            bonus_pct=self.emp_bonus.value(),
            leave_pct=self.emp_leave.value(),
            infra_pct=self.emp_infra.value(),
            admin_pct=self.emp_admin.value(),
        )
        emp.recalculate_costs()
        self.session.add(emp)
        self.session.commit()
        self.audit_repo.log("employees", emp.id, "CREATE")

        self._refresh_emp_table()
        self.main._refresh_emp_combo()
        self.emp_name.clear()
        self.emp_salary.setValue(0)
        self.main.statusBar().showMessage(f"Employee '{name}' added.", 3000)

    def _del_employee(self):
        r = self.emp_table.currentRow()
        if r < 0:
            return

        eid = int(self.emp_table.item(r, 0).text())
        e = self.session.query(Employee).get(eid)
        if e:
            self.audit_repo.log("employees", eid, "DELETE")
            self.session.delete(e)
            self.session.commit()
            self._refresh_emp_table()
            self.main._refresh_emp_combo()

    def _refresh_emp_table(self):
        emps = self.session.query(Employee).filter_by(is_active=True).all()
        self.emp_table.setRowCount(len(emps))
        for i, e in enumerate(emps):
            for j, v in enumerate(
                [
                    str(e.id),
                    e.name,
                    e.role,
                    format_inr(e.base_salary),
                    format_inr(e.real_monthly_cost),
                    format_inr(e.hourly_cost),
                ]
            ):
                self.emp_table.setItem(i, j, QTableWidgetItem(v))
        self.emp_table.resizeColumnsToContents()

    # ═══════════════ STACK CRUD ═══════════════
    def _add_stack(self):
        n = self.stack_name.text().strip()
        if not n:
            QMessageBox.warning(self, "Validation", "Name required.")
            return

        sc = StackCost(
            name=n,
            category=self.stack_cat.currentText(),
            cost=self.stack_cost.value(),
            billing_type=self.stack_bill.currentText(),
        )
        self.session.add(sc)
        self.session.commit()
        self._refresh_stack_table()
        self.stack_name.clear()
        self.stack_cost.setValue(0)

    def _del_stack(self):
        r = self.stack_table.currentRow()
        if r < 0:
            return

        sc = self.session.query(StackCost).get(int(self.stack_table.item(r, 0).text()))
        if sc:
            self.session.delete(sc)
            self.session.commit()
            self._refresh_stack_table()

    def _refresh_stack_table(self):
        items = self.session.query(StackCost).all()
        self.stack_table.setRowCount(len(items))
        for i, s in enumerate(items):
            for j, v in enumerate(
                [str(s.id), s.name, format_inr(s.cost), s.billing_type]
            ):
                self.stack_table.setItem(i, j, QTableWidgetItem(v))
        self.stack_table.resizeColumnsToContents()

    # ═══════════════ INFRA CRUD ═══════════════
    def _add_infra(self):
        n = self.infra_name.text().strip()
        if not n:
            QMessageBox.warning(self, "Validation", "Name required.")
            return

        ic = InfraCost(
            name=n,
            category=self.infra_cat.currentText(),
            cost=self.infra_cost_in.value(),
            billing_type=self.infra_bill.currentText(),
        )
        self.session.add(ic)
        self.session.commit()
        self._refresh_infra_table()
        self.infra_name.clear()
        self.infra_cost_in.setValue(0)

    def _del_infra(self):
        r = self.infra_table.currentRow()
        if r < 0:
            return

        ic = self.session.query(InfraCost).get(int(self.infra_table.item(r, 0).text()))
        if ic:
            self.session.delete(ic)
            self.session.commit()
            self._refresh_infra_table()

    def _refresh_infra_table(self):
        items = self.session.query(InfraCost).all()
        self.infra_table.setRowCount(len(items))
        for i, item in enumerate(items):
            for j, v in enumerate(
                [str(item.id), item.name, format_inr(item.cost), item.billing_type]
            ):
                self.infra_table.setItem(i, j, QTableWidgetItem(v))
        self.infra_table.resizeColumnsToContents()

    def _refresh_all(self):
        """Refresh all tables."""
        self._refresh_emp_table()
        self._refresh_stack_table()
        self._refresh_infra_table()
