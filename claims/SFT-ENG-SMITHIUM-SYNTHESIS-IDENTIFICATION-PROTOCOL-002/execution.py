from pathlib import Path
from sft.engineering.novel_translation_execution_v1 import build_execution as build

def build_execution(root: Path):
    return build(root, "SFT-ENG-SMITHIUM-SYNTHESIS-IDENTIFICATION-PROTOCOL-002", Path(__file__).resolve())
