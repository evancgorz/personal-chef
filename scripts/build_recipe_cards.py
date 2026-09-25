"""Render one-page recipe-card PDFs from structured YAML sources."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, KeepInFrame, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = ROOT / "artifacts" / "recipe-cards"
DEFAULT_OUTPUT = ROOT / "output" / "pdf"

NAVY = colors.HexColor("#18324B")
TEAL = colors.HexColor("#1F7A7A")
CORAL = colors.HexColor("#D96C4F")
INK = colors.HexColor("#22313F")
MUTED = colors.HexColor("#5B6B78")
PALE = colors.HexColor("#F3F7F7")
RULE = colors.HexColor("#D7E1E2")

styles = getSampleStyleSheet()
TITLE = ParagraphStyle("CardTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=25, textColor=colors.white, alignment=TA_LEFT, spaceAfter=0)
META = ParagraphStyle("Meta", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=colors.white, alignment=TA_RIGHT)
DECK = ParagraphStyle("Deck", parent=styles["Normal"], fontName="Helvetica", fontSize=12.5, leading=16, textColor=MUTED, spaceAfter=9)
SECTION = ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=TEAL, tracking=0.8, spaceBefore=0, spaceAfter=8)
INGREDIENT = ParagraphStyle("Ingredient", parent=styles["Normal"], fontName="Helvetica", fontSize=10.6, leading=13.5, textColor=INK, leftIndent=0, firstLineIndent=0, spaceAfter=5)
STEP = ParagraphStyle("Step", parent=styles["Normal"], fontName="Helvetica", fontSize=11.1, leading=15.8, textColor=INK, spaceAfter=10)
TIP = ParagraphStyle("Tip", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10.8, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=0)
FOOTER = ParagraphStyle("Footer", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, textColor=MUTED, alignment=TA_CENTER)


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def load_card(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    card = yaml.safe_load(raw) or {}
    if card.get("version") != 1:
        raise ValueError(f"Unsupported recipe-card version in {path}")
    required = ("id", "output_filename", "title", "meta", "deck", "equipment", "ingredients", "steps", "tip")
    missing = [field for field in required if not card.get(field)]
    if missing:
        raise ValueError(f"Recipe-card source {path} lacks: {', '.join(missing)}")
    if card.get("card_format") == 2 and not 1 <= len(card["steps"]) <= 6:
        raise ValueError(f"Recipe-card source {path} must have 1 to 6 steps")
    return card, hashlib.sha256(raw).hexdigest()


def source_photo(card: dict):
    photo = card.get("source_photo")
    if not photo:
        return []
    photo_path = (ROOT / photo["path"]).resolve()
    if not photo_path.is_relative_to(ROOT) or not photo_path.is_file():
        raise ValueError(f"Missing or invalid source photo: {photo['path']}")
    image = Image(str(photo_path))
    image.drawWidth = 7.15 * inch
    image.drawHeight = image.imageHeight * image.drawWidth / image.imageWidth
    if image.drawHeight > 1.35 * inch:
        image.drawHeight = 1.35 * inch
        image.drawWidth = image.imageWidth * image.drawHeight / image.imageHeight
    credit = photo.get("credit") or photo.get("publisher") or "Source recipe photo"
    return [Spacer(1, 6), image, Spacer(1, 3), para(f"Photo: {credit}", FOOTER)]


def on_page(source_hash: str):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.6)
        canvas.line(doc.leftMargin, 0.43 * inch, letter[0] - doc.rightMargin, 0.43 * inch)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 0.25 * inch, "PERSONAL CHEF")
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.25 * inch, f"RECIPE CARD  {source_hash[:10]}")
        canvas.restoreState()

    return draw


def make_card(source_path: Path, output_dir: Path = DEFAULT_OUTPUT) -> Path:
    card, source_hash = load_card(source_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / card["output_filename"]
    doc = SimpleDocTemplate(
        str(output_path), pagesize=letter, leftMargin=0.55 * inch, rightMargin=0.55 * inch,
        topMargin=0.48 * inch, bottomMargin=0.58 * inch, title=card["title"], author="Personal Chef",
        subject=f"Source SHA256: {source_hash}", keywords=f"personal-chef,recipe-card,{card['id']},{source_hash}",
    )

    layout = card.get("layout") or {}
    title_style = TITLE
    if layout.get("title_font_size"):
        title_style = ParagraphStyle(
            f"{card['id']}-title", parent=TITLE, fontSize=layout["title_font_size"],
            leading=layout.get("title_leading", TITLE.leading),
        )

    header = Table(
        [[para(card["title"], title_style), para(card["meta"].replace("\n", "<br/>"), META)]],
        colWidths=[4.75 * inch, 2.4 * inch], rowHeights=[0.95 * inch],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 15), ("RIGHTPADDING", (1, 0), (1, 0), 15),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story = [header]
    story.append(Table([[""]], colWidths=[7.15 * inch], rowHeights=[0.07 * inch], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), CORAL)])))
    story.extend(source_photo(card))
    story.extend([
        Spacer(1, 8), para(card["deck"], DECK),
        para(card["equipment"], ParagraphStyle("Equipment", parent=DECK, fontSize=10.5, leading=13, textColor=NAVY, spaceAfter=12)),
    ])

    left_flow = []
    for section in card["ingredients"]:
        left_flow.append(para(section["section"], SECTION))
        for item in section["items"]:
            left_flow.append(para("- " + item["display"], INGREDIENT))

    right_flow = [para("METHOD", SECTION)]
    for index, step in enumerate(card["steps"], 1):
        right_flow.append(para(f"<b>{index}.</b> {step}", STEP))
    right_flow.extend([Spacer(1, 2), para(card["tip"], TIP)])

    body_height = 5.55 if card.get("source_photo") else 7.0
    left = KeepInFrame(2.16 * inch, (body_height - 0.15) * inch, left_flow, mode="shrink", vAlign="TOP")
    right = KeepInFrame(4.18 * inch, (body_height - 0.15) * inch, right_flow, mode="shrink", vAlign="TOP")
    body = Table([[left, right]], colWidths=[2.55 * inch, 4.6 * inch], rowHeights=[body_height * inch])
    body.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PALE), ("BOX", (0, 0), (-1, -1), 0.8, RULE),
        ("LINEBEFORE", (1, 0), (1, 0), 0.8, RULE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 14), ("RIGHTPADDING", (0, 0), (0, 0), 12),
        ("LEFTPADDING", (1, 0), (1, 0), 16), ("RIGHTPADDING", (1, 0), (1, 0), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 13), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.extend([body, Spacer(1, 9), para(card.get("footer", "Scaled for six servings. Use the quantities shown here for this card."), FOOTER)])
    doc.build(story, onFirstPage=on_page(source_hash))
    return output_path


def discover_sources(paths: list[str], include_legacy: bool = False) -> list[Path]:
    if paths:
        return [Path(value).resolve() for value in paths]
    sources = sorted(DEFAULT_SOURCE_ROOT.glob("**/*.yaml"))
    if include_legacy:
        return sources
    return [path for path in sources if (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("status") == "current"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", help="Recipe-card YAML sources; defaults to every source")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--include-legacy", action="store_true", help="Render migrated historical sources when no explicit paths are supplied")
    args = parser.parse_args()
    sources = discover_sources(args.sources, args.include_legacy)
    if not sources:
        raise SystemExit("No recipe-card YAML sources found")
    for source in sources:
        print(make_card(source, args.output_dir.resolve()))


if __name__ == "__main__":
    main()
