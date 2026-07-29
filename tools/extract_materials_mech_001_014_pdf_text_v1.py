#!/usr/bin/env python3
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/"experiments/external_sources/materials/mech_001_014_v1"
def main():
 for name in ("nist-failure-property-tests","nist-lubrication-handbook"):
  source=BASE/f"{name}.pdf";target=BASE/f"{name}.txt"
  if target.exists(): raise SystemExit("refusing overwrite")
  pages=PdfReader(source).pages;target.write_text("\n\f\n".join((p.extract_text() or "") for p in pages));print(name,len(pages),target.stat().st_size)
if __name__=="__main__":main()
