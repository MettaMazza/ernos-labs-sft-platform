#!/usr/bin/env python3
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/"experiments/external_sources/materials/magsc_001_012_v1"
def main():
 source=BASE/"nist-sc-critical-fields.pdf";target=BASE/"nist-sc-critical-fields.txt"
 if target.exists():raise SystemExit("refusing overwrite")
 pages=PdfReader(source).pages;target.write_text("\n\f\n".join((p.extract_text() or "") for p in pages));print(len(pages),target.stat().st_size)
if __name__=="__main__":main()
