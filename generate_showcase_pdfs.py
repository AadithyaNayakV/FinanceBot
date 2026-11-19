import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, Preformatted, Image
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_dir = r"C:\Windows\Fonts"
if os.path.exists(os.path.join(font_dir, "seguisym.ttf")):
    try:
        pdfmetrics.registerFont(TTFont("SegoeSym", os.path.join(font_dir, "seguisym.ttf")))
    except Exception:
        pass
if os.path.exists(os.path.join(font_dir, "consola.ttf")):
    try:
        pdfmetrics.registerFont(TTFont("Consolas", os.path.join(font_dir, "consola.ttf")))
    except Exception:
        pass


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(46, letter[1] - 32, "FinanceBot & GST Compliance Suite | Technical Showcase Artifact")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(46, letter[1] - 36, letter[0] - 46, letter[1] - 36)

        # Footer (all pages)
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 46, 28, footer_text)
        self.drawString(46, 28, "Candidate Showcase Assessment | Engineering Architecture & Case Study")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(46, 38, letter[0] - 46, 38)

        self.restoreState()


def get_custom_styles():
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0f172a")     # Slate 900
    c_dark_green = colors.HexColor("#065f46")  # Emerald 800
    c_text = colors.HexColor("#1e293b")        # Slate 800

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15.5,
        leading=19.5,
        textColor=c_primary,
        spaceAfter=3
    )

    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.8,
        leading=13.8,
        textColor=c_dark_green,
        spaceBefore=7,
        spaceAfter=2.5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=12.0,
        textColor=c_primary,
        spaceBefore=5.5,
        spaceAfter=2,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'DocH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.0,
        textColor=c_primary,
        spaceBefore=4,
        spaceAfter=1.5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=c_text,
        spaceAfter=2.5
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=c_text,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=1.5
    )

    callout_style = ParagraphStyle(
        'DocCallout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10.2,
        textColor=c_dark_green
    )

    code_font = 'Consolas' if 'Consolas' in pdfmetrics.getRegisteredFontNames() else 'Courier'
    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName=code_font,
        fontSize=6.5,
        leading=8.2,
        textColor=colors.HexColor("#0f172a")
    )

    code_sym_style = ParagraphStyle(
        'DocCodeSym',
        parent=styles['Normal'],
        fontName='SegoeSym' if 'SegoeSym' in pdfmetrics.getRegisteredFontNames() else code_font,
        fontSize=6.5,
        leading=8.2,
        textColor=colors.HexColor("#0f172a")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.0,
        leading=9.0,
        textColor=c_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=9.0,
        textColor=c_primary
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=9.0,
        textColor=colors.white
    )

    return {
        'title': title_style,
        'h1': h1_style,
        'h2': h2_style,
        'h3': h3_style,
        'body': body_style,
        'bullet': bullet_style,
        'callout': callout_style,
        'code': code_style,
        'code_sym': code_sym_style,
        'table_cell': table_cell_style,
        'table_cell_bold': table_cell_bold,
        'table_header': table_header_style
    }


def sanitize_text(text: str) -> str:
    """Sanitizes text, stripping unmapped Unicode glyphs that cause black dots in Type-1 fonts."""
    t = text
    # Currency
    t = t.replace("\u20b9", "INR ").replace("₹", "INR ")
    # Emojis & status symbols
    t = t.replace("⚠️", " [!] ").replace("✅", " [OK] ").replace("❌", " [X] ")
    # Unmapped Unicode arrows and bullets
    t = t.replace("→", "->").replace("←", "<-").replace("•", "- ").replace("●", "- ").replace("▪", "- ")
    t = t.replace("& ", "&amp; ")
    
    # Escape standalone XML brackets
    t = re.sub(r'<(?!/?(b|i|font|bullet)[ >])', '&lt;', t)
    
    # Markdown tags
    t = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.*?)\*', r'<i>\1</i>', t)
    t = re.sub(r'`(.*?)`', r'<font face="Courier" color="#0f172a">\1</font>', t)
    
    return t


def sanitize_code_line(line: str) -> str:
    """Ensures code lines never contain box characters or unmapped characters that render as black dots."""
    l = line
    l = l.replace("\u20b9", "INR ").replace("₹", "INR ")
    if 'SegoeSym' not in pdfmetrics.getRegisteredFontNames():
        l = l.replace("✅", "[OK]")
    l = l.replace("⚠️", "[!]").replace("❌", "[X]")
    l = l.replace("→", "->").replace("←", "<-").replace("•", "- ")
    
    # Replace Unicode box drawing characters with safe ASCII equivalents
    box_chars = {
        '┌': '+', '┐': '+', '└': '+', '┘': '+',
        '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
        '│': '|', '─': '-', '▼': 'v', '▲': '^', '►': '>', '◄': '<'
    }
    for bc, ac in box_chars.items():
        l = l.replace(bc, ac)
    return l


def is_ascii_diagram(code_lines: list) -> bool:
    """Checks if a fenced code block is an ASCII architecture diagram."""
    combined = "\n".join(code_lines)
    box_indicators = ['┌', '─', '│', '▼', '├', '└', '┬', '┴', '┼']
    return any(ind in combined for ind in box_indicators)


def parse_markdown_to_flowables(md_text: str, styles: dict, task_id: str, assets_dir: str):
    lines = md_text.splitlines()
    flowables = []
    
    i = 0
    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []

    def flush_table():
        nonlocal table_lines, in_table
        if not table_lines:
            return
        
        rows = []
        for line in table_lines:
            if re.match(r'^\s*\|?\s*:?-+:?\s*\|', line):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            rows.append(cells)
        
        if rows:
            table_data = []
            num_cols = max(len(r) for r in rows)
            
            for row_idx, r in enumerate(rows):
                row_cells = []
                while len(r) < num_cols:
                    r.append("")
                
                is_header = (row_idx == 0)
                for c in r:
                    c_clean = sanitize_text(c)
                    style_to_use = styles['table_header'] if is_header else styles['table_cell']
                    row_cells.append(Paragraph(c_clean, style_to_use))
                table_data.append(row_cells)
            
            total_avail_width = letter[0] - 92  # 520pt
            if num_cols == 2:
                col_widths = [135, 385]
            elif num_cols == 3:
                col_widths = [110, 205, 205]
            elif num_cols == 4:
                col_widths = [100, 140, 140, 140]
            else:
                col_widths = [total_avail_width / num_cols] * num_cols

            t_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            t_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#065f46")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
            ]))
            flowables.append(Spacer(1, 3))
            flowables.append(t_table)
            flowables.append(Spacer(1, 4))
            
        table_lines = []
        in_table = False

    def flush_code():
        nonlocal code_lines, in_code_block
        if not code_lines:
            return
        
        combined_txt = "\n".join(code_lines)
        
        # Skip ASCII diagram text blocks since high-resolution PNGs are embedded directly
        if is_ascii_diagram(code_lines) or "[ USER ]" in combined_txt or "Initial Approach" in combined_txt:
            code_lines = []
            in_code_block = False
            return

        # Standard code block / traceback / python snippet
        has_emoji = any('✅' in l or '\u2705' in l for l in code_lines)
        style_to_use = styles['code_sym'] if (has_emoji and 'SegoeSym' in pdfmetrics.getRegisteredFontNames()) else styles['code']

        clean_lines = [sanitize_code_line(l) for l in code_lines]
        pre = Preformatted("\n".join(clean_lines), style_to_use)
        t_box = Table([[pre]], colWidths=[letter[0] - 92])
        t_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        flowables.append(Spacer(1, 3))
        flowables.append(t_box)
        flowables.append(Spacer(1, 3))
        
        code_lines = []
        in_code_block = False

    while i < len(lines):
        line = lines[i]

        # Fenced code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                flush_code()
            else:
                if in_table:
                    flush_table()
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Tables
        if "|" in line and (line.strip().startswith("|") or line.strip().endswith("|")):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            flush_table()

        # Blockquote / Callout
        if line.startswith("> "):
            callout_text = sanitize_text(line.lstrip("> ").strip())
            p_call = Paragraph(callout_text, styles['callout'])
            t_call = Table([[p_call]], colWidths=[letter[0] - 92])
            t_call.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
                ('LINEBEFORE', (0, 0), (0, -1), 2.0, colors.HexColor("#059669")),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            flowables.append(Spacer(1, 2))
            flowables.append(t_call)
            flowables.append(Spacer(1, 2))
            i += 1
            continue

        # Horizontal Rule
        if line.strip() in ["---", "***", "___"]:
            flowables.append(Spacer(1, 1.5))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=2.5, spaceBefore=2.5))
            i += 1
            continue

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Embed Markdown images directly into PDF
        if line.strip().startswith("!["):
            match = re.search(r'\((.*?)\)', line.strip())
            if match:
                rel_img_path = match.group(1).replace('/', os.sep)
                img_full_path = os.path.join(base_dir, rel_img_path)
                if not os.path.exists(img_full_path):
                    img_full_path = os.path.join(assets_dir, os.path.basename(rel_img_path))
                if os.path.exists(img_full_path):
                    base_name = os.path.basename(img_full_path).lower()
                    if "architecture" in base_name:
                        img_h = 245
                    elif "waterfall" in base_name or "pipeline" in base_name:
                        img_h = 85
                    elif "scoping" in base_name or "failures" in base_name:
                        img_h = 130
                    else:
                        img_h = 120
                    flowables.append(Spacer(1, 4))
                    flowables.append(Image(img_full_path, width=510, height=img_h))
                    flowables.append(Spacer(1, 5))
            i += 1
            continue

        formatted_line = sanitize_text(line.strip())

        # Headings & List formatting
        if line.startswith("# "):
            flowables.append(Paragraph(formatted_line.lstrip("# "), styles['title']))
        elif line.startswith("## "):
            flowables.append(Paragraph(formatted_line.lstrip("# "), styles['h1']))
        elif line.startswith("### "):
            flowables.append(Paragraph(formatted_line.lstrip("# "), styles['h2']))
        elif line.startswith("#### "):
            flowables.append(Paragraph(formatted_line.lstrip("# "), styles['h3']))
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            # Clean en-dash bullet avoiding unmapped Unicode font glyphs
            bullet_text = "<b>&ndash;</b> " + formatted_line.lstrip("-* ").strip()
            flowables.append(Paragraph(bullet_text, styles['bullet']))
        elif re.match(r'^\d+\.\s', line.strip()):
            match = re.match(r'^(\d+\.)\s*(.*)$', line.strip())
            num_label = match.group(1)
            num_text = f"<b>{num_label}</b> " + formatted_line[len(num_label):].strip()
            flowables.append(Paragraph(num_text, styles['bullet']))
        else:
            flowables.append(Paragraph(formatted_line, styles['body']))

        i += 1

    if in_table:
        flush_table()
    if in_code_block:
        flush_code()

    return flowables


def build_pdf_from_md(md_path: str, pdf_path: str, task_id: str, assets_dir: str):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=46,
        rightMargin=46,
        topMargin=46,
        bottomMargin=46
    )

    styles = get_custom_styles()
    flowables = parse_markdown_to_flowables(md_content, styles, task_id, assets_dir)
    doc.build(flowables, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Built PDF: {pdf_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "showcase_assets")

    tasks = [
        ("Task_A_Solution_I_Built.md", "Task_A_Solution_I_Built.pdf", "A"),
        ("Task_B_Solution_Scoping.md", "Task_B_Solution_Scoping.pdf", "B"),
        ("Task_C_Fix_or_Failure.md", "Task_C_Fix_or_Failure.pdf", "C"),
    ]

    for md_file, pdf_file, tid in tasks:
        md_p = os.path.join(base_dir, md_file)
        pdf_p = os.path.join(base_dir, pdf_file)
        if os.path.exists(md_p):
            build_pdf_from_md(md_p, pdf_p, tid, assets_dir)
        else:
            print(f"[ERROR] Markdown file not found: {md_p}")
