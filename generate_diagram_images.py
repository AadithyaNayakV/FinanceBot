import os
from PIL import Image, ImageDraw, ImageFont

def get_fonts():
    """Loads clean TrueType fonts from Windows fonts directory."""
    font_dir = r"C:\Windows\Fonts"
    try:
        font_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 30)
        font_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 20)
        font_card_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 22)
        font_card_bold = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 18)
        font_card_text = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 16)
        font_small = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 15)
        font_badge = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 16)
    except Exception:
        # Fallback to default
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_card_title = font_title
        font_card_bold = font_title
        font_card_text = font_title
        font_small = font_title
        font_badge = font_title
    return {
        "title": font_title,
        "sub": font_sub,
        "card_title": font_card_title,
        "card_bold": font_card_bold,
        "card_text": font_card_text,
        "small": font_small,
        "badge": font_badge
    }

def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, x1, y1, x2, y2, color, width=3, arrow_size=10):
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if y1 < y2 and x1 == x2:  # Downward
        draw.polygon([(x2 - arrow_size, y2 - arrow_size), (x2 + arrow_size, y2 - arrow_size), (x2, y2)], fill=color)
    elif y1 > y2 and x1 == x2:  # Upward
        draw.polygon([(x2 - arrow_size, y2 + arrow_size), (x2 + arrow_size, y2 + arrow_size), (x2, y2)], fill=color)
    elif x1 < x2 and y1 == y2:  # Rightward
        draw.polygon([(x2 - arrow_size, y2 - arrow_size), (x2 - arrow_size, y2 + arrow_size), (x2, y2)], fill=color)
    elif x1 > x2 and y1 == y2:  # Leftward
        draw.polygon([(x2 + arrow_size, y2 - arrow_size), (x2 + arrow_size, y2 + arrow_size), (x2, y2)], fill=color)


def generate_task_a_architecture_image(out_path):
    w, h = 1400, 720
    im = Image.new("RGBA", (w, h), (248, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    fonts = get_fonts()

    # Outer border
    draw_rounded_rect(draw, (4, 4, w - 4, h - 4), 16, fill=(248, 250, 252, 255), outline=(203, 213, 225, 255), width=2)

    # Title header banner
    draw_rounded_rect(draw, (14, 14, w - 14, 76), 10, fill=(15, 23, 42, 255))
    draw.text((w / 2, 34), "FINANCEBOT & GST COMPLIANCE PLATFORM — DUAL ENGINE ARCHITECTURE", fill=(255, 255, 255, 255), font=fonts["title"], anchor="mm")
    draw.text((w / 2, 60), "Unified End-to-End Enterprise Architecture: Multimodal AI Assistant + Deterministic Tax Audit Suite", fill=(148, 163, 184, 255), font=fonts["small"], anchor="mm")

    # End User Pill
    draw_rounded_rect(draw, (w / 2 - 120, 96, w / 2 + 120, 144), 8, fill=(30, 41, 59, 255), outline=(15, 23, 42, 255), width=2)
    draw.text((w / 2, 120), "END USER (Finance Analyst / CA / CFO)", fill=(255, 255, 255, 255), font=fonts["card_bold"], anchor="mm")

    # Connectors to Frontends
    draw.line((w / 2 - 120, 120, 360, 120), fill=(59, 130, 246, 255), width=3)
    draw_arrow(draw, 360, 120, 360, 175, color=(59, 130, 246, 255), width=3, arrow_size=10)

    draw.line((w / 2 + 120, 120, 1040, 120), fill=(16, 185, 129, 255), width=3)
    draw_arrow(draw, 1040, 120, 1040, 175, color=(16, 185, 129, 255), width=3, arrow_size=10)

    # ================= LEFT SIDE: FinanceBot AI Assistant =================
    # Frontend Card
    draw_rounded_rect(draw, (40, 175, 680, 265), 10, fill=(239, 246, 255, 255), outline=(59, 130, 246, 255), width=2)
    draw.text((60, 198), "FinanceBot Frontend (Port 5174)", fill=(30, 58, 138, 255), font=fonts["card_title"])
    draw_rounded_rect(draw, (490, 190, 660, 222), 6, fill=(59, 130, 246, 255))
    draw.text((575, 206), "React 18 + Vite", fill=(255, 255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((60, 234), "Interactive Financial Chat, Multi-page File Uploads, Document Session Inspector", fill=(71, 85, 105, 255), font=fonts["card_text"])

    draw_arrow(draw, 360, 265, 360, 310, color=(59, 130, 246, 255), width=3, arrow_size=10)

    # Backend Card
    draw_rounded_rect(draw, (40, 310, 680, 400), 10, fill=(240, 253, 250, 255), outline=(13, 148, 136, 255), width=2)
    draw.text((60, 333), "FinanceBot Async API (Port 8001)", fill=(19, 78, 74, 255), font=fonts["card_title"])
    draw_rounded_rect(draw, (500, 325, 660, 357), 6, fill=(13, 148, 136, 255))
    draw.text((580, 341), "FastAPI Core", fill=(255, 255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((60, 369), "3-Tier Priority Waterfall: Uploaded Doc -> Knowledge Base -> SerpAPI Web RAG", fill=(71, 85, 105, 255), font=fonts["card_text"])

    draw_arrow(draw, 360, 400, 360, 445, color=(13, 148, 136, 255), width=3, arrow_size=10)

    # Core Intelligence Modules Box
    draw_rounded_rect(draw, (40, 445, 680, 690), 10, fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((60, 468), "FinanceBot Core Intelligence & Data Engines", fill=(15, 23, 42, 255), font=fonts["card_bold"])

    # Pills inside Left Engine
    # Pill 1: Tier 1
    draw_rounded_rect(draw, (60, 498, 660, 546), 6, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=1)
    draw.text((80, 522), "• Tier 1: Uploaded Doc QA (pypdf text extraction + Gemini Vision OCR)", fill=(15, 23, 42, 255), font=fonts["card_text"], anchor="lm")
    # Pill 2: Tier 2
    draw_rounded_rect(draw, (60, 554, 660, 602), 6, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=1)
    draw.text((80, 578), "• Tier 2: ChromaDB Knowledge Base (all-MiniLM-L6-v2 dense embeddings)", fill=(15, 23, 42, 255), font=fonts["card_text"], anchor="lm")
    # Pill 3: Tier 3 & Cache
    draw_rounded_rect(draw, (60, 610, 660, 658), 6, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=1)
    draw.text((80, 634), "• Tier 3: SerpAPI Web Search RAG | Redis Semantic Cache (Sub-second)", fill=(15, 23, 42, 255), font=fonts["card_text"], anchor="lm")

    # ================= RIGHT SIDE: GST Invoicer Audit Suite =================
    # Frontend Card
    draw_rounded_rect(draw, (720, 175, 1360, 265), 10, fill=(236, 253, 245, 255), outline=(16, 185, 129, 255), width=2)
    draw.text((740, 198), "GST Invoicer Frontend (Port 5173)", fill=(6, 95, 70, 255), font=fonts["card_title"])
    draw_rounded_rect(draw, (1160, 190, 1340, 222), 6, fill=(16, 185, 129, 255))
    draw.text((1250, 206), "React 18 + Tailwind", fill=(255, 255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((740, 234), "Purchase Register & GSTR-2B Ingestion, Discrepancy Dashboard, Human Review Queue", fill=(71, 85, 105, 255), font=fonts["card_text"])

    draw_arrow(draw, 1040, 265, 1040, 310, color=(16, 185, 129, 255), width=3, arrow_size=10)

    # Backend Card
    draw_rounded_rect(draw, (720, 310, 1360, 400), 10, fill=(254, 242, 242, 255), outline=(239, 68, 68, 255), width=2)
    draw.text((740, 333), "GST Reconcile API (Port 8000)", fill=(153, 27, 27, 255), font=fonts["card_title"])
    draw_rounded_rect(draw, (1160, 325, 1340, 357), 6, fill=(239, 68, 68, 255))
    draw.text((1250, 341), "Python Decimal Core", fill=(255, 255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((740, 369), "Deterministic Reconciler: Vectorized Joins + Rapidfuzz Candidate Match + Gemini Classifier", fill=(71, 85, 105, 255), font=fonts["card_text"])

    draw_arrow(draw, 1040, 400, 1040, 445, color=(239, 68, 68, 255), width=3, arrow_size=10)

    # Core Reconciliation Modules Box
    draw_rounded_rect(draw, (720, 445, 1360, 690), 10, fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((740, 468), "GST Reconciliation & Audit Engines", fill=(15, 23, 42, 255), font=fonts["card_bold"])

    # Pills inside Right Engine
    # Pill 1: Aggregation & Normalization
    draw_rounded_rect(draw, (740, 498, 1340, 546), 6, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=1)
    draw.text((760, 522), "• Pre-Reconciliation Aggregation by (GSTIN, Invoice_No) & Duplicate Detection", fill=(15, 23, 42, 255), font=fonts["card_text"], anchor="lm")
    # Pill 2: Deterministic + AI Classifier
    draw_rounded_rect(draw, (740, 554, 1340, 602), 6, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=1)
    draw.text((760, 578), "• Rapidfuzz String Distance + Gemini Tax Discrepancy Classifier (JSON schema)", fill=(15, 23, 42, 255), font=fonts["card_text"], anchor="lm")
    # Pill 3: Mathematical Risk
    draw_rounded_rect(draw, (740, 610, 1340, 658), 6, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=1)
    draw.text((760, 634), "• Deterministic Python Decimal Risk Engine (Total ITC at Risk in INR)", fill=(15, 23, 42, 255), font=fonts["card_text"], anchor="lm")

    # Save image
    im.save(out_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated: {out_path}")


def generate_task_a_waterfall_image(out_path):
    w, h = 1400, 240
    im = Image.new("RGBA", (w, h), (248, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    fonts = get_fonts()

    draw_rounded_rect(draw, (4, 4, w - 4, h - 4), 12, fill=(248, 250, 252, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((w / 2, 24), "FINANCEBOT 3-TIER PRIORITY WATERFALL (STRICT RESOLUTION HIERARCHY)", fill=(15, 23, 42, 255), font=fonts["card_bold"], anchor="mm")

    y_pos = 55
    box_h = 155

    # Step 1: User Query
    draw_rounded_rect(draw, (24, y_pos, 220, y_pos + box_h), 8, fill=(15, 23, 42, 255))
    draw.text((122, y_pos + 45), "User Financial Query", fill=(255, 255, 255, 255), font=fonts["card_bold"], anchor="mm")
    draw.text((122, y_pos + 80), "/ Uploaded File", fill=(148, 163, 184, 255), font=fonts["card_text"], anchor="mm")
    draw.text((122, y_pos + 115), "[ Greeting Guard ]", fill=(52, 211, 153, 255), font=fonts["badge"], anchor="mm")

    draw_arrow(draw, 220, y_pos + box_h / 2, 260, y_pos + box_h / 2, color=(59, 130, 246, 255), width=3, arrow_size=10)

    # Step 2: Tier 1
    draw_rounded_rect(draw, (260, y_pos, 580, y_pos + box_h), 8, fill=(236, 253, 245, 255), outline=(16, 185, 129, 255), width=2)
    draw.text((420, y_pos + 30), "PRIORITY 1: Uploaded Doc", fill=(6, 95, 70, 255), font=fonts["card_bold"], anchor="mm")
    draw.text((420, y_pos + 62), "• pypdf digital text extraction", fill=(51, 65, 85, 255), font=fonts["card_text"], anchor="mm")
    draw.text((420, y_pos + 92), "• Gemini Vision OCR on Scans", fill=(51, 65, 85, 255), font=fonts["card_text"], anchor="mm")
    draw.text((420, y_pos + 125), "Found -> Return 'Uploaded Doc'", fill=(5, 150, 105, 255), font=fonts["badge"], anchor="mm")

    draw_arrow(draw, 580, y_pos + box_h / 2, 620, y_pos + box_h / 2, color=(16, 185, 129, 255), width=3, arrow_size=10)

    # Step 3: Tier 2
    draw_rounded_rect(draw, (620, y_pos, 960, y_pos + box_h), 8, fill=(240, 253, 250, 255), outline=(13, 148, 136, 255), width=2)
    draw.text((790, y_pos + 30), "PRIORITY 2: Internal KB", fill=(19, 78, 74, 255), font=fonts["card_bold"], anchor="mm")
    draw.text((790, y_pos + 62), "• ChromaDB Vector Database", fill=(51, 65, 85, 255), font=fonts["card_text"], anchor="mm")
    draw.text((790, y_pos + 92), "• HuggingFace MiniLM Embeddings", fill=(51, 65, 85, 255), font=fonts["card_text"], anchor="mm")
    draw.text((790, y_pos + 125), "Score <= 1.15 -> Return 'KB'", fill=(13, 148, 136, 255), font=fonts["badge"], anchor="mm")

    draw_arrow(draw, 960, y_pos + box_h / 2, 1000, y_pos + box_h / 2, color=(13, 148, 136, 255), width=3, arrow_size=10)

    # Step 4: Tier 3
    draw_rounded_rect(draw, (1000, y_pos, 1376, y_pos + box_h), 8, fill=(239, 246, 255, 255), outline=(59, 130, 246, 255), width=2)
    draw.text((1188, y_pos + 30), "PRIORITY 3: Live Web RAG", fill=(30, 58, 138, 255), font=fonts["card_bold"], anchor="mm")
    draw.text((1188, y_pos + 62), "• SerpAPI Google Search Query", fill=(51, 65, 85, 255), font=fonts["card_text"], anchor="mm")
    draw.text((1188, y_pos + 92), "• Live Snippet Extraction Fallback", fill=(51, 65, 85, 255), font=fonts["card_text"], anchor="mm")
    draw.text((1188, y_pos + 125), "Live Market Synthesis + Citations", fill=(37, 99, 235, 255), font=fonts["badge"], anchor="mm")

    im.save(out_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated: {out_path}")


def generate_task_b_scoping_image(out_path):
    w, h = 1400, 360
    im = Image.new("RGBA", (w, h), (248, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    fonts = get_fonts()

    draw_rounded_rect(draw, (4, 4, w - 4, h - 4), 12, fill=(248, 250, 252, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((w / 2, 24), "HYBRID ARCHITECTURAL SCOPING MODEL: DETERMINISTIC VS. MULTIMODAL AI", fill=(15, 23, 42, 255), font=fonts["card_bold"], anchor="mm")

    col_w = 660
    card_h = 280
    y_card = 55

    # Left: Deterministic Core
    draw_rounded_rect(draw, (24, y_card, 24 + col_w, y_card + card_h), 10, fill=(236, 253, 245, 255), outline=(16, 185, 129, 255), width=2)
    draw.text((24 + col_w / 2, y_card + 30), "DETERMINISTIC CORE (Tax Precision & Compliance)", fill=(6, 95, 70, 255), font=fonts["card_title"], anchor="mm")
    
    bullets_left = [
        "• Python Decimal Arithmetic: Exact rounding on statutory tax numbers.",
        "• Pre-Reconciliation Aggregation: Groups multi-line invoices by (GSTIN, Inv_No).",
        "• Duplicate Row Detection: Audits duplicate purchase ledger bookings.",
        "• Pandas Vectorized Joins & Rapidfuzz: Sub-millisecond candidate blocking.",
        "• Deterministic Isolation: Offloads math from generative LLM to Python code."
    ]
    y_b = y_card + 70
    for b in bullets_left:
        draw.text((45, y_b), b, fill=(30, 41, 59, 255), font=fonts["card_text"])
        y_b += 40

    # Right: Multimodal AI & RAG Core
    draw_rounded_rect(draw, (716, y_card, 716 + col_w, y_card + card_h), 10, fill=(239, 246, 255, 255), outline=(59, 130, 246, 255), width=2)
    draw.text((716 + col_w / 2, y_card + 30), "MULTIMODAL AI & RAG CORE (Unstructured Intelligence)", fill=(30, 58, 138, 255), font=fonts["card_title"], anchor="mm")

    bullets_right = [
        "• Google Gemini 3.5 Flash Lite: Qualitative reasoning over financial docs.",
        "• Gemini Multimodal Vision OCR: Optical perception on scanned PDFs.",
        "• 1200px Thumbnail Pipeline: 94% payload reduction for rapid OCR.",
        "• ChromaDB Vector Store: Semantic search across finance textbooks.",
        "• SerpAPI Google Search RAG: Live market data, rates & corporate filings."
    ]
    y_b = y_card + 70
    for b in bullets_right:
        draw.text((737, y_b), b, fill=(30, 41, 59, 255), font=fonts["card_text"])
        y_b += 40

    im.save(out_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated: {out_path}")


def generate_task_c_failures_image(out_path):
    w, h = 1400, 360
    im = Image.new("RGBA", (w, h), (248, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    fonts = get_fonts()

    draw_rounded_rect(draw, (4, 4, w - 4, h - 4), 12, fill=(248, 250, 252, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((w / 2, 24), "REAL ENGINEERING BREAKDOWNS, ROOT CAUSES, AND VALIDATED RESOLUTIONS", fill=(15, 23, 42, 255), font=fonts["card_bold"], anchor="mm")

    col_w = 320
    card_h = 280
    y_card = 55

    cards = [
        {
            "num": "1. Missing Redis Crashout",
            "issue": "Redis not installed/running -> socket error 10061 crashed prompt execution on boot; cp1252 emoji crash.",
            "fix": "Configured local Redis service + strict 2s socket timeout and graceful in-memory cache bypass.",
            "color": (239, 68, 68, 255)
        },
        {
            "num": "2. Duplicate Rows in GST",
            "issue": "Multi-line invoices & duplicate entries caused false MISSING_IN_2B and double-counted ITC exposure.",
            "fix": "Pre-reconciliation groupby on (GSTIN, Invoice_No) + DUPLICATE_IN_BOOKS audit detection.",
            "color": (245, 158, 11, 255)
        },
        {
            "num": "3. Scanned PDF Dropped",
            "issue": "pypdf extracted 0 characters from 15-page scanned file; bot ignored uploaded document completely.",
            "fix": "Gemini Multimodal Vision OCR pipeline with PIL JPEG thumbnail compression (94% payload cut).",
            "color": (16, 185, 129, 255)
        },
        {
            "num": "4. Currency Commas & FY",
            "issue": "float('18,450.00') crashed with ValueError; regex distorted INV/24-25/43 to 242543.",
            "fix": "Python Decimal sanitization (replace commas) + normalized sequence serial regex isolation.",
            "color": (59, 130, 246, 255)
        }
    ]

    for idx, c in enumerate(cards):
        x = 24 + idx * 340
        draw_rounded_rect(draw, (x, y_card, x + col_w, y_card + card_h), 8, fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=2)
        # Header banner
        draw_rounded_rect(draw, (x, y_card, x + col_w, y_card + 45), 8, fill=c["color"])
        draw.text((x + col_w / 2, y_card + 22), c["num"], fill=(255, 255, 255, 255), font=fonts["card_bold"], anchor="mm")

        draw.text((x + 15, y_card + 65), "WHAT FAILED / SYMPTOM:", fill=(185, 28, 28, 255), font=fonts["badge"])
        # Wrap text
        issue_lines = [
            c["issue"][:42],
            c["issue"][42:85],
            c["issue"][85:128],
            c["issue"][128:]
        ]
        y_t = y_card + 90
        for l in issue_lines:
            if l.strip():
                draw.text((x + 15, y_t), l.strip(), fill=(71, 85, 105, 255), font=fonts["small"])
                y_t += 20

        draw.text((x + 15, y_card + 180), "ENGINEERING RESOLUTION:", fill=(5, 150, 105, 255), font=fonts["badge"])
        fix_lines = [
            c["fix"][:42],
            c["fix"][42:85],
            c["fix"][85:128],
            c["fix"][128:]
        ]
        y_t = y_card + 205
        for l in fix_lines:
            if l.strip():
                draw.text((x + 15, y_t), l.strip(), fill=(15, 23, 42, 255), font=fonts["small"])
                y_t += 20

    im.save(out_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated: {out_path}")


def generate_task_a_gst_pipeline_image(out_path):
    w, h = 1400, 240
    im = Image.new("RGBA", (w, h), (248, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    fonts = get_fonts()

    draw_rounded_rect(draw, (4, 4, w - 4, h - 4), 12, fill=(248, 250, 252, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((w / 2, 24), "GST INVOICER RECONCILIATION & AUDIT PIPELINE", fill=(15, 23, 42, 255), font=fonts["card_bold"], anchor="mm")

    y_pos = 55
    box_h = 155
    step_w = 240
    spacing = 35

    steps = [
        ("1. Multi-Page Ingestion", ["• CSV & PDF multi-page", "• Decimal sanitization", "• Serial regex isolation"], (30, 58, 138, 255), (239, 246, 255, 255)),
        ("2. Group Aggregation", ["• Group by (GSTIN, Inv)", "• Aggregate tax amounts", "• Detect duplicate rows"], (6, 95, 70, 255), (236, 253, 245, 255)),
        ("3. Exact Matching", ["• Vectorized Pandas join", "• Clean deterministic pairs", "• 0 LLM cost overhead"], (13, 148, 136, 255), (240, 253, 250, 255)),
        ("4. Candidate Matching", ["• Rapidfuzz candidate search", "• Vendor string blocking", "• Fuzzy pairing queue"], (217, 119, 6, 255), (254, 243, 199, 255)),
        ("5. AI Audit & Risk", ["• Gemini tax classification", "• Discrepancy taxonomy", "• Exact ITC at Risk (INR)"], (220, 38, 38, 255), (254, 242, 242, 255))
    ]

    for idx, (title, bullets, text_col, bg_col) in enumerate(steps):
        x = 20 + idx * (step_w + spacing)
        draw_rounded_rect(draw, (x, y_pos, x + step_w, y_pos + box_h), 8, fill=bg_col, outline=text_col, width=2)
        draw.text((x + step_w / 2, y_pos + 26), title, fill=text_col, font=fonts["card_bold"], anchor="mm")
        y_b = y_pos + 55
        for b in bullets:
            draw.text((x + 12, y_b), b, fill=(51, 65, 85, 255), font=fonts["small"])
            y_b += 28
        if idx < len(steps) - 1:
            draw_arrow(draw, x + step_w, y_pos + box_h / 2, x + step_w + spacing, y_pos + box_h / 2, color=(100, 116, 139, 255), width=3, arrow_size=8)

    im.save(out_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated: {out_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "showcase_assets")
    os.makedirs(img_dir, exist_ok=True)

    generate_task_a_architecture_image(os.path.join(img_dir, "task_a_architecture.png"))
    generate_task_a_waterfall_image(os.path.join(img_dir, "task_a_waterfall.png"))
    generate_task_a_gst_pipeline_image(os.path.join(img_dir, "task_a_gst_pipeline.png"))
    generate_task_b_scoping_image(os.path.join(img_dir, "task_b_scoping.png"))
    generate_task_c_failures_image(os.path.join(img_dir, "task_c_failures.png"))
