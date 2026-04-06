import os
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from services.analysis import generate_quality_issues

PRIMARY = HexColor("#6366f1")
SECONDARY = HexColor("#0f172a")
ACCENT = HexColor("#22d3ee")
LIGHT_BG = HexColor("#f1f5f9")
SUCCESS = HexColor("#22c55e")
WARNING = HexColor("#f59e0b")

def build_pdf_report(
    output_path: str,
    filename: str,
    summary: Dict[str, Any],
    timestamp: str
) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=24,
        textColor=PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    sub_style = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#64748b"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    story.append(Paragraph("DataCleaner", title_style))
    story.append(Paragraph("Data Cleaning &amp; Analysis Report", sub_style))
    story.append(Paragraph(f"Generated: {timestamp}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=12))

    # File info
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=SECONDARY,
        spaceAfter=6,
        spaceBefore=12,
        fontName="Helvetica-Bold"
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=SECONDARY,
        spaceAfter=4,
    )

    story.append(Paragraph("File Information", section_style))
    info_data = [
        ["Field", "Value"],
        ["Filename", filename],
        ["Processed At", timestamp],
    ]
    info_table = Table(info_data, colWidths=[5*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_BG]),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)

    # Cleaning options
    options = summary.get("cleaning_options", {})
    story.append(Paragraph("Cleaning Configuration", section_style))
    opts_data = [["Option", "Value"]]
    opts_map = {
        "remove_duplicates": "Remove Duplicates",
        "missing_numeric": "Numeric Missing Strategy",
        "missing_categorical": "Categorical Missing Strategy",
        "normalize_types": "Type Normalization",
        "handle_outliers": "Outlier Handling",
    }
    for key, label in opts_map.items():
        val = options.get(key, "N/A")
        opts_data.append([label, str(val)])

    notes = options.get("user_notes") or "None"
    opts_data.append(["User Notes", notes])

    opts_table = Table(opts_data, colWidths=[8*cm, 9*cm])
    opts_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(opts_table)

    # Before/After stats
    before = summary.get("before", {})
    after = summary.get("after", {})
    story.append(Paragraph("Dataset: Before vs After", section_style))

    ba_data = [
        ["Metric", "Before", "After"],
        ["Rows", str(before.get("rows", 0)), str(after.get("rows", 0))],
        ["Columns", str(before.get("columns", 0)), str(after.get("columns", 0))],
        ["Duplicates Removed", str(summary.get("duplicates_removed", 0)), "—"],
        ["Outliers Handled", str(summary.get("outliers_handled", 0)), "—"],
    ]
    # Total missing
    total_missing_before = sum(before.get("missing_by_column", {}).values())
    total_missing_after = sum(after.get("missing_by_column", {}).values())
    ba_data.append(["Total Missing Values", str(total_missing_before), str(total_missing_after)])

    ba_table = Table(ba_data, colWidths=[8*cm, 4.5*cm, 4.5*cm])
    ba_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(ba_table)

    # Quality issues
    issues = generate_quality_issues(summary)
    story.append(Paragraph("Data Quality Issues Fixed", section_style))
    if issues:
        for issue in issues:
            story.append(Paragraph(f"• {issue}", body_style))
    else:
        story.append(Paragraph("No major quality issues found.", body_style))

    # Descriptive stats
    stats = summary.get("stats", {})
    if stats:
        story.append(Paragraph("Descriptive Statistics (Numeric Columns)", section_style))
        stat_data = [["Column", "Mean", "Median", "Std", "Min", "Max"]]
        for col, s in stats.items():
            stat_data.append([
                col,
                str(s.get("mean", "N/A")),
                str(s.get("median", "N/A")),
                str(s.get("std", "N/A")),
                str(s.get("min", "N/A")),
                str(s.get("max", "N/A")),
            ])
        stat_table = Table(stat_data, colWidths=[4*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm, 2*cm])
        stat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(stat_table)

    # Correlations
    correlations = summary.get("correlations", [])
    if correlations:
        story.append(Paragraph("Top Feature Correlations", section_style))
        corr_data = [["Column 1", "Column 2", "Correlation"]]
        for item in correlations:
            corr_data.append([item["col1"], item["col2"], str(item["correlation"])])
        corr_table = Table(corr_data, colWidths=[6*cm, 6*cm, 5*cm])
        corr_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ]))
        story.append(corr_table)

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#e2e8f0")))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=HexColor("#94a3b8"), alignment=TA_CENTER)
    story.append(Paragraph("DataCleaner MVP — AI-powered data cleaning platform", footer_style))

    doc.build(story)
