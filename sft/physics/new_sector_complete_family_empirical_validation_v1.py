"""Direct-source reconstruction and sealed custody for Claim 095."""

from dataclasses import replace
from html import unescape
import json
from pathlib import Path

from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.dark_smithion_lfv_validation_v1 import authoritative_record as dark_record, exact_analysis as dark_analysis
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator
from sft.physics.new_sector_complete_family_empirical_v1 import PREREGISTRATION_HASH, PREREGISTRATION_PATH, SOURCE_FILES, SOURCE_HASH, SOURCE_PATH, SPEC
from sft.physics.sector_inventory_validation_v1 import anchor_record


def normalized_html(path: Path) -> str:
    return " ".join(unescape(path.read_text(encoding="utf-8", errors="replace")).split()).lower()


class NewSectorCompleteFamilyMeasurementValidator(BlindExternalMeasurementValidator):
    def __init__(self, root: Path):
        super().__init__(root, SPEC)

    def direct_source_certificate(self) -> dict[str, object]:
        root = self.root
        if hash_file(root / SOURCE_PATH) != SOURCE_HASH:
            raise ValueError("new-sector source record differs from its bound identity")
        if hash_file(root / PREREGISTRATION_PATH) != PREREGISTRATION_HASH:
            raise ValueError("new-sector preregistration differs from its frozen identity")
        for path, expected in SOURCE_FILES:
            if hash_file(root / path) != expected:
                raise ValueError(f"new-sector source differs: {path}")
        record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
        force = anchor_record(root)
        dark = dark_record(root)
        dark_checks = dark_analysis(dark)
        summary = normalized_html(root / SOURCE_FILES[3][0])
        searches = normalized_html(root / SOURCE_FILES[4][0])
        atlas = normalized_html(root / SOURCE_FILES[5][0])
        checks = {
            "five_source_identities_retained": len(record["sources"]) == 5,
            "all_classifications_retained": len({row["classification"] for row in record["sources"]}) == 5,
            "known_sector_anchors_and_predictions_retained": force["anchors_pass"] and force["standing_predictions_retained"],
            "known_particle_categories_retained": all(token in summary for token in ("gauge & higgs bosons", "leptons (e, mu, tau, ... neutrinos ...)", "quarks (u, d, s, c, b, t")),
            "outside_list_search_categories_retained": all(token in searches for token in ("supersymmetry: experiment", "axions and other similar particles", "heavy neutral leptons, searches for", "supersymmetric particle searches")),
            "atlas_confining_dark_jet_classes_retained": all(token in atlas for token in ("semi-visible jets", "emerging jets", "missing transverse momentum", "dark quarks into exotic matter")),
            "atlas_limits_remain_model_dependent": all(token in atlas for token in ("exclusion limits", "mediator mass", "dark quark couplings", "proper decay length")),
            "dark_abundance_and_gravity_rows_retained": dark_checks["ratio_passes"] and dark_checks["absolute_transport_passes"] and dark_checks["sparc_complete"],
            "smithion_measurement_not_invented": not dark_checks["smithion_mass_measured"] and dark["comparison_policy"]["smithion"].startswith("The four spectra remain standing exact predictions"),
            "complete_scope_boundary_retained": len(record["complete_comparison_vector"]) == 9 and len(record["source_power"]["establishes"]) == 5 and len(record["source_power"]["does_not_establish"]) == 6 and "retirement of a standing prediction from current non-observation" in record["source_power"]["does_not_establish"],
        }
        return {
            "checks": checks,
            "all_passed": all(checks.values()),
            "source_ids": tuple(source["source_id"] for source in record["sources"]),
            "source_count": len(record["sources"]),
            "standing_predictions_retained": force["standing_predictions_retained"] and not dark_checks["smithion_mass_measured"],
            "nonobservation_not_retirement": "retirement of a standing prediction from current non-observation" in record["source_power"]["does_not_establish"],
        }

    def validate(self, sealed):
        direct = self.direct_source_certificate()
        if not all((direct["all_passed"], direct["standing_predictions_retained"], direct["nonobservation_not_retirement"])):
            raise ValueError("new-sector direct source reconstruction failed")
        base = super().validate(sealed)
        return replace(
            base,
            all_rows_preserved=base.all_rows_preserved and direct["source_count"] == 5,
            measurements=base.measurements + tuple(f"direct source check {name}: {passed}" for name, passed in direct["checks"].items()) + ("all standing predictions retained without fabricated measurement or retirement",),
            measurement_receipt_hash=sha256_identity((base.measurement_receipt_hash, direct)),
            passed=base.passed and direct["all_passed"] and direct["standing_predictions_retained"] and direct["nonobservation_not_retirement"],
        )


__all__ = ("NewSectorCompleteFamilyMeasurementValidator",)
