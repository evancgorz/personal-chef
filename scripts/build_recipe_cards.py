"""Build polished one-page recipe cards for the current kid-friendly menu."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepInFrame,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"

NAVY = colors.HexColor("#18324B")
TEAL = colors.HexColor("#1F7A7A")
CORAL = colors.HexColor("#D96C4F")
INK = colors.HexColor("#22313F")
MUTED = colors.HexColor("#5B6B78")
PALE = colors.HexColor("#F3F7F7")
RULE = colors.HexColor("#D7E1E2")


styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "CardTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=25,
    textColor=colors.white,
    alignment=TA_LEFT,
    spaceAfter=0,
)
META = ParagraphStyle(
    "Meta",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=14,
    textColor=colors.white,
    alignment=TA_RIGHT,
)
DECK = ParagraphStyle(
    "Deck",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=12.5,
    leading=16,
    textColor=MUTED,
    spaceAfter=9,
)
SECTION = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11.5,
    leading=14,
    textColor=TEAL,
    tracking=0.8,
    spaceBefore=0,
    spaceAfter=8,
)
INGREDIENT = ParagraphStyle(
    "Ingredient",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10.6,
    leading=13.5,
    textColor=INK,
    leftIndent=0,
    firstLineIndent=0,
    spaceAfter=5,
)
STEP = ParagraphStyle(
    "Step",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=11.1,
    leading=15.8,
    textColor=INK,
    spaceAfter=10,
)
TIP = ParagraphStyle(
    "Tip",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10.8,
    leading=14,
    textColor=NAVY,
    spaceBefore=8,
    spaceAfter=0,
)
FOOTER = ParagraphStyle(
    "Footer",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=MUTED,
    alignment=TA_CENTER,
)


CARDS = [
    {
        "filename": "magic-crispy-chicken.pdf",
        "title": "Magic Crispy Chicken",
        "meta": "SERVES 6\n50 MINUTES",
        "deck": "Extra-crispy oven chicken thighs with a mellow honey-Dijon dip for dunking.",
        "equipment": "Equipment: rimmed baking sheet; wire rack; medium skillet",
        "ingredients": [
            ("CHICKEN", [
                "Boneless skinless chicken thighs - <b>2 1/4 lb</b>",
                "Large egg yolks - <b>2</b>",
                "Mayonnaise - <b>4 1/2 tbsp</b>",
                "Dijon mustard - <b>1 1/2 tbsp</b>",
                "Kosher salt - <b>2 1/4 tsp</b>",
                "Black pepper - <b>to taste</b>",
            ]),
            ("CRISPY CRUST", [
                "Avocado oil - <b>3/4 cup</b>",
                "Panko breadcrumbs - <b>3 cups</b>",
            ]),
            ("HONEY-MUSTARD DIP", [
                "Mayonnaise - <b>3/8 cup</b>",
                "Dijon mustard - <b>3/8 cup</b>",
                "Honey - <b>1 1/2 tbsp</b>",
                "Cayenne pepper - <b>pinch</b>",
                "Fresh chives, finely chopped - <b>4 1/2 tbsp</b>",
            ]),
        ],
        "steps": [
            "Heat the oven to 450 F. Set a wire rack inside a rimmed baking sheet and pat boneless skinless chicken thighs (<b>2 1/4 lb</b>) dry.",
            "Whisk large egg yolks (<b>2</b>), mayonnaise (<b>4 1/2 tbsp</b>), Dijon mustard (<b>1 1/2 tbsp</b>), kosher salt (<b>2 1/4 tsp</b>), and black pepper in a large bowl. Add the chicken and turn to coat.",
            "Heat avocado oil (<b>3/4 cup</b>) in a medium skillet over medium heat. Test it with a pinch of panko; the crumbs should bubble immediately.",
            "Add panko breadcrumbs (<b>3 cups</b>) and stir constantly for about 5 minutes, until golden. Remove from heat and cool for several minutes.",
            "Press the toasted panko onto every side of the chicken, place the pieces on the rack, and discard leftover crumbs. Bake for 15-20 minutes, until deeply golden and 165 F in the thickest part.",
            "Stir mayonnaise (<b>3/8 cup</b>), Dijon mustard (<b>3/8 cup</b>), honey (<b>1 1/2 tbsp</b>), cayenne pepper (<b>pinch</b>), black pepper, and fresh chives (<b>4 1/2 tbsp</b>) together. Rest the chicken briefly, then serve with the dip on the side.",
        ],
        "tip": "KIDDO CONTROL: Serve the honey-mustard dip separately and cut the chicken into strips after resting.",
    },
    {
        "filename": "cheeseburger-casserole.pdf",
        "title": "Cheeseburger Casserole",
        "title_font_size": 18,
        "title_leading": 21,
        "meta": "SERVES 6\n35 MINUTES",
        "deck": "A scoopable cheeseburger pasta bake with beef, tomatoes, cheddar, and pickles served your way.",
        "equipment": "Equipment: large pot; large skillet; 9 x 13-inch baking dish",
        "ingredients": [
            ("BEEF + PASTA", [
                "Lean ground beef - <b>1 1/4 lb</b>",
                "Rotini pasta, dry - <b>8 oz</b>",
            ]),
            ("SAUCE", [
                "Pre-diced onion - <b>1 1/2 cups</b>",
                "Jarred minced garlic - <b>1 tsp</b>",
                "No-salt-added diced tomatoes - <b>28 oz</b>",
                "Tomato paste - <b>1 1/2 tbsp</b>",
                "Dijon mustard - <b>3 tbsp</b>",
                "Avocado oil - <b>2 tsp</b>",
                "Kosher salt - <b>1 tsp</b>",
                "Black pepper - <b>1/2 tsp</b>",
            ]),
            ("TOPPING + SIDE", [
                "Reduced-fat cheddar cheese, shredded - <b>2 1/2 cups</b>",
                "Dill pickles, chopped - <b>1/3 cup</b>",
                "Broccoli florets - <b>12 oz</b>",
            ]),
        ],
        "steps": [
            "Heat the oven to 350 F. Lightly coat a 9 x 13-inch baking dish and set it aside.",
            "Cook rotini pasta (<b>8 oz dry</b>) in salted water until just al dente; drain well.",
            "Heat avocado oil (<b>2 tsp</b>) in a large skillet over medium-low heat. Add pre-diced onion (<b>1 1/2 cups</b>) and cook until soft, then stir in jarred minced garlic (<b>1 tsp</b>) for 30 seconds.",
            "Add lean ground beef (<b>1 1/4 lb</b>) and cook until browned. Season with kosher salt (<b>1 tsp</b>) and black pepper (<b>1/2 tsp</b>).",
            "Stir in tomato paste (<b>1 1/2 tbsp</b>), no-salt-added diced tomatoes (<b>28 oz</b>), and Dijon mustard (<b>3 tbsp</b>). Simmer for about 2 minutes, until slightly thickened.",
            "Toss the beef mixture with the rotini and spread it in the baking dish. Top with reduced-fat cheddar cheese (<b>2 1/2 cups</b>) and bake for about 15 minutes, until melted. Steam or roast broccoli florets (<b>12 oz</b>) during the bake, then offer chopped dill pickles (<b>1/3 cup</b>) on top or on the side.",
        ],
        "tip": "KIDDO CONTROL: Keep pickles separate for dipping or let the kiddo sprinkle them on top.",
    },
]


def para(text, style):
    return Paragraph(text, style)


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, 0.43 * inch, letter[0] - doc.rightMargin, 0.43 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 0.25 * inch, "PERSONAL CHEF")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.25 * inch, "RECIPE CARD")
    canvas.restoreState()


def make_card(card):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / card["filename"]
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.48 * inch,
        bottomMargin=0.58 * inch,
        title=card["title"],
        author="Personal Chef",
    )

    story = []
    title_style = TITLE
    if "title_font_size" in card:
        title_style = ParagraphStyle(
            f"{card['filename']}-title",
            parent=TITLE,
            fontSize=card["title_font_size"],
            leading=card.get("title_leading", TITLE.leading),
        )
    header = Table(
        [[para(card["title"], title_style), para(card["meta"].replace("\n", "<br/>"), META)]],
        colWidths=[4.75 * inch, 2.4 * inch],
        rowHeights=[0.95 * inch],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 15),
        ("RIGHTPADDING", (1, 0), (1, 0), 15),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(header)
    story.append(Table([[""]], colWidths=[7.15 * inch], rowHeights=[0.07 * inch], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CORAL),
    ])))
    story.append(Spacer(1, 8))
    story.append(para(card["deck"], DECK))
    story.append(para(card["equipment"], ParagraphStyle(
        "Equipment",
        parent=DECK,
        fontSize=10.5,
        leading=13,
        textColor=NAVY,
        spaceAfter=12,
    )))

    left_flow = []
    for section, items in card["ingredients"]:
        left_flow.append(para(section, SECTION))
        for item in items:
            left_flow.append(para("- " + item, INGREDIENT))

    right_flow = [para("METHOD", SECTION)]
    for index, step in enumerate(card["steps"], 1):
        right_flow.append(para(f"<b>{index}.</b> {step}", STEP))
    right_flow.append(Spacer(1, 2))
    right_flow.append(para(card["tip"], TIP))

    left = KeepInFrame(2.16 * inch, 6.85 * inch, left_flow, mode="shrink", vAlign="TOP")
    right = KeepInFrame(4.18 * inch, 6.85 * inch, right_flow, mode="shrink", vAlign="TOP")
    body = Table([[left, right]], colWidths=[2.55 * inch, 4.6 * inch], rowHeights=[7.0 * inch])
    body.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PALE),
        ("BOX", (0, 0), (-1, -1), 0.8, RULE),
        ("LINEBEFORE", (1, 0), (1, 0), 0.8, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 14),
        ("RIGHTPADDING", (0, 0), (0, 0), 12),
        ("LEFTPADDING", (1, 0), (1, 0), 16),
        ("RIGHTPADDING", (1, 0), (1, 0), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 13),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(body)
    story.append(Spacer(1, 9))
    story.append(para("Scaled for six servings. Use the quantities shown here for this card.", FOOTER))
    doc.build(story, onFirstPage=on_page)
    return path


if __name__ == "__main__":
    for card in CARDS:
        print(make_card(card))
