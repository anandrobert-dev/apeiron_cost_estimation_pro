"""
Apeiron CostEstimation Pro – Client Proposal Generator (Layer 2)
================================================================
Generates professional PDF proposals hiding internal costs.
Uses ReportLab for PDF rendering.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from app.logic import format_inr


# ──────────────────────────────────────────────
# COLOR PALETTE
# ──────────────────────────────────────────────
PRIMARY = HexColor("#1a237e")     # Deep Indigo
SECONDARY = HexColor("#283593")   # Dark Blue
ACCENT = HexColor("#ff6f00")      # Orange
LIGHT_BG = HexColor("#f5f5f5")    # Light Grey
WHITE = HexColor("#ffffff")
TEXT_DARK = HexColor("#212121")
TEXT_MUTED = HexColor("#757575")
BORDER = HexColor("#e0e0e0")


# ──────────────────────────────────────────────
# STYLES
# ──────────────────────────────────────────────
def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=6 * mm,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Helvetica",
        fontSize=14,
        textColor=SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=PRIMARY,
        spaceBefore=8 * mm,
        spaceAfter=4 * mm,
    ))
    styles.add(ParagraphStyle(
        name="SubHeader",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=SECONDARY,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName="Helvetica",
        fontSize=11,
        textColor=TEXT_DARK,
        leading=16,
        spaceAfter=2 * mm,
    ))
    styles.add(ParagraphStyle(
        name="FooterText",
        fontName="Helvetica",
        fontSize=8,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="RightAligned",
        fontName="Helvetica",
        fontSize=11,
        textColor=TEXT_DARK,
        alignment=TA_RIGHT,
    ))
    return styles


# ──────────────────────────────────────────────
# TABLE HELPERS
# ──────────────────────────────────────────────
def _styled_table(data, col_widths=None):
    """Create a professionally styled table."""
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_DARK),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(
        A4[0] / 2, 15 * mm,
        f"Confidential – TechLogix | Generated on {datetime.now().strftime('%d %b %Y')} | Page {doc.page}"
    )
    canvas.restoreState()


# ──────────────────────────────────────────────
# PROPOSAL GENERATOR
# ──────────────────────────────────────────────
def generate_proposal_pdf(
    filepath: str,
    project_name: str,
    client_name: str,
    app_type: str,
    complexity: str,
    description: str,
    timeline_months: float,
    scope_modules: list,
    final_price: float,
    stage_distribution: dict,
    maintenance_annual: float = 0.0,
    maintenance_years: int = 0,
    payment_terms: str = "",
    include_maintenance: bool = True,
) -> str:
    """
    Generate a professional client-facing proposal PDF.
    Hides internal rates, salaries, buffers.
    Returns the filepath.
    """
    styles = _get_styles()
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=25 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )
    story = []

    # ── COVER PAGE ──
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("TechLogix", styles["CoverSubtitle"]))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Project Cost Proposal", styles["CoverTitle"]))
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(
        width="60%", thickness=2, color=ACCENT,
        spaceBefore=2 * mm, spaceAfter=6 * mm,
        hAlign="CENTER"
    ))
    story.append(Paragraph(f"<b>{project_name}</b>", styles["CoverSubtitle"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"Prepared for: {client_name}", styles["CoverSubtitle"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        datetime.now().strftime("%d %B %Y"), styles["CoverSubtitle"]
    ))
    story.append(PageBreak())

    # ── EXECUTIVE SUMMARY ──
    story.append(Paragraph("1. Executive Summary", styles["SectionHeader"]))
    story.append(Paragraph(
        f"This document presents the cost proposal for <b>{project_name}</b>, "
        f"a <b>{complexity}</b>-level <b>{app_type}</b> application. "
        f"The estimated project timeline is <b>{timeline_months:.1f} months</b>.",
        styles["BodyText2"]
    ))
    if description:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(description, styles["BodyText2"]))
    story.append(Spacer(1, 4 * mm))

    # ── SCOPE ──
    story.append(Paragraph("2. High-Level Scope", styles["SectionHeader"]))
    if scope_modules:
        scope_data = [["#", "Module / Feature"]]
        for i, mod_name in enumerate(scope_modules, 1):
            scope_data.append([str(i), mod_name])
        story.append(_styled_table(scope_data, col_widths=[30, 400]))
    else:
        story.append(Paragraph("Scope to be detailed during planning phase.", styles["BodyText2"]))
    story.append(Spacer(1, 4 * mm))

    # ── TIMELINE ──
    story.append(Paragraph("3. Project Timeline", styles["SectionHeader"]))
    if stage_distribution:
        timeline_data = [["Phase", "Allocation"]]
        for stage, cost in stage_distribution.items():
            pct = round(cost / final_price * 100, 1) if final_price > 0 else 0
            timeline_data.append([stage, f"{pct}%"])
        story.append(_styled_table(timeline_data, col_widths=[200, 230]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f"Estimated Duration: <b>{timeline_months:.1f} months</b>",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 4 * mm))

    # ── INVESTMENT ──
    story.append(Paragraph("4. Total Investment", styles["SectionHeader"]))
    story.append(Spacer(1, 2 * mm))

    inv_data = [["Description", "Amount"]]
    inv_data.append(["Project Development", format_inr(final_price)])
    if include_maintenance and maintenance_annual > 0 and maintenance_years > 0:
        total_maint = maintenance_annual * maintenance_years
        inv_data.append([
            f"Maintenance ({maintenance_years} yr{'s' if maintenance_years > 1 else ''})",
            format_inr(total_maint),
        ])
        inv_data.append([
            "Grand Total",
            format_inr(final_price + total_maint),
        ])
    story.append(_styled_table(inv_data, col_widths=[280, 150]))
    story.append(Spacer(1, 4 * mm))

    # ── PAYMENT TERMS ──
    if payment_terms:
        story.append(Paragraph("5. Payment Terms", styles["SectionHeader"]))
        story.append(Paragraph(payment_terms, styles["BodyText2"]))
        story.append(Spacer(1, 4 * mm))

    # ── SIGNATURE BLOCK ──
    story.append(Spacer(1, 20 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    story.append(Spacer(1, 10 * mm))

    sig_data = [
        ["For TechLogix", "For Client"],
        ["", ""],
        ["_________________________", "_________________________"],
        ["Authorized Signatory", f"{client_name}"],
        [f"Date: {datetime.now().strftime('%d/%m/%Y')}", "Date: __/__/____"],
    ]
    sig_table = Table(sig_data, colWidths=[220, 220])
    sig_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_DARK),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)

    # ── BUILD PDF ──
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return filepath
