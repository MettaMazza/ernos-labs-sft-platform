from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from sft.engine_seal import ENGINE_SEAL_ID, verify_engine_seal


ROOT = Path(__file__).resolve().parents[1]


class EngineSealTests(unittest.TestCase):
    def _sealed_copy(self, temporary: str) -> Path:
        root = Path(temporary)
        (root / "sft").mkdir(parents=True)
        (root / "governance").mkdir(parents=True)
        shutil.copytree(ROOT / "sft" / "engine", root / "sft" / "engine")
        shutil.copy2(ROOT / "sft" / "__init__.py", root / "sft" / "__init__.py")
        shutil.copy2(ROOT / "sft" / "engine_seal.py", root / "sft" / "engine_seal.py")
        shutil.copy2(
            ROOT / "governance" / "engine_seal_v1.json",
            root / "governance" / "engine_seal_v1.json",
        )
        return root

    def test_current_runtime_tree_matches_canonical_seal(self) -> None:
        result = verify_engine_seal(ROOT)
        self.assertEqual(result.status, "VALID_CANONICAL_ENGINE")
        self.assertEqual(result.seal_id, ENGINE_SEAL_ID)
        self.assertEqual(result.verified_file_count, 16)
        self.assertEqual(result.violations, ())

    def test_changed_engine_byte_is_void_and_halted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._sealed_copy(temporary)
            path = root / "sft" / "engine" / "engine.py"
            path.write_bytes(path.read_bytes() + b"\n# unauthorized change\n")
            result = verify_engine_seal(root)
            self.assertEqual(result.status, "VOID_INVALID_HALTED")
            self.assertTrue(any("engine.py" in row and "changed" in row for row in result.violations))

    def test_added_removed_and_symlinked_engine_files_are_void(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._sealed_copy(temporary)
            (root / "sft" / "engine" / "extra.py").write_text("pass\n", encoding="utf-8")
            (root / "sft" / "engine" / "errors.py").unlink()
            try:
                (root / "sft" / "engine" / "alias.py").symlink_to("canonical.py")
            except OSError:
                pass
            result = verify_engine_seal(root)
            self.assertEqual(result.status, "VOID_INVALID_HALTED")
            joined = "\n".join(result.violations)
            self.assertIn("unexpected engine file is present: sft/engine/extra.py", joined)
            self.assertIn("canonical engine file is missing: sft/engine/errors.py", joined)

    def test_edited_manifest_cannot_ratify_an_edited_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._sealed_copy(temporary)
            path = root / "governance" / "engine_seal_v1.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["empirical_strength_commitments"] = ["weakened"]
            path.write_text(json.dumps(manifest), encoding="utf-8")
            result = verify_engine_seal(root)
            self.assertEqual(result.status, "VOID_INVALID_HALTED")
            self.assertIn(
                "seal manifest contents do not match the canonical seal identity",
                result.violations,
            )

    def test_package_import_halts_before_tampered_engine_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._sealed_copy(temporary)
            path = root / "sft" / "engine" / "engine.py"
            path.write_bytes(path.read_bytes() + b"\n# unauthorized change\n")
            completed = subprocess.run(
                (sys.executable, "-c", "import sft.engine"),
                cwd=root,
                env={"PYTHONPATH": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("VOID / INVALID / HALTED", completed.stderr)

    def test_standalone_command_emits_canonical_identity(self) -> None:
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools" / "verify_engine_seal.py"), "--json"),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "VALID_CANONICAL_ENGINE")
        self.assertEqual(payload["seal_id"], ENGINE_SEAL_ID)


if __name__ == "__main__":
    unittest.main()
