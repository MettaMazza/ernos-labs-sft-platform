#!/usr/bin/env python3
"""Render the completed foundation branch paper to archival PDF."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate,Frame,PageBreak,PageTemplate,Paragraph,Spacer,Table,TableStyle
import render_platform_paper as base

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"publications/current/foundation/FROM_NOTHING_TO_FOLD.md"
OUTPUT=ROOT/"output/pdf/from-nothing-to-fold-foundation-branch-paper-001.pdf"

def draw_page(canvas,doc):
 canvas.saveState();w,h=A4
 if doc.page>1:
  canvas.setStrokeColor(base.RULE);canvas.setLineWidth(.4);canvas.line(20*mm,h-15*mm,w-20*mm,h-15*mm)
  canvas.setFont("Helvetica",7.5);canvas.setFillColor(base.MUTED);canvas.drawString(20*mm,h-11.8*mm,"FROM NOTHING TO FOLD - ERNOS LABS FOUNDATION BRANCH PAPER 001");canvas.drawRightString(w-20*mm,11*mm,str(doc.page));canvas.drawString(20*mm,11*mm,"Maria Smith - 2026 - CC BY 4.0 - SFT V3 clean-room reconstruction")
 canvas.restoreState()

def cover():
 title=ParagraphStyle("T",fontName="Helvetica-Bold",fontSize=29,leading=34,textColor=base.ACCENT_DARK,alignment=TA_CENTER)
 sub=ParagraphStyle("S",fontName="Helvetica",fontSize=14,leading=20,textColor=base.INK,alignment=TA_CENTER)
 kick=ParagraphStyle("K",fontName="Helvetica-Bold",fontSize=9,leading=12,textColor=base.ACCENT,alignment=TA_CENTER)
 auth=ParagraphStyle("A",fontName="Times-Roman",fontSize=12,leading=18,textColor=base.INK,alignment=TA_CENTER)
 note=ParagraphStyle("N",fontName="Times-Roman",fontSize=9,leading=13,textColor=base.MUTED,alignment=TA_CENTER,leftIndent=24*mm,rightIndent=24*mm)
 return [Spacer(1,28*mm),Paragraph("SMITHIAN FOLD THEORY - FOUNDATION BRANCH PAPER 001",kick),Paragraph("From Nothing to Fold",title),Spacer(1,8*mm),Paragraph("A Premise-Free, Parameter-Free and Machine-Closed Foundation for Smithian Fold Theory",sub),Spacer(1,12*mm),Table([[""]],colWidths=[70*mm],rowHeights=[1.5*mm],style=TableStyle([("BACKGROUND",(0,0),(-1,-1),base.ACCENT)])),Spacer(1,12*mm),Paragraph("Ernos Labs",kick),Paragraph("Open Source Science Platform and Knowledge Tree",auth),Spacer(1,18*mm),Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com",auth),Spacer(1,20*mm),Paragraph("Third clean-room reconstruction - Foundation current-knowledge inventory complete<br/>Ten admitted derivations - 2,450 generated candidate classes<br/>Version 1.0 - 23 July 2026<br/>Paper: CC BY 4.0 - Code: Apache-2.0",note)]

def main():
 OUTPUT.parent.mkdir(parents=True,exist_ok=True);source=SOURCE.read_text(encoding="utf-8")
 doc=BaseDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=21*mm,bottomMargin=18*mm,title="From Nothing to Fold",author="Maria Smith",subject="Completed Smithian Fold Theory foundation branch",creator="Ernos Labs publication renderer")
 frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id="body");doc.addPageTemplates([PageTemplate(id="paper",frames=[frame],onPage=draw_page)]);doc.build(cover()+[PageBreak()]+base.body_story(source));print(f"rendered {OUTPUT}")
if __name__=="__main__":main()
