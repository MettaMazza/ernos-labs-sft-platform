from pathlib import Path
from sft.openai_2026.source_validity_execution_v2 import build_execution as assemble


def build_execution(root: Path):
    return assemble(root, 'SFT-COMP-OAI26-PERMANENT-FORMULA-VALIDITY-001', Path(__file__).resolve())
