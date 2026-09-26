"""One-time script to generate the 10 fictional ForgeCore Industries PDFs.

Run with:
    python scripts/generate_documents.py

Outputs:
    data/raw/*.pdf   (10 PDF documents)

These PDFs are checked into git so the project is self-contained and reproducible.
The content is fictional but internally consistent — sufficient for a working RAG demo.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMPANY = "ForgeCore Industries"
TAGLINE = "B2B Manufacturer of Industrial Crucibles & Foundry Consumables"
FOUNDED = "Founded 1987 — Pittsburgh, Pennsylvania, USA"


# ─── Style helpers ───────────────────────────────────────────────────────────
def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontSize=22,
            spaceAfter=18,
            textColor=colors.HexColor("#1a3a5c"),
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=16,
            spaceBefore=18,
            spaceAfter=10,
            textColor=colors.HexColor("#1a3a5c"),
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#2d5986"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontSize=10.5,
            leading=14,
            spaceAfter=8,
            alignment=0,  # left
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontSize=10.5,
            leading=14,
            leftIndent=18,
            bulletIndent=6,
            spaceAfter=4,
        ),
        "note": ParagraphStyle(
            "Note",
            parent=base["BodyText"],
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#555555"),
            spaceAfter=6,
        ),
    }


def _para(text: str, style: ParagraphStyle) -> Paragraph:
    """Escape XML-special characters and wrap in Paragraph."""
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style)


def _table(headers: list[str], rows: list[list[str]]) -> Table:
    """Build a styled table with header row in brand colour."""
    data = [headers, *rows]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#888888")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f9")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


# ─── 1. Product Catalogue ─────────────────────────────────────────────────────
def build_product_catalogue() -> None:
    s = _styles()
    story: list = []
    story += [_para(f"{COMPANY}", s["title"]), _para(TAGLINE, s["body"]), _para(FOUNDED, s["note"])]
    story += [Spacer(1, 0.2 * inch)]

    story += [_para("Product Catalogue — 2025 Edition", s["h1"])]
    story += [
        _para(
            "ForgeCore Industries has been a trusted supplier of high-performance crucibles and foundry "
            "consumables for over 35 years. Our product line serves foundries, smelters, and research "
            "laboratories across 40+ countries. Each product is engineered for durability, thermal "
            "stability, and consistent performance in demanding industrial environments.",
            s["body"],
        )
    ]

    story += [_para("Product Family Overview", s["h2"])]
    story += [
        _table(
            ["SKU", "Material", "Max Temp (°C)", "Primary Use"],
            [
                ["FC-45", "Silicon Carbide", "1,500", "Ferrous metal melting"],
                ["FC-50", "High-purity Graphite", "1,800", "Non-ferrous metals, copper alloys"],
                ["FC-72", "Clay-Graphite Composite", "1,300", "Aluminum and zinc casting"],
                ["FC-90", "Zircon (ZrSiO₄)", "2,000", "Precious metals, specialty alloys"],
                ["FC-AX", "Alumina Ceramic", "1,750", "High-purity laboratory melting"],
                ["FC-MX", "Magnesia Refractory", "1,600", "Slag-line protection"],
            ],
        )
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("Detailed Product Descriptions", s["h1"])]

    products = [
        (
            "FC-45 — Silicon Carbide Crucible",
            "Our flagship product. FC-45 is engineered for high-temperature ferrous metal melting "
            "applications including iron and steel production. The silicon carbide composition offers "
            "exceptional thermal conductivity and resistance to thermal shock.",
            [("Operating Temperature", "Up to 1,500°C"), ("Standard Sizes", "S, M, L, XL"), ("Wall Thickness", "12-25 mm"), ("Typical Lifespan", "300-500 heats")],
        ),
        (
            "FC-50 — High-Purity Graphite Crucible",
            "Designed for non-ferrous metal melting, particularly copper alloys, brass, and bronze. "
            "The high-purity graphite construction provides excellent thermal conductivity and minimal "
            "contamination risk for sensitive alloys.",
            [("Operating Temperature", "Up to 1,800°C"), ("Standard Sizes", "S, M, L, XL, XXL"), ("Carbon Content", "99.5% min"), ("Typical Lifespan", "200-400 heats")],
        ),
        (
            "FC-72 — Clay-Graphite Composite Crucible",
            "An economical choice for aluminum and zinc casting operations. The clay-graphite blend "
            "balances cost and performance for high-volume production foundries.",
            [("Operating Temperature", "Up to 1,300°C"), ("Standard Sizes", "S, M, L"), ("Density", "2.1 g/cm³"), ("Typical Lifespan", "150-250 heats")],
        ),
        (
            "FC-90 — Zircon Crucible",
            "A premium crucible for precious metals and specialty alloys. Zircon (zirconium silicate) "
            "offers outstanding chemical inertness and the highest temperature rating in our lineup.",
            [("Operating Temperature", "Up to 2,000°C"), ("Standard Sizes", "S, M, L"), ("ZrO₂ Content", "65% min"), ("Typical Lifespan", "100-200 heats")],
        ),
    ]
    for title, desc, specs in products:
        story += [_para(title, s["h2"]), _para(desc, s["body"])]
        story += [_table(["Specification", "Value"], [list(pair) for pair in specs])]
        story += [Spacer(1, 0.15 * inch)]

    story += [_para("Ordering Information", s["h1"])]
    story += [
        _para(
            "Orders can be placed via your regional ForgeCore sales representative or through our "
            "customer portal at orders.forgecore.example.com. Standard sizes ship within 5 business days; "
            "custom dimensions require a 4-6 week lead time. All crucibles ship in protective foam-lined "
            "wooden crates with full handling documentation.",
            s["body"],
        ),
        _para(
            "Minimum order quantities apply for custom sizes: 25 units for FC-45 and FC-50, 50 units for "
            "FC-72, and 10 units for FC-90. Volume discounts are available for orders exceeding 100 units.",
            s["body"],
        ),
    ]
    story += [PageBreak()]
    story += [_para("Technical Support and Warranty", s["h1"])]
    story += [
        _para(
            "All ForgeCore products are backed by a 12-month limited warranty against manufacturing "
            "defects. Our applications engineering team provides complimentary sizing and material "
            "selection consultations. Contact support@forgecore.example.com or call +1-412-555-0142.",
            s["body"],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "01_product_catalogue.pdf"),
        pagesize=LETTER,
        title="ForgeCore Product Catalogue 2025",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 2. Crucible Specifications ───────────────────────────────────────────────
def build_specifications() -> None:
    s = _styles()
    story: list = [_para("Crucible Specifications", s["title"]), _para(f"{COMPANY} — Engineering Division", s["body"])]
    story += [Spacer(1, 0.2 * inch)]
    story += [_para("Engineering Specifications — FC Series Crucibles", s["h1"])]
    story += [
        _para(
            "This document provides detailed engineering specifications for all standard crucibles in the "
            "ForgeCore FC series. All dimensions are nominal and subject to ±2% manufacturing tolerance. "
            "Custom specifications are available on request.",
            s["body"],
        )
    ]

    products = [
        (
            "FC-45 — Silicon Carbide",
            {
                "Physical Properties": [
                    ["Bulk Density", "3.05 g/cm³"],
                    ["Apparent Porosity", "12% max"],
                    ["Cold Crushing Strength", "120 MPa min"],
                    ["Modulus of Rupture", "45 MPa @ 25°C"],
                    ["Thermal Conductivity", "85 W/m·K @ 1000°C"],
                    ["Thermal Expansion", "4.5 × 10⁻⁶ /°C"],
                ],
                "Operating Limits": [
                    ["Maximum Service Temperature", "1,500°C"],
                    ["Recommended Operating Range", "1,100-1,450°C"],
                    ["Thermal Shock Resistance", "ΔT 400°C"],
                    ["Maximum Heating Rate", "200°C/hour"],
                ],
                "Standard Dimensions (mm)": [
                    ["Size", "Height", "Outer Ø", "Wall", "Capacity"],
                    ["S", "200", "150", "12", "2.5 L"],
                    ["M", "280", "200", "15", "6.0 L"],
                    ["L", "360", "260", "20", "14 L"],
                    ["XL", "450", "320", "25", "26 L"],
                ],
            },
        ),
        (
            "FC-50 — High-Purity Graphite",
            {
                "Physical Properties": [
                    ["Bulk Density", "1.78 g/cm³"],
                    ["Carbon Content", "99.5% min"],
                    ["Ash Content", "0.3% max"],
                    ["Electrical Resistivity", "12 µΩ·m max"],
                    ["Thermal Conductivity", "110 W/m·K"],
                    ["Modulus of Elasticity", "10 GPa"],
                ],
                "Operating Limits": [
                    ["Maximum Service Temperature", "1,800°C"],
                    ["Recommended Operating Range", "1,200-1,750°C"],
                    ["Oxidation Resistance", "Requires inert atmosphere above 600°C"],
                    ["Maximum Heating Rate", "300°C/hour"],
                ],
                "Standard Dimensions (mm)": [
                    ["Size", "Height", "Outer Ø", "Wall", "Capacity"],
                    ["S", "220", "160", "10", "3.0 L"],
                    ["M", "300", "220", "13", "7.5 L"],
                    ["L", "400", "290", "18", "19 L"],
                    ["XL", "500", "360", "22", "36 L"],
                    ["XXL", "600", "440", "28", "65 L"],
                ],
            },
        ),
        (
            "FC-72 — Clay-Graphite Composite",
            {
                "Physical Properties": [
                    ["Bulk Density", "2.10 g/cm³"],
                    ["Carbon Content", "32%"],
                    ["Modulus of Rupture", "18 MPa"],
                    ["Thermal Conductivity", "25 W/m·K"],
                    ["Thermal Expansion", "3.2 × 10⁻⁶ /°C"],
                ],
                "Operating Limits": [
                    ["Maximum Service Temperature", "1,300°C"],
                    ["Recommended Operating Range", "700-1,250°C"],
                    ["Thermal Shock Resistance", "ΔT 350°C"],
                    ["Maximum Heating Rate", "150°C/hour"],
                ],
                "Standard Dimensions (mm)": [
                    ["Size", "Height", "Outer Ø", "Wall", "Capacity"],
                    ["S", "180", "130", "10", "1.8 L"],
                    ["M", "260", "190", "13", "5.0 L"],
                    ["L", "340", "250", "17", "12 L"],
                ],
            },
        ),
        (
            "FC-90 — Zircon",
            {
                "Physical Properties": [
                    ["Bulk Density", "3.85 g/cm³"],
                    ["ZrO₂ Content", "65% min"],
                    ["SiO₂ Content", "33%"],
                    ["Cold Crushing Strength", "150 MPa"],
                    ["Thermal Expansion", "4.0 × 10⁻⁶ /°C"],
                    ["Thermal Conductivity", "5 W/m·K"],
                ],
                "Operating Limits": [
                    ["Maximum Service Temperature", "2,000°C"],
                    ["Recommended Operating Range", "1,400-1,950°C"],
                    ["Thermal Shock Resistance", "ΔT 250°C"],
                    ["Maximum Heating Rate", "120°C/hour"],
                ],
                "Standard Dimensions (mm)": [
                    ["Size", "Height", "Outer Ø", "Wall", "Capacity"],
                    ["S", "180", "130", "10", "1.5 L"],
                    ["M", "260", "190", "14", "4.5 L"],
                    ["L", "360", "260", "20", "11 L"],
                ],
            },
        ),
    ]
    for title, sections in products:
        story += [_para(title, s["h2"])]
        for section_title, rows in sections.items():
            story += [_para(section_title, s["body"])]
            story += [_table(rows[0], rows[1:])]
            story += [Spacer(1, 0.1 * inch)]
        story += [PageBreak()]

    story += [_para("Testing and Certification", s["h1"])]
    story += [
        _para(
            "Each production lot is sampled and tested according to ASTM C401, C417, and C133 "
            "standard test methods. Certificates of analysis (COA) ship with every order. "
            "Lot traceability is maintained for 7 years from manufacture.",
            s["body"],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "02_crucible_specifications.pdf"),
        pagesize=LETTER,
        title="Crucible Specifications",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 3. Quality Control SOP ──────────────────────────────────────────────────
def build_quality_sop() -> None:
    s = _styles()
    story: list = [_para("Quality Control Standard Operating Procedure", s["title"]), _para(f"{COMPANY} — Quality Assurance Department", s["body"])]
    story += [Spacer(1, 0.2 * inch)]
    story += [_para("Document ID: QC-SOP-001 | Revision: 14 | Effective Date: 2025-01-15", s["note"])]

    story += [_para("1. Purpose and Scope", s["h1"])]
    story += [
        _para(
            "This SOP defines the quality control procedures for all crucibles manufactured at ForgeCore "
            "Industries' Pittsburgh facility. It covers incoming raw material inspection, in-process "
            "controls, finished-goods testing, and non-conformance handling. This procedure applies to "
            "all FC-series products.",
            s["body"],
        )
    ]

    story += [_para("2. Incoming Material Inspection", s["h1"])]
    story += [
        _para("All raw materials must pass inspection before release to production:", s["body"]),
        _para("Silicon carbide grain: certified purity ≥ 98.5% SiC, Fe₂O₃ ≤ 0.6%", s["bullet"], ),
        _para("Graphite flake: certified carbon content ≥ 99.5%, ash ≤ 0.5%", s["bullet"]),
        _para("Zircon sand: certified ZrO₂ ≥ 65%, TiO₂ ≤ 0.15%", s["bullet"]),
        _para("Clay binder: moisture content 8-12%, plasticity index ≥ 25", s["bullet"]),
        _para("Sample size: 5 kg composite per shipment; tested per ASTM C323, C324, C325", s["bullet"]),
        _para(
            "Acceptance criteria: all test results within supplier specification AND within ForgeCore "
            "internal specification. Any out-of-specification result requires QA Manager approval before "
            "material release.",
            s["body"],
        ),
    ]

    story += [_para("3. In-Process Quality Control", s["h1"])]
    story += [
        _para("Production operators must perform the following checks at the indicated frequencies:", s["body"]),
        _table(
            ["Check", "Frequency", "Method", "Acceptance"],
            [
                ["Batch weight", "Every mix", "Calibrated scale ±0.1kg", "±1% of recipe"],
                ["Moisture", "Every mix", "Moisture analyzer", "5-9%"],
                ["Mold pressure", "Every press", "Pressure gauge", "35-45 MPa"],
                ["Green density", "Every 10th piece", "Dimensional + weight", "±3% of nominal"],
                ["Kiln temperature", "Continuous", "Thermocouple + logger", "Per firing curve ±10°C"],
                ["Firing duration", "Continuous", "Timer + kiln log", "Per firing curve ±30 min"],
            ],
        ),
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("4. Finished Goods Testing", s["h1"])]
    story += [
        _para(
            "Sampling plan: ANSI/ASQ Z1.4, level II inspection, AQL 1.5 for major defects, 2.5 for minor.",
            s["body"],
        ),
        _para("Required tests per production lot (minimum):", s["body"]),
        _para("Visual inspection: 100% of finished pieces", s["bullet"]),
        _para("Dimensional check: 10 pieces per lot", s["bullet"]),
        _para("Bulk density: 3 pieces per lot (ASTM C134)", s["bullet"]),
        _para("Cold crushing strength: 1 piece per lot (ASTM C133)", s["bullet"]),
        _para("Modulus of rupture: 1 piece per lot (ASTM C133)", s["bullet"]),
        _para("Thermal cycling test: 1 piece per lot, 5 cycles to rated temperature", s["bullet"]),
    ]

    story += [PageBreak()]
    story += [_para("5. Non-Conformance Handling", s["h1"])]
    story += [
        _para(
            "Any product failing finished goods testing must be placed on QC hold with a red tag "
            "indicating lot number, defect type, and date. The QA Manager must disposition within 48 hours. "
            "Disposition options:",
            s["body"],
        ),
        _para("Rework: minor defects correctable within standard process", s["bullet"]),
        _para("Relabel: downgraded to lower-tier product if functional", s["bullet"]),
        _para("Scrap: dispose per environmental SOP ENV-002", s["bullet"]),
        _para("Return to supplier: if defect traced to incoming material", s["bullet"]),
    ]

    story += [_para("6. Records and Retention", s["h1"])]
    story += [
        _para(
            "All QC records are stored digitally in the ForgeCore QMS (qms.forgecore.example.com). "
            "Records are retained for 7 years. COAs are provided to customers with each shipment and "
            "archived in the customer portal.",
            s["body"],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "03_quality_control_sop.pdf"),
        pagesize=LETTER,
        title="Quality Control SOP",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 4. Manufacturing SOP ────────────────────────────────────────────────────
def build_manufacturing_sop() -> None:
    s = _styles()
    story: list = [_para("Crucible Manufacturing Procedure", s["title"]), _para(f"{COMPANY} — Production Department", s["body"])]
    story += [Spacer(1, 0.2 * inch)]
    story += [_para("Document ID: MFG-SOP-001 | Revision: 22 | Effective Date: 2025-03-01", s["note"])]

    story += [_para("1. Process Overview", s["h1"])]
    story += [
        _para(
            "ForgeCore crucibles are produced by either isostatic pressing (FC-45, FC-90) or "
            "slip-casting (FC-72) followed by controlled drying, high-temperature firing, and "
            "finishing operations. Total cycle time from raw material to finished goods is 12-18 days "
            "depending on product family and size.",
            s["body"],
        )
    ]

    story += [_para("2. Bill of Materials Summary", s["h1"])]
    story += [
        _table(
            ["Product", "Primary Material", "Binder", "Additives"],
            [
                ["FC-45", "Silicon carbide 75-85%", "Clay + lignin", "Si powder 5%"],
                ["FC-50", "Graphite flake 80-90%", "Pitch + resin", "Boron carbide 3%"],
                ["FC-72", "Clay + graphite 60/40", "Water + deflocculant", "Grog 10%"],
                ["FC-90", "Zircon sand 80-90%", "Clay + organic binder", "Stabiliser 2%"],
            ],
        )
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("3. Mixing Procedure", s["h1"])]
    story += [
        _para(
            "Raw materials are weighed per the batch recipe (typically 250-500 kg per batch) and "
            "loaded into a high-shear Eirich mixer. Dry mixing proceeds for 5 minutes, followed by "
            "gradual addition of binder solution over 3 minutes, then wet mixing for 12-15 minutes. "
            "Mix temperature must be maintained between 18-25°C throughout.",
            s["body"],
        ),
        _para("Critical control points:", s["body"]),
        _para("Mix homogeneity verified by torque curve analysis", s["bullet"]),
        _para("Moisture content must be within ±0.5% of target before discharge", s["bullet"]),
        _para("Discharge temperature must not exceed 35°C", s["bullet"]),
    ]

    story += [_para("4. Forming", s["h1"])]
    story += [
        _para(
            "FC-45 and FC-90 are formed by cold isostatic pressing at 35-45 MPa. The rubber mould is "
            "filled with batch material, sealed, and subjected to high-pressure water in a CIP chamber. "
            "Pressing cycle: 90 seconds hold at peak pressure, 30-second depressurisation.",
            s["body"],
        ),
        _para(
            "FC-72 is formed by slip casting into plaster moulds. Slip viscosity is controlled at "
            "800-1200 cP using a Brookfield viscometer at 100 rpm. Mould residence time is 6-8 hours "
            "for standard sizes, up to 14 hours for XL sizes. Cast pieces are trimmed after 4 hours "
            "of controlled drying.",
            s["body"],
        ),
    ]

    story += [_para("5. Drying", s["h1"])]
    story += [
        _para(
            "Formed pieces enter controlled drying chambers with the following profile:",
            s["body"],
        ),
        _para("Stage 1 — 25°C, 80% RH, 24 hours (prevention of skin formation)", s["bullet"]),
        _para("Stage 2 — 40°C, 60% RH, 48 hours (bulk moisture removal)", s["bullet"]),
        _para("Stage 3 — 80°C, 30% RH, 24 hours (residual moisture)", s["bullet"]),
        _para("Final moisture content target: <0.5%", s["bullet"]),
    ]

    story += [PageBreak()]
    story += [_para("6. Firing", s["h1"])]
    story += [
        _para(
            "Dried pieces are loaded into gas-fired shuttle kilns with carefully controlled temperature "
            "profiles. Maximum firing temperatures by product:",
            s["body"],
        ),
        _table(
            ["Product", "Pre-heat", "Body Rise", "Peak", "Hold", "Cool"],
            [
                ["FC-45", "RT→200°C in 6h", "200→1300°C in 10h", "1,350°C", "2h", "Natural to 200°C"],
                ["FC-50", "RT→300°C in 8h", "300→1500°C in 12h", "1,550°C", "3h", "Natural to 300°C"],
                ["FC-72", "RT→200°C in 5h", "200→1100°C in 9h", "1,150°C", "2h", "Natural to 150°C"],
                ["FC-90", "RT→200°C in 6h", "200→1400°C in 11h", "1,450°C", "3h", "Natural to 200°C"],
            ],
        )
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("7. Finishing and Inspection", s["h1"])]
    story += [
        _para(
            "After firing, each crucible is visually inspected and dimensionally verified per QC-SOP-001. "
            "Surface defects >2 mm depth or >5 mm length are grounds for rejection. Acceptable pieces "
            "are sanded, marked with lot code and size designation, packaged in foam-lined crates, and "
            "moved to finished goods inventory.",
            s["body"],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "04_manufacturing_sop.pdf"),
        pagesize=LETTER,
        title="Manufacturing SOP",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 5. Product Application Guide ────────────────────────────────────────────
def build_application_guide() -> None:
    s = _styles()
    story: list = [_para("Product Application Guide", s["title"]), _para(f"{COMPANY} — Applications Engineering", s["body"])]
    story += [Spacer(1, 0.2 * inch)]

    story += [_para("Selecting the Right Crucible for Your Application", s["h1"])]
    story += [
        _para(
            "Choosing the correct crucible material is critical to furnace life, melt quality, and "
            "operational cost. This guide walks through the decision factors and presents our "
            "recommendations for common industrial applications.",
            s["body"],
        )
    ]

    story += [_para("Decision Factors", s["h2"])]
    story += [
        _para("1. Metal or alloy being melted (chemistry compatibility)", s["bullet"]),
        _para("2. Maximum melting temperature required", s["bullet"]),
        _para("3. Furnace atmosphere (oxidising, neutral, reducing, inert)", s["bullet"]),
        _para("4. Charge weight and pour frequency", s["bullet"]),
        _para("5. Cost-per-heat vs lifespan trade-off", s["bullet"]),
    ]

    story += [_para("Application Recommendations", s["h1"])]
    apps = [
        ("Iron and Steel Melting", "FC-45", "Silicon carbide offers excellent thermal shock resistance for intermittent furnace cycles typical in iron foundries. Service life 300-500 heats under normal conditions. Recommended for batch sizes 50-500 kg."),
        ("Copper and Copper Alloy Melting", "FC-50", "High-purity graphite is the industry standard for copper melting due to non-wetting behaviour and minimal carbon pickup. Use under protective atmosphere when melt exceeds 1,200°C."),
        ("Aluminium Die-Casting Foundries", "FC-72", "Clay-graphite composite is the most economical choice for high-volume aluminium operations. Avoid in furnaces exceeding 1,300°C — consider FC-45 for higher temperatures."),
        ("Precious Metals (Gold, Silver, Platinum)", "FC-90", "Zircon's chemical inertness minimises metal loss and contamination. Essential for high-purity alloys and jewellery-grade melts. Higher cost is justified by metal value preservation."),
        ("Zinc and Zinc Alloys", "FC-72", "Lower operating temperatures of zinc allow the economical clay-graphite composite. Service life commonly exceeds 1,000 heats."),
        ("Magnesium Allting", "FC-90", "Zircon crucibles with protective flux coating are mandatory for magnesium due to high reactivity. Special handling required — see Safety Guidelines document."),
        ("Laboratory and R&D Use", "FC-AX", "Alumina ceramic crucibles provide the highest purity environment for analytical and research applications. Limited to non-ferrous, non-reactive metals."),
    ]
    for app, rec, note in apps:
        story += [_para(app, s["h2"])]
        story += [_para(f"<b>Recommended product:</b> {rec}", s["body"])]
        story += [_para(note, s["body"])]

    story += [PageBreak()]
    story += [_para("Common Application Mistakes", s["h1"])]
    story += [
        _para(
            "Avoid these frequent errors that significantly reduce crucible life:",
            s["body"],
        ),
        _para("Exceeding rated maximum temperature (even by 50°C halves lifespan)", s["bullet"]),
        _para("Charging cold metal into a hot crucible without pre-warming the charge", s["bullet"]),
        _para("Using inappropriate tongs or handling equipment that damages crucible walls", s["bullet"]),
        _para("Mixing crucible materials in the same furnace (carbon pickup in oxide crucibles)", s["bullet"]),
        _para("Inadequate pre-heating on initial use (follow the staged heating procedure)", s["bullet"]),
    ]

    story += [_para("Pre-Heating Procedure (All Crucibles)", s["h1"])]
    story += [
        _para(
            "Before first use and after any extended storage period, all crucibles must be conditioned "
            "by a controlled pre-heat to remove residual moisture and stress-relieve the structure:",
            s["body"],
        ),
        _para("Load crucible into cold furnace", s["bullet"]),
        _para("Heat at 50°C/hour to 200°C, hold 2 hours", s["bullet"]),
        _para("Heat at 100°C/hour to 600°C, hold 1 hour", s["bullet"]),
        _para("Continue to operating temperature at 150°C/hour", s["bullet"]),
        _para(
            "Total conditioning time: 8-12 hours. Failure to condition results in thermal shock "
            "cracking on first heat-up.",
            s["body"],
        ),
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "05_product_application_guide.pdf"),
        pagesize=LETTER,
        title="Product Application Guide",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 6. Customer FAQ ─────────────────────────────────────────────────────────
def build_faq() -> None:
    s = _styles()
    story: list = [_para("Customer FAQ", s["title"]), _para(f"{COMPANY} — Customer Success", s["body"])]
    story += [Spacer(1, 0.2 * inch)]
    story += [_para("Frequently Asked Questions", s["h1"])]
    story += [
        _para(
            "Common questions from our customers. If you don't see your question here, contact our "
            "support team at support@forgecore.example.com.",
            s["body"],
        )
    ]

    faqs = [
        ("What is the typical lead time for standard crucibles?", "Standard sizes of FC-45, FC-50, FC-72, and FC-90 ship within 5 business days from order confirmation. Custom dimensions require 4-6 weeks. International orders add 2-3 weeks for shipping."),
        ("Do you offer trial samples?", "Yes. We provide free sample crucibles (one per product family) for evaluation. Customers pay only shipping. Contact your regional sales representative to arrange a sample shipment."),
        ("What is the warranty period?", "All ForgeCore crucibles carry a 12-month limited warranty against manufacturing defects. The warranty does not cover damage from improper use, exceeding rated temperatures, or thermal shock from incorrect conditioning."),
        ("Can you test a competitor's failed crucible?", "Yes. Our applications lab provides complimentary failure analysis on any crucible, including competitor products. Submit a failed piece through your sales rep; we deliver a written report within 10 business days."),
        ("Do you provide installation and training?", "On-site installation supervision and operator training are available for large orders (typically >500 units). Charges apply for travel and accommodation. Remote training via video conference is available at no charge."),
        ("What are your minimum order quantities?", "Standard products have no MOQ. Custom sizes: 25 units for FC-45 and FC-50; 50 units for FC-72; 10 units for FC-90. Trial orders below MOQ may be possible with a setup fee."),
        ("How do I dispose of a failed crucible?", "Failed silicon carbide, clay-graphite, and zircon crucibles are non-hazardous industrial waste. Recycle through a refractory waste handler. Graphite crucibles (FC-50) may contain residual metals and should be tested for TCLP leaching before disposal. See Waste Disposal SOP ENV-002."),
        ("Are your products certified for international markets?", "Yes. FC-series products carry CE marking (EU), UKCA marking (UK), and comply with REACH, RoHS, and OSHA standards. Country-specific certifications available on request (e.g., CCC for China, INMETRO for Brazil)."),
        ("Can I get a custom formulation?", "Yes. Our R&D team develops custom compositions for specialised applications. Typical development cycle is 8-12 weeks from specification to sample delivery. Custom development requires a development agreement and NRE charge."),
        ("What if a crucible fails prematurely?", "Document the failure with photos and lot number, then contact customer support within 30 days. We investigate every premature failure claim and provide credit or replacement if the failure is determined to be manufacturing-related."),
        ("Do you publish MSDS for your products?", "Yes. Material Safety Data Sheets are available for download at msds.forgecore.example.com. MSDS cover composition, handling, storage, and emergency procedures."),
        ("What packaging do you use for international shipments?", "International orders ship in ISPM-15 compliant wooden crates with foam cushioning and silica gel desiccant. All paperwork (commercial invoice, packing list, certificate of origin) is included inside a waterproof pouch attached to the crate exterior."),
    ]
    for q, a in faqs:
        story += [_para(f"Q: {q}", s["h2"])]
        story += [_para(f"A: {a}", s["body"])]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "06_customer_faq.pdf"),
        pagesize=LETTER,
        title="Customer FAQ",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 7. Warranty Policy ──────────────────────────────────────────────────────
def build_warranty() -> None:
    s = _styles()
    story: list = [_para("Warranty Policy", s["title"]), _para(f"{COMPANY}", s["body"])]
    story += [Spacer(1, 0.2 * inch)]
    story += [_para("Document ID: WTY-POL-001 | Effective Date: 2025-01-01", s["note"])]

    story += [_para("1. Coverage", s["h1"])]
    story += [
        _para(
            "ForgeCore Industries warrants that all FC-series crucibles will be free from manufacturing "
            "defects in materials and workmanship for a period of 12 months from the date of shipment. "
            "If a product is found to be defective within this period, ForgeCore will, at its option:",
            s["body"],
        ),
        _para("Replace the defective product at no charge", s["bullet"]),
        _para("Issue credit for the original purchase price", s["bullet"]),
        _para("Refund the original purchase price in full", s["bullet"]),
    ]

    story += [_para("2. Exclusions", s["h1"])]
    story += [
        _para("This warranty does not cover damage resulting from:", s["body"]),
        _para("Operation beyond rated temperature limits", s["bullet"]),
        _para("Improper pre-heating or thermal shock during conditioning", s["bullet"]),
        _para("Mechanical damage from inappropriate handling equipment", s["bullet"]),
        _para("Use with incompatible metals or alloys", s["bullet"]),
        _para("Operation in atmospheres outside product specifications", s["bullet"]),
        _para("Failure to follow published operating procedures", s["bullet"]),
        _para("Normal wear and tear at end of expected service life", s["bullet"]),
        _para("Acts of nature, fire, flood, or other events beyond ForgeCore's control", s["bullet"]),
    ]

    story += [_para("3. Claim Procedure", s["h1"])]
    story += [
        _para(
            "All warranty claims must be submitted within 30 days of defect discovery. Claims require:",
            s["body"],
        ),
        _para("Original purchase order number or invoice", s["bullet"]),
        _para("Lot number printed on the failed product", s["bullet"]),
        _para("Photographs of the defect", s["bullet"]),
        _para("Written description of operating conditions", s["bullet"]),
        _para(
            "Submit claims to warranty@forgecore.example.com. ForgeCore will respond within 5 business "
            "days with a claim number and disposition timeline.",
            s["body"],
        ),
    ]

    story += [_para("4. Limitation of Liability", s["h1"])]
    story += [
        _para(
            "ForgeCore's liability under this warranty is limited to the replacement value of the "
            "defective product. ForgeCore is not liable for incidental, consequential, or indirect "
            "damages including lost production, lost profits, or damage to other equipment. This "
            "warranty is in lieu of all other warranties, express or implied, including warranties "
            "of merchantability and fitness for a particular purpose.",
            s["body"],
        )
    ]

    story += [_para("5. Governing Law", s["h1"])]
    story += [
        _para(
            "This warranty is governed by the laws of the Commonwealth of Pennsylvania, USA. Any "
            "disputes will be resolved in the state or federal courts located in Allegheny County, PA.",
            s["body"],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "07_warranty_policy.pdf"),
        pagesize=LETTER,
        title="Warranty Policy",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 8. Export Documentation ─────────────────────────────────────────────────
def build_export_docs() -> None:
    s = _styles()
    story: list = [_para("Export Documentation Guide", s["title"]), _para(f"{COMPANY} — Logistics Department", s["body"])]
    story += [Spacer(1, 0.2 * inch)]

    story += [_para("International Shipments — Required Documentation", s["h1"])]
    story += [
        _para(
            "ForgeCore ships to over 40 countries. This guide documents the standard export paperwork "
            "included with every international order. Customers are responsible for any import duties, "
            "taxes, and country-specific clearance requirements in the destination country.",
            s["body"],
        )
    ]

    story += [_para("1. Standard Document Set", s["h1"])]
    story += [
        _table(
            ["Document", "Description", "Included"],
            [
                ["Commercial Invoice", "Value, terms, parties", "Always"],
                ["Packing List", "Item-level detail, weights, dimensions", "Always"],
                ["Certificate of Origin", "Country of manufacture attestation", "Always"],
                ["Bill of Lading / Airway Bill", "Carrier transport document", "Always"],
                ["Certificate of Analysis (COA)", "Per-lot test results", "Always"],
                ["MSDS / SDS", "Material safety data", "On request"],
                ["Fumigation Certificate", "ISPM-15 compliance", "Wooden crate shipments"],
                ["Insurance Certificate", "Cargo insurance coverage", "On request"],
            ],
        )
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("2. Incoterms", s["h1"])]
    story += [
        _para("ForgeCore supports the following Incoterms 2020:", s["body"]),
        _para("EXW (Ex Works) — Customer takes responsibility at our dock", s["bullet"]),
        _para("FCA (Free Carrier) — ForgeCore delivers to named carrier", s["bullet"]),
        _para("FOB (Free On Board) — ForgeCore delivers to vessel at named port", s["bullet"]),
        _para("CIF (Cost, Insurance, Freight) — ForgeCore arranges shipping to named port", s["bullet"]),
        _para("DDP (Delivered Duty Paid) — ForgeCore handles all import clearance", s["bullet"], ),
    ]

    story += [_para("3. Restricted Destinations", s["h1"])]
    story += [
        _para(
            "Due to export control regulations (US EAR, EU Dual-Use), ForgeCore cannot ship to certain "
            "destinations without prior approval. Contact our export compliance team at "
            "export@forgecore.example.com before placing orders for:",
            s["body"],
        ),
        _para("Countries under US sanctions (Cuba, Iran, North Korea, Syria, Crimea region)", s["bullet"]),
        _para("Customers requiring end-use in nuclear, missile, or chemical-weapon applications", s["bullet"]),
        _para("Military end-use without US State Department approval", s["bullet"]),
    ]

    story += [PageBreak()]
    story += [_para("4. HazMat Classification", s["h1"])]
    story += [
        _para(
            "FC-series crucibles are classified as non-hazardous for transport per IATA, IMDG, and "
            "ADR regulations. No dangerous goods surcharge applies. However, FC-50 graphite crucibles "
            "may be subject to special provisions if shipped by air in large quantities (over 100 kg "
            "per package) due to dust inhalation risk during handling.",
            s["body"],
        )
    ]

    story += [_para("5. Packaging Standards", s["h1"])]
    story += [
        _para("Standard export packaging:", s["body"]),
        _para("Wooden crate, ISPM-15 compliant, heat-treated and stamped", s["bullet"]),
        _para("Closed-cell foam cushioning (minimum 50 mm on all sides)", s["bullet"]),
        _para("Silica gel desiccant packs (200g per cubic foot of crate volume)", s["bullet"]),
        _para("Vapour barrier polyethylene liner", s["bullet"]),
        _para("Waterproof document pouch attached to crate exterior", s["bullet"]),
        _para(
            "Crate dimensions optimised for 20' and 40' container loading. A standard 40' container "
            "holds approximately 1,200 small crucibles or 300 large crucibles.",
            s["body"],
        )
    ]

    story += [_para("6. Typical Transit Times", s["h1"])]
    story += [
        _table(
            ["Region", "Sea (days)", "Air (days)"],
            [
                ["North America", "5-10", "2-3"],
                ["Europe", "18-25", "3-4"],
                ["South America", "20-30", "4-5"],
                ["Middle East", "25-35", "4-5"],
                ["Asia-Pacific", "28-40", "5-7"],
                ["Africa", "30-45", "5-8"],
            ],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "08_export_documentation.pdf"),
        pagesize=LETTER,
        title="Export Documentation Guide",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 9. Safety Guidelines ────────────────────────────────────────────────────
def build_safety() -> None:
    s = _styles()
    story: list = [_para("Safety Guidelines", s["title"]), _para(f"{COMPANY} — Environment, Health & Safety", s["body"])]
    story += [Spacer(1, 0.2 * inch)]
    story += [_para("Document ID: EHS-SOP-001 | Revision: 18 | Effective Date: 2025-02-01", s["note"])]

    story += [_para("1. Scope", s["h1"])]
    story += [
        _para(
            "These guidelines cover safe handling, storage, and use of ForgeCore crucible products. "
            "Compliance with these guidelines is mandatory for all personnel handling our products. "
            "Site-specific safety plans must incorporate these requirements and may add additional "
            "controls based on local hazard assessments.",
            s["body"],
        )
    ]

    story += [_para("2. Personal Protective Equipment (PPE)", s["h1"])]
    story += [
        _para("Required PPE for crucible handling:", s["body"]),
        _para("Heat-resistant gloves rated to 250°C minimum (leather or aluminised)", s["bullet"]),
        _para("Safety glasses with side shields (ANSI Z87.1)", s["bullet"]),
        _para("Face shield for pour operations (additional to safety glasses)", s["bullet"]),
        _para("Long-sleeved flame-resistant clothing (Nomex or equivalent)", s["bullet"]),
        _para("Safety footwear with metatarsal protection", s["bullet"]),
        _para("Respiratory protection (N95 minimum) when handling dry powder materials", s["bullet"]),
    ]

    story += [_para("3. Material-Specific Hazards", s["h1"])]
    story += [
        _table(
            ["Product", "Primary Hazard", "Control"],
            [
                ["FC-45 (SiC)", "Dust inhalation during machining", "Wet cutting, local exhaust, P100 respirator"],
                ["FC-50 (Graphite)", "Dust ignition above 500°C in air", "Inert atmosphere during pre-heat"],
                ["FC-72 (Clay-graphite)", "Silica dust (cristobalite risk)", "Wet handling, medical surveillance"],
                ["FC-90 (Zircon)", "Generally inert, dust nuisance", "Standard dust controls"],
            ],
        )
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("4. Storage Requirements", s["h1"])]
    story += [
        _para(
            "Crucibles must be stored in a dry, covered area protected from weather. Storage temperature "
            "should remain between 5-35°C with relative humidity below 70%. Crucibles must be stored "
            "upright on padded surfaces to prevent rim damage. Never stack crucibles inside each other. "
            "Maximum stack height: 3 crates.",
            s["body"],
        )
    ]

    story += [_para("5. Hot Handling Procedures", s["h1"])]
    story += [
        _para(
            "Crucibles removed from furnaces at operating temperature present severe burn and thermal "
            "shock risks. Use only ForgeCore-approved tongs and lift fixtures rated for the crucible "
            "weight plus a 50% safety margin. Allow hot crucibles to cool on a refractory surface for a "
            "minimum of 4 hours before any further handling.",
            s["body"],
        )
    ]

    story += [PageBreak()]
    story += [_para("6. Emergency Response", s["h1"])]
    story += [
        _para("Burns:", s["h2"]),
        _para("Immediate cooling with clean running water for 20 minutes minimum", s["bullet"]),
        _para("Do not apply ice directly; do not break blisters", s["bullet"]),
        _para("Seek medical attention for any burn larger than a 50-paisa coin or on hands/face/joints", s["bullet"]),
        _para("Inhalation of dust:", s["h2"]),
        _para("Move affected person to fresh air immediately", s["bullet"]),
        _para("Administer oxygen if breathing is difficult", s["bullet"]),
        _para("Seek medical attention if symptoms persist beyond 30 minutes", s["bullet"]),
        _para("Crucible failure during pour:", s["h2"]),
        _para("Evacuate area within 5 metres radius", s["bullet"]),
        _para("Allow molten metal to solidify before cleanup (minimum 2 hours)", s["bullet"]),
        _para("Do not use water to extinguish molten metal — risk of steam explosion", s["bullet"]),
        _para("Use dry sand or Class D fire extinguisher for metal fires", s["bullet"]),
    ]

    story += [_para("7. Training Requirements", s["h1"])]
    story += [
        _para(
            "All personnel operating crucible furnaces must complete ForgeCore's 2-day Crucible Safety "
            "and Operations course (CSO-101) before independent operation. Refresher training is required "
            "every 24 months. Records maintained in the ForgeCore Training Management System.",
            s["body"],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "09_safety_guidelines.pdf"),
        pagesize=LETTER,
        title="Safety Guidelines",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── 10. Pricing Policy ──────────────────────────────────────────────────────
def build_pricing() -> None:
    s = _styles()
    story: list = [_para("Pricing Policy", s["title"]), _para(f"{COMPANY} — Sales Operations", s["body"])]
    story += [Spacer(1, 0.2 * inch)]
    story += [_para("Document ID: SAL-POL-002 | Effective Date: 2025-04-01 | Valid through 2026-03-31", s["note"])]

    story += [_para("1. Base Pricing", s["h1"])]
    story += [
        _para(
            "All prices are quoted in US Dollars (USD), Ex Works (EXW) ForgeCore Pittsburgh, unless "
            "otherwise specified in a written quotation. Prices are subject to change with 30 days "
            "notice. Confirmed orders are honoured at the price in effect at order acceptance.",
            s["body"],
        ),
        _para("Base list prices (per unit, single-unit purchase):", s["body"]),
    ]
    story += [
        _table(
            ["Product", "Size S", "Size M", "Size L", "Size XL", "Size XXL"],
            [
                ["FC-45", "$145", "$285", "$520", "$890", "—"],
                ["FC-50", "$175", "$345", "$640", "$1,120", "$1,850"],
                ["FC-72", "$95", "$185", "$340", "—", "—"],
                ["FC-90", "$240", "$475", "$880", "—", "—"],
                ["FC-AX", "$165", "$320", "$595", "—", "—"],
            ],
        )
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("2. Volume Discounts", s["h1"])]
    story += [
        _table(
            ["Order Quantity (units)", "Discount off list"],
            [
                ["10-49", "5%"],
                ["50-99", "10%"],
                ["100-249", "15%"],
                ["250-499", "20%"],
                ["500-999", "23%"],
                ["1,000+", "Negotiated"],
            ],
        )
    ]
    story += [Spacer(1, 0.15 * inch)]

    story += [_para("3. Payment Terms", s["h1"])]
    story += [
        _para("Net 30 days from invoice date for established accounts with approved credit", s["bullet"]),
        _para("Net 15 days for new accounts (first 3 orders)", s["bullet"]),
        _para("Prepayment required for orders under $500 list value", s["bullet"]),
        _para("2% early-payment discount if paid within 10 days", s["bullet"]),
        _para("Letter of credit accepted for orders exceeding $25,000", s["bullet"]),
    ]

    story += [_para("4. Freight and Handling", s["h1"])]
    story += [
        _para(
            "Domestic US orders over $2,000 list value: freight prepaid and added to invoice. "
            "International orders: freight collect unless CIF or DDP terms are agreed. "
            "Rush manufacturing surcharge: 25% for orders requiring <2 week lead time.",
            s["body"],
        )
    ]

    story += [PageBreak()]
    story += [_para("5. Custom and Non-Standard Pricing", s["h1"])]
    story += [
        _para(
            "Custom dimensions, compositions, or quantities below standard MOQ are priced on a "
            "case-by-case basis. Custom pricing includes a one-time tooling/setup fee and a per-unit "
            "premium of 30-60% over standard pricing depending on complexity. All custom pricing is "
            "valid for 30 days from quotation.",
            s["body"],
        )
    ]

    story += [_para("6. Regional Adjustments", s["h1"])]
    story += [
        _para(
            "List prices are adjusted for regional markets to reflect local competitive conditions, "
            "currency, and distribution costs. Contact your regional sales representative for "
            "applicable pricing in your market. Regional price lists are issued semi-annually.",
            s["body"],
        )
    ]

    story += [_para("7. Price Review Process", s["h1"])]
    story += [
        _para(
            "ForgeCore reviews pricing annually in February, with new prices effective 1 April. "
            "Material cost changes (silicon carbide, graphite, zircon, energy) exceeding 5% may trigger "
            "mid-year adjustments. Customers with annual contracts receive price protection for the "
            "contract term.",
            s["body"],
        )
    ]

    SimpleDocTemplate(
        str(OUTPUT_DIR / "10_pricing_policy.pdf"),
        pagesize=LETTER,
        title="Pricing Policy",
        author=COMPANY,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    ).build(story)


# ─── Main ────────────────────────────────────────────────────────────────────
DOCUMENTS = [
    ("Product Catalogue", build_product_catalogue),
    ("Crucible Specifications", build_specifications),
    ("Quality Control SOP", build_quality_sop),
    ("Manufacturing SOP", build_manufacturing_sop),
    ("Product Application Guide", build_application_guide),
    ("Customer FAQ", build_faq),
    ("Warranty Policy", build_warranty),
    ("Export Documentation", build_export_docs),
    ("Safety Guidelines", build_safety),
    ("Pricing Policy", build_pricing),
]


def main() -> None:
    print(f"Generating ForgeCore documents into {OUTPUT_DIR}...")
    for name, builder in DOCUMENTS:
        print(f"  - {name}...")
        builder()
    print(f"\nDone! {len(DOCUMENTS)} documents created.")


if __name__ == "__main__":
    main()
