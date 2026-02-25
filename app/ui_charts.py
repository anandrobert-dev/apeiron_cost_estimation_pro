"""
Apeiron CostEstimation Pro – Chart Widgets
===========================================
Matplotlib charts embedded in PyQt6 via FigureCanvasQTAgg.
"""

import io
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


def create_stage_pie_chart(stage_distribution: dict, theme: dict) -> FigureCanvas:
    """Pie chart for stage-based cost distribution."""
    fig = Figure(figsize=(4.5, 3.2), dpi=100)
    fig.patch.set_facecolor(theme["chart_bg"])
    ax = fig.add_subplot(111)

    labels = list(stage_distribution.keys())
    values = list(stage_distribution.values())
    colors = theme.get("chart_palette", ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"])

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=colors[:len(labels)], startangle=90,
        textprops={"color": theme["chart_text"], "fontsize": 9},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color(theme["chart_text"])
    ax.set_title("Stage Cost Distribution", color=theme["chart_text"], fontsize=11, fontweight="bold", pad=10)
    fig.tight_layout()
    return FigureCanvas(fig)


def create_variance_bar_chart(estimated: float, actual: float, theme: dict) -> FigureCanvas:
    """Bar chart comparing estimated vs actual cost."""
    fig = Figure(figsize=(4.5, 3.2), dpi=100)
    fig.patch.set_facecolor(theme["chart_bg"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(theme["chart_bg"])

    bars = ax.bar(
        ["Estimated", "Actual"], [estimated, actual],
        color=[theme.get("accent", "#3B82F6"), theme.get("success", "#10B981")], width=0.5, edgecolor="none",
    )
    ax.set_title("Estimated vs Actual", color=theme["chart_text"], fontsize=11, fontweight="bold")
    ax.tick_params(colors=theme["chart_text"])
    ax.spines["bottom"].set_color(theme["border"])
    ax.spines["left"].set_color(theme["border"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h, f"₹{h:,.0f}",
                ha="center", va="bottom", color=theme["chart_text"], fontsize=9)
    fig.tight_layout()
    return FigureCanvas(fig)


def create_maintenance_line_chart(forecast: list, theme: dict) -> FigureCanvas:
    """Line chart for multi-year maintenance projection."""
    fig = Figure(figsize=(4.5, 3.2), dpi=100)
    fig.patch.set_facecolor(theme["chart_bg"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(theme["chart_bg"])

    years = [f["year"] for f in forecast]
    annual = [f["annual_cost"] for f in forecast]
    cumulative = [f["cumulative_cost"] for f in forecast]

    ax.plot(years, annual, "o-", color=theme.get("accent", "#3B82F6"), label="Annual", linewidth=2, markersize=6)
    ax.plot(years, cumulative, "s--", color=theme.get("warning", "#F59E0B"), label="Cumulative", linewidth=2, markersize=6)

    ax.set_title("Maintenance Forecast", color=theme["chart_text"], fontsize=11, fontweight="bold")
    ax.set_xlabel("Year", color=theme["chart_text"], fontsize=9)
    ax.set_ylabel("Cost (₹)", color=theme["chart_text"], fontsize=9)
    ax.legend(fontsize=8, facecolor=theme["chart_bg"], edgecolor=theme["border"],
              labelcolor=theme["chart_text"])
    ax.tick_params(colors=theme["chart_text"])
    ax.spines["bottom"].set_color(theme["border"])
    ax.spines["left"].set_color(theme["border"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return FigureCanvas(fig)


def create_module_cost_bar_chart(module_costs: list, theme: dict) -> FigureCanvas:
    """Horizontal bar chart showing cost per module."""
    fig = Figure(figsize=(4.5, 3.2), dpi=100)
    fig.patch.set_facecolor(theme["chart_bg"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(theme["chart_bg"])

    names = [m["name"][:20] for m in module_costs]
    costs = [m["cost"] for m in module_costs]
    colors = theme.get("chart_palette", ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#0EA5E9", "#EC4899", "#14B8A6"])

    ax.barh(names, costs, color=colors[:len(names)], height=0.6)
    ax.set_title("Cost by Module", color=theme["chart_text"], fontsize=11, fontweight="bold")
    ax.tick_params(colors=theme["chart_text"], labelsize=8)
    ax.spines["bottom"].set_color(theme["border"])
    ax.spines["left"].set_color(theme["border"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()
    fig.tight_layout()
    return FigureCanvas(fig)
