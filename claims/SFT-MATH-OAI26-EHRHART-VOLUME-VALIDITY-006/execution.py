from pathlib import Path
from sft.openai_2026.source_validity_execution_v2 import build_execution as assemble


def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-OAI26-EHRHART-VOLUME-VALIDITY-006', Path(__file__).resolve())
