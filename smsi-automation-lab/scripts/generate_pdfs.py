#!/usr/bin/env python3
"""
generate_pdfs.py — Génération des livrables SMSI en PDF
TechShop SAS — Portfolio GRC Automation
"""

import re
import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import Preformatted

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "livrables-pdf"

DOCUMENTS = [
    ("smsi/01-politique/politique-securite.md",            "01-politique-securite-techshop.pdf"),
    ("smsi/01-politique/charte-informatique.md",            "02-charte-informatique-techshop.pdf"),
    ("smsi/02-perimetre/declaration-perimetre.md",          "03-declaration-perimetre-smsi.pdf"),
    ("smsi/03-analyse-risques/inventaire-actifs.md",        "04-inventaire-actifs.pdf"),
    ("smsi/03-analyse-risques/registre-risques.md",         "05-registre-risques-ebios.pdf"),
    ("smsi/04-declaration-applicabilite/SoA-iso27001.md",   "06-soa-iso27001-2022.pdf"),
    ("smsi/05-plan-traitement/plan-traitement-risques.md",  "07-plan-traitement-risques.pdf"),
    ("smsi/05-plan-traitement/procedure-incidents.md",      "08-procedure-gestion-incidents.pdf"),
    ("smsi/06-controles-nis2-rgpd/nis2-article21.md",       "09-nis2-article21-mapping.pdf"),
    ("smsi/06-controles-nis2-rgpd/rgpd-conformite.md",      "10-rgpd-conformite-techshop.pdf"),
    ("smsi/07-indicateurs/kri-kpi-tableau-bord.md",         "11-kri-kpi-tableau-bord.pdf"),
    ("smsi/08-audit-interne/plan-audit-interne.md",         "12-plan-audit-interne.pdf"),
    ("smsi/09-ai-gouvernance/inventaire-systemes-ia.md",    "13-inventaire-systemes-ia.pdf"),
    ("smsi/09-ai-gouvernance/eu-ai-act-mapping.md",         "14-eu-ai-act-mapping.pdf"),
    ("smsi/09-ai-gouvernance/politique-ia.md",              "15-politique-ia-responsable.pdf"),
]

# Couleurs
INDIGO     = colors.HexColor('#4F46E5')
INDIGO_LIGHT = colors.HexColor('#EEF2FF')
GRAY_900   = colors.HexColor('#111827')
GRAY_700   = colors.HexColor('#374151')
GRAY_500   = colors.HexColor('#6B7280')
GRAY_200   = colors.HexColor('#E5E7EB')
GRAY_50    = colors.HexColor('#F9FAFB')
RED_600    = colors.HexColor('#DC2626')
CODE_BG    = colors.HexColor('#1F2937')
CODE_FG    = colors.HexColor('#F9FAFB')
QUOTE_BG   = colors.HexColor('#EEF2FF')
QUOTE_FG   = colors.HexColor('#3730A3')


def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s['h1'] = ParagraphStyle('H1',
        fontSize=18, fontName='Helvetica-Bold', textColor=GRAY_900,
        spaceAfter=12, spaceBefore=0, leading=22,
        borderPadding=(0, 0, 6, 0),
    )
    s['h2'] = ParagraphStyle('H2',
        fontSize=13, fontName='Helvetica-Bold', textColor=GRAY_700,
        spaceAfter=8, spaceBefore=18, leading=16,
        leftIndent=8, borderWidth=0, borderColor=INDIGO,
    )
    s['h3'] = ParagraphStyle('H3',
        fontSize=11, fontName='Helvetica-Bold', textColor=GRAY_700,
        spaceAfter=4, spaceBefore=12, leading=14,
    )
    s['h4'] = ParagraphStyle('H4',
        fontSize=10, fontName='Helvetica-Bold', textColor=GRAY_500,
        spaceAfter=3, spaceBefore=8, leading=13,
    )
    s['body'] = ParagraphStyle('Body',
        fontSize=9.5, fontName='Helvetica', textColor=GRAY_700,
        spaceAfter=6, spaceBefore=0, leading=14,
        alignment=TA_JUSTIFY,
    )
    s['meta'] = ParagraphStyle('Meta',
        fontSize=9, fontName='Helvetica', textColor=GRAY_500,
        spaceAfter=3, spaceBefore=0, leading=13,
    )
    s['quote'] = ParagraphStyle('Quote',
        fontSize=9.5, fontName='Helvetica-Oblique', textColor=QUOTE_FG,
        spaceAfter=6, spaceBefore=6, leading=14,
        leftIndent=12, rightIndent=12,
        backColor=QUOTE_BG,
        borderPadding=(6, 8, 6, 8),
    )
    s['code_inline'] = ParagraphStyle('CodeInline',
        fontSize=8.5, fontName='Courier', textColor=RED_600,
        spaceAfter=0,
    )
    s['li'] = ParagraphStyle('Li',
        fontSize=9.5, fontName='Helvetica', textColor=GRAY_700,
        spaceAfter=3, spaceBefore=0, leading=14,
        leftIndent=14,
    )
    return s


def cover_page(canvas, doc):
    """Page de couverture pour la première page du document."""
    canvas.saveState()
    w, h = A4

    # Bande gauche colorée
    canvas.setFillColor(INDIGO)
    canvas.rect(0, 0, 8*mm, h, fill=1, stroke=0)

    # Bande top colorée
    canvas.setFillColor(INDIGO)
    canvas.rect(0, h - 40*mm, w, 40*mm, fill=1, stroke=0)

    # Nom organisation dans la bande top
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawString(18*mm, h - 18*mm, "TechShop SAS")
    canvas.setFont('Helvetica', 10)
    canvas.drawString(18*mm, h - 27*mm, "Systeme de Management de la Securite de l'Information")

    # Badge SMSI
    canvas.setFillColor(colors.HexColor('#818CF8'))
    canvas.roundRect(w - 55*mm, h - 32*mm, 40*mm, 10*mm, 3, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawCentredString(w - 35*mm, h - 27.5*mm, "Portfolio GRC Automation")

    # Ligne de séparation
    canvas.setStrokeColor(GRAY_200)
    canvas.setLineWidth(0.5)
    canvas.line(18*mm, h - 45*mm, w - 15*mm, h - 45*mm)

    # Pied de page
    canvas.setFillColor(GRAY_50)
    canvas.rect(0, 0, w, 18*mm, fill=1, stroke=0)
    canvas.setStrokeColor(GRAY_200)
    canvas.line(18*mm, 18*mm, w - 15*mm, 18*mm)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(18*mm, 11*mm, "Dorian Poncelet — Consultant GRC")
    canvas.drawRightString(w - 15*mm, 11*mm, f"Page {doc.page}")

    canvas.restoreState()


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Bande gauche fine (pages intérieures)
    canvas.setFillColor(INDIGO)
    canvas.rect(0, 0, 3*mm, h, fill=1, stroke=0)

    # En-tête
    canvas.setStrokeColor(GRAY_200)
    canvas.setLineWidth(0.5)
    canvas.line(15*mm, h - 12*mm, w - 15*mm, h - 12*mm)
    canvas.setFont('Helvetica-Bold', 7.5)
    canvas.setFillColor(INDIGO)
    canvas.drawString(15*mm, h - 9.5*mm, "TechShop SAS")
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(43*mm, h - 9.5*mm, "— SMSI")
    canvas.drawRightString(w - 15*mm, h - 9.5*mm, "Document confidentiel")

    # Pied de page
    canvas.setFillColor(GRAY_50)
    canvas.rect(0, 0, w, 16*mm, fill=1, stroke=0)
    canvas.setStrokeColor(GRAY_200)
    canvas.line(15*mm, 16*mm, w - 15*mm, 16*mm)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(15*mm, 9*mm, "Dorian Poncelet — Consultant GRC")
    canvas.drawRightString(w - 15*mm, 9*mm, f"Page {doc.page}")

    canvas.restoreState()


def clean(text):
    """Nettoie le texte markdown pour reportlab (retire * ** ` etc.)"""
    # Gras
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italique
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Code inline
    text = re.sub(r'`(.+?)`', r'<font name="Courier" color="#DC2626">\1</font>', text)
    # Liens markdown [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Émojis problématiques -> texte
    emoji_map = {
        '✅': '[OK]', '❌': '[NON]', '⚠️': '[!]', '🔴': '[CRITIQUE]',
        '🟠': '[ELEVE]', '🟡': '[MODERE]', '🟢': '[OK]', '🔵': '[INFO]',
        '📊': '', '📋': '', '📅': '', '💰': '', '🎯': '', '🚨': '',
        'ℹ️': '', '→': '->', '←': '<-', '✓': 'OK', '✗': 'NON',
        '█': '|', '░': '.', '─': '-', '│': '|',
        '╔': '+', '╗': '+', '╚': '+', '╝': '+', '║': '|', '═': '=',
        '┌': '+', '┐': '+', '└': '+', '┘': '+', '├': '+', '┤': '+',
        '┬': '+', '┴': '+', '┼': '+',
    }
    for emoji, replacement in emoji_map.items():
        text = text.replace(emoji, replacement)
    return text


def parse_table(lines):
    """Parse un tableau markdown en liste de listes."""
    rows = []
    for line in lines:
        if re.match(r'^\s*\|[-:| ]+\|\s*$', line):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    return rows


def build_table_flowable(rows):
    if not rows:
        return None

    # Nettoyer les cellules
    data = []
    for row in rows:
        data.append([Paragraph(clean(cell), ParagraphStyle('tc',
            fontSize=8.5, fontName='Helvetica', textColor=GRAY_700, leading=12)) for cell in row])

    col_count = max(len(r) for r in data)
    page_width = A4[0] - 30*mm
    col_width = page_width / col_count

    ts = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), INDIGO),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRAY_50]),
        ('GRID',       (0, 0), (-1, -1), 0.5, GRAY_200),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])

    t = Table(data, colWidths=[col_width] * col_count, repeatRows=1)
    t.setStyle(ts)
    return t


def md_to_flowables(md_text, styles):
    flowables = []
    lines = md_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Titre H1
        if line.startswith('# ') and not line.startswith('## '):
            text = clean(line[2:].strip())
            flowables.append(Paragraph(text, styles['h1']))
            flowables.append(HRFlowable(width="100%", thickness=2, color=INDIGO, spaceAfter=8))
            i += 1

        # Titre H2
        elif line.startswith('## ') and not line.startswith('### '):
            text = clean(line[3:].strip())
            p = Paragraph(text, styles['h2'])
            flowables.append(Spacer(1, 4))
            flowables.append(p)
            i += 1

        # Titre H3
        elif line.startswith('### ') and not line.startswith('#### '):
            text = clean(line[4:].strip())
            flowables.append(Paragraph(text, styles['h3']))
            i += 1

        # Titre H4
        elif line.startswith('#### '):
            text = clean(line[5:].strip())
            flowables.append(Paragraph(text, styles['h4']))
            i += 1

        # Séparateur ---
        elif re.match(r'^---+\s*$', line):
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_200,
                                         spaceBefore=8, spaceAfter=8))
            i += 1

        # Bloc de code ```
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = '\n'.join(code_lines)
            # Nettoyer les caractères non-ASCII problématiques
            code_text = code_text.replace('→', '->').replace('←', '<-')
            code_text = re.sub(r'[^\x00-\x7F]', '?', code_text)
            flowables.append(Preformatted(code_text, ParagraphStyle('code',
                fontName='Courier', fontSize=7.5, textColor=CODE_FG,
                backColor=CODE_BG, leading=11,
                leftIndent=8, rightIndent=8,
                borderPadding=(6, 8, 6, 8),
                spaceAfter=8, spaceBefore=4,
            )))

        # Citation > ...
        elif line.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].startswith('>'):
                quote_lines.append(lines[i][2:].strip())
                i += 1
            text = ' '.join(quote_lines)
            if text:
                flowables.append(Paragraph(clean(text), styles['quote']))

        # Tableau |
        elif line.startswith('|') and '|' in line[1:]:
            table_lines = []
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1
            rows = parse_table(table_lines)
            t = build_table_flowable(rows)
            if t:
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 6))

        # Liste - ou *
        elif re.match(r'^(\s*[-*+]|\s*\d+\.)\s+', line):
            m = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)', line)
            if m:
                indent = len(m.group(1))
                text = clean(m.group(3))
                bullet = '-'
                style = ParagraphStyle('li',
                    fontSize=9.5, fontName='Helvetica', textColor=GRAY_700,
                    spaceAfter=2, leading=14,
                    leftIndent=14 + indent * 4, bulletIndent=6 + indent * 4,
                )
                flowables.append(Paragraph(f'{bullet} {text}', style))
            i += 1

        # Ligne vide
        elif line.strip() == '':
            flowables.append(Spacer(1, 4))
            i += 1

        # Paragraphe normal
        else:
            # Ligne de métadonnées (**Version :** etc.)
            if re.match(r'^\*\*[^*]+:\*\*', line):
                flowables.append(Paragraph(clean(line.strip()), styles['meta']))
            else:
                text = clean(line.strip())
                if text:
                    flowables.append(Paragraph(text, styles['body']))
            i += 1

    return flowables


def convert_doc(src_relative, output_filename):
    src_path = BASE_DIR / src_relative
    out_path = OUTPUT_DIR / output_filename

    if not src_path.exists():
        print(f"  [MANQUANT] {src_path.name}")
        return False

    with open(src_path, encoding='utf-8') as f:
        md_content = f.read()

    styles = make_styles()

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=48*mm,       # laisse de la place pour la bande top (40mm) + marge
        bottomMargin=24*mm,
        title=output_filename.replace('.pdf', '').replace('-', ' ').title(),
        author='Dorian Poncelet',
        subject='SMSI TechShop SAS',
        creator='GRC Automation Portfolio',
    )

    # Sur les pages suivantes la marge top revient à normale
    # On injecte un template de page secondaire avec marges différentes
    from reportlab.platypus import NextPageTemplate
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame

    # Reconstruire avec deux templates : cover (marge haute 48mm) + inner (15mm)
    class DualMarginDoc(BaseDocTemplate):
        def __init__(self, filename, **kw):
            super().__init__(filename, **kw)
            w, h = A4
            frame_cover = Frame(
                18*mm, 24*mm,
                w - 36*mm, h - 48*mm - 24*mm,
                id='cover'
            )
            frame_inner = Frame(
                18*mm, 24*mm,
                w - 36*mm, h - 15*mm - 24*mm,
                id='inner'
            )
            self.addPageTemplates([
                PageTemplate(id='Cover', frames=[frame_cover], onPage=cover_page),
                PageTemplate(id='Inner', frames=[frame_inner], onPage=header_footer),
            ])

    doc2 = DualMarginDoc(
        str(out_path),
        pagesize=A4,
        title=output_filename.replace('.pdf', '').replace('-', ' ').title(),
        author='Dorian Poncelet',
        subject='SMSI TechShop SAS',
    )

    flowables = [NextPageTemplate('Cover')] + md_to_flowables(md_content, styles)
    # Basculer sur le template inner après la première page
    from reportlab.platypus import FrameBreak
    # Insérer le changement de template après le premier saut de page naturel
    switch = [NextPageTemplate('Inner')]

    # On insère le switch après les métadonnées (environ 8 premiers éléments)
    insert_pos = min(8, len(flowables))
    flowables = flowables[:insert_pos] + switch + flowables[insert_pos:]

    doc2.build(flowables)

    size_kb = out_path.stat().st_size // 1024
    pages = "?"
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(str(out_path)).pages)
    except Exception:
        pass
    print(f"  [OK] {output_filename:<50} {pages:>3} pages  {size_kb:>4} Ko")
    return True


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("  Generation PDF — Livrables SMSI TechShop SAS")
    print("=" * 60 + "\n")

    success = 0
    for src, out in DOCUMENTS:
        if convert_doc(src, out):
            success += 1

    print(f"\n{success}/{len(DOCUMENTS)} PDF generes dans : {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
