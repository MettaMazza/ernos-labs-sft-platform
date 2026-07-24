from pathlib import Path

from sft.physics.sector_inventory_execution_v1 import build_execution as build_sector_execution


def build_execution(root: Path):
    return build_sector_execution(root, Path(__file__))
