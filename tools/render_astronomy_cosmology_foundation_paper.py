#!/usr/bin/env python3
"""Render the Astronomy/Cosmology foundation manuscript to PDF."""

from __future__ import annotations

import json
from pathlib import Path
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate,Frame,PageBreak,PageTemplate,Paragraph,Spacer,Table,TableStyle
import render_platform_paper as base

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"publications/current/astronomy_cosmology/FROM_ONE_SKY_TO_COSMOS.md"
OUTPUT=ROOT/"output/pdf/from-one-sky-to-cosmos-astronomy-cosmology-foundation-paper-001-v1.0.pdf"
METADATA=ROOT/"publication/astronomy_cosmology_foundation_zenodo_metadata.json"

def cover(authorized,doi):
    title=ParagraphStyle("AstroTitle",fontName="Helvetica-Bold",fontSize=27,leading=32,textColor=base.ACCENT_DARK,alignment=TA_CENTER)
    subtitle=ParagraphStyle("AstroSubtitle",fontName="Helvetica",fontSize=13,leading=18,textColor=base.INK,alignment=TA_CENTER)
    kicker=ParagraphStyle("AstroKicker",fontName="Helvetica-Bold",fontSize=9,leading=12,textColor=base.ACCENT,alignment=TA_CENTER)
    author=ParagraphStyle("AstroAuthor",fontName="Times-Roman",fontSize=12,leading=18,textColor=base.INK,alignment=TA_CENTER)
    note=ParagraphStyle("AstroNote",fontName="Times-Roman",fontSize=9,leading=13,textColor=base.MUTED,alignment=TA_CENTER,leftIndent=18*mm,rightIndent=18*mm)
    warning=ParagraphStyle("AstroWarning",fontName="Helvetica-Bold",fontSize=9,leading=13,textColor=base.ACCENT_DARK,alignment=TA_CENTER)
    return [Spacer(1,15*mm),Paragraph("SMITHIAN FOLD THEORY - ASTRONOMY AND COSMOLOGY PAPER 001",kicker),Paragraph("From One Sky to Cosmos",title),Spacer(1,7*mm),Paragraph("An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Astronomy and Cosmology from Smithian Fold Theory",subtitle),Spacer(1,10*mm),Table([[""]],colWidths=[70*mm],rowHeights=[1.5*mm],style=TableStyle([("BACKGROUND",(0,0),(-1,-1),base.ACCENT)])),Spacer(1,10*mm),Paragraph("Ernos Labs",kicker),Paragraph("Open Source Science Platform and Knowledge Tree",author),Spacer(1,12*mm),Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com",author),Spacer(1,12*mm),Paragraph("Version 1.0.0 - current-evidence closed, extension-open foundation<br/>72 required laws - 18,432 exact candidates<br/>28 July 2026"+(f"<br/>DOI: {doi}" if doi else "")+"<br/>Paper: CC BY 4.0 - Code: Apache-2.0",note),Spacer(1,8*mm),Paragraph("PUBLISHED OPEN-ACCESS BRANCH PAPER" if authorized else "LOCAL PREPUBLICATION MANUSCRIPT - PUBLICATION NOT YET AUTHORIZED",warning)]

def main():
    meta=json.loads(METADATA.read_text()); authorized=bool(meta["publication_authorized"]); doi=str(meta.get("doi","")); OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    def page(canvas,doc):
        canvas.saveState(); width,height=A4
        if doc.page>1:
            canvas.setStrokeColor(base.RULE); canvas.setLineWidth(.4); canvas.line(18*mm,height-15*mm,width-18*mm,height-15*mm); canvas.setFont("Helvetica",7.1); canvas.setFillColor(base.MUTED); canvas.drawString(18*mm,height-11.8*mm,"FROM ONE SKY TO COSMOS - ERNOS LABS PAPER 001"); canvas.drawRightString(width-18*mm,11*mm,str(doc.page)); canvas.drawString(18*mm,11*mm,(f"Maria Smith - 2026 - CC BY 4.0 - DOI {doi}" if authorized else "Maria Smith - 2026 - CC BY 4.0 - LOCAL PREPUBLICATION"))
        canvas.restoreState()
    doc=BaseDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=21*mm,bottomMargin=18*mm,title="From One Sky to Cosmos",author="Maria Smith",subject="Smithian Fold Theory Astronomy and Cosmology foundation",creator="Ernos Labs publication renderer")
    frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id="body"); doc.addPageTemplates([PageTemplate(id="paper",frames=[frame],onPage=page)]); source=SOURCE.read_text().replace("\u2011","-").replace("\u2013","-").replace("\u2014","-"); doc.build(cover(authorized,doi)+[PageBreak()]+base.body_story(source)); print(f"rendered {OUTPUT.relative_to(ROOT)}")
if __name__=="__main__": main()
