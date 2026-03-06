"""
Apeiron CostEstimation Pro – SOP & User Guide
==============================================
A detachable, colorful window explaining each tab and the calculation matrix.
"""

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt

SOP_HTML = """
<html>
<head>
<style>
    body { background-color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; line-height: 1.6; color: #333; padding: 10px; }
    h1 { color: #2c3e50; border-bottom: 2px solid #3d5a99; padding-bottom: 5px; }
    h2 { color: #3d5a99; margin-top: 20px; }
    h3 { color: #c07d20; }
    .tab-section { background-color: #f8f9fa; border-left: 5px solid #3d5a99; padding: 10px 15px; margin: 15px 0; border-radius: 4px; }
    .calc-box { background-color: #e8f4f8; border: 1px solid #bce8f1; padding: 15px; border-radius: 6px; }
    .formula { font-family: monospace; font-size: 15px; color: #d35400; font-weight: bold; background: #fff; padding: 4px 8px; border-radius: 3px; display: inline-block; }
    .highlight { font-weight: bold; color: #27855a; }
    ul { margin-top: 5px; }
    li { margin-bottom: 5px; }
</style>
</head>
<body>

<h1>Apeiron CostEstimation Pro - Standard Operating Procedure (SOP)</h1>
<p>Welcome to the Apeiron CostEstimation Pro system. This guide is designed to be kept open on your second monitor while you work.</p>

<h2>📋 1. The Four Core Tabs Explained</h2>

<div class="tab-section">
    <h3>Tab 1: Master Data (The Foundation)</h3>
    <p>Before running any estimates, ensure your master costs are up to date.</p>
    <ul>
        <li><b>Employees:</b> Base salaries get multiplied by overheads (PF, Bonus, Leave, Infra, Admin) to calculate the <span class="highlight">True Real Hourly Cost</span>.</li>
        <li><b>Stack & Infra:</b> Add ongoing costs like AWS hosting, GitHub Copilot licenses, or API subscriptions.</li>
    </ul>
</div>

<div class="tab-section">
    <h3>Tab 2: New Estimation (The Engine)</h3>
    <p>This is where you build the client quote.</p>
    <ul>
        <li><b>Industry Presets:</b> Fast-track estimates by loading templates (e.g., SME CRM) which auto-populate standard modules.</li>
        <li><b>Pricing Strategy:</b> Overrides profit and risk. <i>Competitive</i> strips margins to win the bid; <i>Premium Enterprise</i> pads the budget for high-touch clients.</li>
        <li><b>Module Hours:</b> Assign specific employees to specific task modules.</li>
        <li><b>Live Charts:</b> Watch the pie chart dynamically update as you add modules.</li>
    </ul>
</div>

<div class="tab-section">
    <h3>Tab 3: Analysis Dashboard (The Financials)</h3>
    <p>Track post-completion project health to refine future quotes.</p>
    <ul>
        <li><b>Enter Actuals:</b> Once a project is finished, enter the actual money spent.</li>
        <li><b>Variance Badge:</b> The system grades you: <span style="color:green;font-weight:bold;">Perfect Estimate (0-5%)</span>, Controlled (5-10%), Moderate (10-20%), or <span style="color:red;font-weight:bold;">High Risk (>20%)</span>.</li>
        <li><b>Maintenance Forecast:</b> Multi-year projections to see long-term revenue.</li>
    </ul>
</div>

<div class="tab-section">
    <h3>Tab 4: Proposal Export (The Output)</h3>
    <p>Generate the final client-facing document.</p>
    <ul>
        <li><b>Terms & Maintenance:</b> Attach payment milestones (e.g., 50/50 split) and decide if maintenance contracts are bundled.</li>
        <li><b>Export PDF:</b> Generates a clean, corporate-branded PDF proposal.</li>
    </ul>
</div>

<h2>🧮 2. The Internal Calculation Matrix</h2>
<p>Ever wonder how the Final Price is calculated? Here is the exact mathematical flow the engine uses:</p>

<div class="calc-box">
    <p><b>Step 1: Raw Employee Cost</b></p>
    <p><span class="formula">Raw Labor = Σ (Module Hours × Employee True Hourly Rate)</span></p>

    <p><b>Step 2: Adjusted Labor (The Multipliers)</b></p>
    <p><span class="formula">Adjusted Labor = Raw Labor × App Type Multiplier × Complexity Multiplier × Region Multiplier</span></p>

    <p><b>Step 3: Gross Cost (The Floor)</b></p>
    <p><span class="formula">Gross Cost = Adjusted Labor + Infrastructure Costs + Stack Costs</span></p>

    <p><b>Step 4: Safe Cost (The Buffer)</b></p>
    <p><span class="formula">Safe Cost = Gross Cost + Risk Contingency % + Maintenance Buffer %</span></p>

    <p><b>Step 5: Final Price (The Quote)</b></p>
    <p><span class="formula">Final Price = Safe Cost + Profit Margin %</span></p>
</div>

<h2>💡 3. Deep Dive: Key Analytics</h2>
<ul>
    <li><b>Burn Rate/Month:</b> <span class="formula">Final Price ÷ Estimated Duration Months</span>. Use this to ensure your cash flow covers server and payroll run rates.</li>
    <li><b>Revenue Margin:</b> <span class="formula">((Final Price - Safe Cost) ÷ Final Price) × 100</span>. Your true profit margin after accounting for all disastrous risk scenarios.</li>
</ul>

</body>
</html>
"""

class SOPWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 Apeiron SOP & Calculation Matrix")
        self.setMinimumSize(500, 500)
        
        # Float the window independently
        self.setWindowFlags(Qt.WindowType.Window)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.browser = QTextBrowser()
        self.browser.setHtml(SOP_HTML)
        layout.addWidget(self.browser)
        
        close_btn = QPushButton("Close SOP Guide")
        close_btn.setStyleSheet("padding: 8px; font-weight: bold; background-color: #3d5a99; color: white; border-radius: 4px;")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
