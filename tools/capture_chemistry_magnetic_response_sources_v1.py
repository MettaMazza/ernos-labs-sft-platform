#!/usr/bin/env python3
"""Capture the complete NIST molecular magnetic-response surface for PROP-012.

The capture starts from every holding exposed by NIST SRD 114, 115 and 117.
It preserves every holdings page, every linked constants page, and every table
cell carrying a rotational molecular g-factor or magnetic-susceptibility
component.  Values and source orientations are written only to the withheld
target registry; the identity registry contains no target inscription.
"""

from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-012-magnetic-response-v1"
PRIMARY_PATH = SNAPSHOT_DIR / "magnetic-response-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/magnetic_response_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/magnetic_response_withheld_targets_v1.json"
RESOLUTION_PATH = SNAPSHOT_DIR / "nist-complete-constants-page-resolution-v1.json"
DIATOMIC_REFERENCE_URL = "https://srd.nist.gov/jpcrdreprint/1.3253146.pdf"
DIATOMIC_REFERENCE_PATH = SNAPSHOT_DIR / "nist-jpcrd-microwave-spectral-tables-i-diatomic-1974.pdf"
DIATOMIC_TEXT_PATH = SNAPSHOT_DIR / "nist-jpcrd-microwave-spectral-tables-i-diatomic-1974-extracted.txt"

USER_AGENT = "Ernos-Labs-SFT-v3-source-custodian/1"
SEEDS = (
    ("diatomic", "https://physics.nist.gov/cgi-bin/MolSpec/diperiodic.pl", 121, 121),
    ("triatomic", "https://physics.nist.gov/cgi-bin/MolSpec/triperiodic.pl", 55, 55),
    ("hydrocarbon", "https://physics.nist.gov/PhysRefData/MolSpec/Hydro/hydrotable.html", 39, 91),
)


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urlopen(request, timeout=90) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
        except URLError:
            if attempt == 3:
                raise
        time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable NIST retrieval boundary")


def get_with_host_fallback(url: str) -> tuple[bytes, str]:
    """Open a NIST page, retaining a deterministic alternate-host fallback."""

    alternatives = (url, url.replace("https://physics.nist.gov/", "https://www.physics.nist.gov/"))
    last: Exception | None = None
    for candidate in dict.fromkeys(alternatives):
        try:
            return get(candidate), candidate
        except (HTTPError, URLError) as exc:
            last = exc
    if last is not None:
        raise last
    raise RuntimeError("NIST page has no resolvable host")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


@dataclass(frozen=True)
class Cell:
    text: str
    is_header: bool
    colspan: int


@dataclass(frozen=True)
class Row:
    section: str
    table_ordinal: int
    row_ordinal: int
    cells: tuple[Cell, ...]


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.section = "source-page"
        self._heading_tag = ""
        self._heading_parts: list[str] = []
        self._cell_tag = ""
        self._cell_parts: list[str] = []
        self._cell_colspan = 1
        self._row_cells: list[Cell] = []
        self._table_ordinal = 0
        self._row_ordinals: dict[int, int] = {}
        self.rows: list[Row] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        lowered = tag.casefold()
        if lowered in ("h1", "h2", "h3", "h4"):
            self._heading_tag = lowered
            self._heading_parts = []
        elif lowered == "table":
            self._table_ordinal += 1
            self._row_ordinals.setdefault(self._table_ordinal, 0)
        elif lowered in ("td", "th"):
            self._cell_tag = lowered
            self._cell_parts = []
            raw = dict(attrs).get("colspan", "1")
            self._cell_colspan = int(raw) if str(raw).isdigit() and int(raw) > 0 else 1
        elif lowered == "sub" and self._cell_tag:
            self._cell_parts.append("_")
        elif lowered == "sup" and self._cell_tag:
            self._cell_parts.append("^")
        elif lowered == "br" and self._cell_tag:
            self._cell_parts.append(" ")
        elif lowered == "img" and self._cell_tag:
            alt = dict(attrs).get("alt", "")
            if alt:
                self._cell_parts.append(" " + alt + " ")

    def handle_data(self, data: str) -> None:
        if self._heading_tag:
            self._heading_parts.append(data)
        if self._cell_tag:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered == self._heading_tag:
            value = clean_text("".join(self._heading_parts))
            if value:
                self.section = value
            self._heading_tag = ""
            self._heading_parts = []
        elif lowered == self._cell_tag:
            self._row_cells.append(Cell(
                clean_text("".join(self._cell_parts)),
                self._cell_tag == "th",
                self._cell_colspan,
            ))
            self._cell_tag = ""
            self._cell_parts = []
            self._cell_colspan = 1
        elif lowered == "tr":
            if self._row_cells and self._table_ordinal:
                ordinal = self._row_ordinals[self._table_ordinal] + 1
                self._row_ordinals[self._table_ordinal] = ordinal
                self.rows.append(Row(self.section, self._table_ordinal, ordinal, tuple(self._row_cells)))
            self._row_cells = []


def clean_text(value: str) -> str:
    return " ".join(value.replace("\u00a0", " ").replace("\u2009", " ").split())


def links(source: bytes, base: str) -> tuple[str, ...]:
    parser = LinkParser()
    parser.feed(source.decode("latin1", errors="replace"))
    return tuple(urljoin(base, item.replace("&amp;", "&")) for item in parser.links)


def safe_name(database: str, url: str) -> str:
    tail = url.rsplit("/", 1)[-1].split("?", 1)[0]
    return f"{database}-{re.sub(r'[^A-Za-z0-9_.-]+', '-', tail)}"


def magnetic_parameter(text: str, context: str) -> bool:
    compact = clean_text(text)
    lowered = compact.casefold()
    if "χ" in compact or "susceptib" in lowered:
        if any(unit in lowered for unit in ("mhz", "khz", "cm^-1", "cm-1")):
            return False
        if re.search(r"\((?:\^?[0-9]+)?(?:cl|n|o|s|d)\)", lowered):
            return False
        if "erg/g" in lowered or "j/t" in lowered or "susceptib" in lowered:
            return True
        tensor_difference = compact.count("χ") >= 2
        susceptibility_context = any(word in context.casefold() for word in ("magnetic", "zeeman"))
        return tensor_difference and susceptibility_context
    if "g-factor" in lowered or "g factor" in lowered or "magnetic moment" in lowered:
        return True
    g_token = re.search(r"(?:^|[^A-Za-z])g(?:_|\s)*(?:J|[abcxyz]{1,2}|[∥⊥]|para|perp)(?:\b|_)", compact)
    magnetic_context = any(word in context.casefold() for word in ("magnetic", "zeeman", "g-factor", "g factor"))
    magnetic_unit = any(unit in compact for unit in ("µ_N", "μ_N", "µN", "μN"))
    return bool(g_token and (magnetic_context or magnetic_unit))


def external_value_cell(text: str) -> bool:
    value = clean_text(text)
    if not value:
        return True
    if not re.match(r"^[<>~≈]?\s*[+-]?\s*(?:[0-9]|\.[0-9])", value):
        return False
    # Five-digit NIST reference identifiers are provenance, not target values.
    if re.fullmatch(r"\[?[0-9]{5}\]?", value):
        return False
    return True


def first_exact_scalar(inscription: str) -> dict[str, object] | None:
    text = clean_text(inscription)
    if not text:
        return None
    comparator = "exact"
    if "<" in text:
        comparator = "upper-bound"
    elif ">" in text:
        comparator = "lower-bound"
    elif "~" in text or "≈" in text:
        comparator = "approximate-source-inscription"
    match = re.search(
        r"(?P<sign>[+-]?)\s*(?P<number>[0-9]+(?:\s+[0-9]+)*(?:\.\s*[0-9]+(?:\s+[0-9]+)*)?|\.\s*[0-9]+)",
        text,
    )
    if match is None:
        return None
    number = match.group("number").replace(" ", "")
    magnitude = Fraction(number)
    exponent_match = re.search(r"(?:[x×]\s*)?10\s*\^?\s*([+-]?[0-9]+)", text[match.end():])
    exponent = int(exponent_match.group(1)) if exponent_match else 0
    if exponent >= 0:
        magnitude *= 10 ** exponent
    else:
        magnitude /= 10 ** (-exponent)
    sign = match.group("sign")
    orientation = "source-opposed" if sign == "-" else "source-aligned" if sign == "+" else "source-orientation-unspecified"
    uncertainty = None
    uncertainty_match = re.search(r"\(([0-9]+)\)", text[match.start():])
    if uncertainty_match:
        uncertainty = uncertainty_match.group(1)
    if magnitude == 0:
        return {
            "external_orientation": orientation,
            "external_comparator": comparator,
            "external_numerical_absence": "structural-EmptyOne",
            "source_parenthetical_uncertainty_digits": uncertainty,
        }
    return {
        "external_orientation": orientation,
        "external_comparator": comparator,
        "exact_positive_magnitude": {"numerator": magnitude.numerator, "denominator": magnitude.denominator},
        "source_parenthetical_uncertainty_digits": uncertainty,
    }


def expanded_cells(row: Row) -> tuple[tuple[int, Cell], ...]:
    resolved: list[tuple[int, Cell]] = []
    column = 1
    for cell in row.cells:
        for offset in range(cell.colspan):
            resolved.append((column + offset, cell))
        column += cell.colspan
    return tuple(resolved)


def extract_targets(database: str, page_ordinal: int, page_url: str, rows: tuple[Row, ...]) -> tuple[dict[str, object], ...]:
    tables: dict[int, list[Row]] = {}
    for row in rows:
        tables.setdefault(row.table_ordinal, []).append(row)
    targets: list[dict[str, object]] = []
    for table_ordinal, table_rows in sorted(tables.items()):
        table_text = " ".join(cell.text for row in table_rows for cell in row.cells)
        magnetic_columns: dict[int, str] = {}
        for row in table_rows:
            context = row.section + " " + table_text
            for column, cell in expanded_cells(row):
                if cell.is_header and magnetic_parameter(cell.text, context):
                    magnetic_columns[column] = cell.text
        for row in table_rows:
            context = row.section + " " + table_text
            expanded = expanded_cells(row)
            direct = tuple((column, cell) for column, cell in expanded if magnetic_parameter(cell.text, context))
            selected: list[tuple[int, Cell, str]] = []
            if direct:
                active_parameter: str | None = None
                for column, cell in expanded:
                    if magnetic_parameter(cell.text, context):
                        active_parameter = cell.text
                        continue
                    if active_parameter is not None and external_value_cell(cell.text):
                        selected.append((column, cell, active_parameter))
                    elif active_parameter is not None and cell.text:
                        active_parameter = None
            else:
                for column, cell in expanded:
                    if column in magnetic_columns and not cell.is_header and external_value_cell(cell.text):
                        selected.append((column, cell, magnetic_columns[column]))
            seen: set[tuple[int, str]] = set()
            for column, cell, parameter in selected:
                key = (column, cell.text)
                if key in seen:
                    continue
                seen.add(key)
                target_id = (
                    f"NIST-MOLSPEC-PROP-012-{database.upper()}-"
                    f"P{page_ordinal:03d}-T{table_ordinal:03d}-R{row.row_ordinal:03d}-C{column:03d}"
                )
                identity_cells = [
                    value.text for col, value in expanded
                    if col < column and value.text and not external_value_cell(value.text)
                ]
                parsed = first_exact_scalar(cell.text)
                targets.append({
                    "target_id": target_id,
                    "source_id": "NIST-MOLECULAR-MICROWAVE-SPECTRAL-DATABASES-SRD-114-115-117",
                    "source_locator": page_url,
                    "database": database,
                    "section": row.section,
                    "table_ordinal": table_ordinal,
                    "row_ordinal": row.row_ordinal,
                    "column_ordinal": column,
                    "magnetic_parameter": parameter,
                    "identity_context": identity_cells,
                    "measurement_kind": "molecular-rotational-g-factor-or-magnetic-susceptibility-component",
                    "source_value_present": bool(cell.text),
                    "source_value_inscription": cell.text if cell.text else None,
                    "native_value": parsed if parsed is not None else {"external_non_scalar_inscription": cell.text} if cell.text else {"structural_absence": "EmptyOne"},
                })
    return tuple(targets)


def diatomic_reference_pdf_targets() -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    """Extract every printed rotational g-factor scalar from the complete NIST table."""

    import pdfplumber

    if not DIATOMIC_REFERENCE_PATH.exists():
        DIATOMIC_REFERENCE_PATH.write_bytes(get(DIATOMIC_REFERENCE_URL))
    targets: list[dict[str, object]] = []
    text_archive: list[str] = []
    scalar_pattern = re.compile(r"[+\-±]?\s*[0-9]+\.\s*[0-9]+(?:\s*[0-9]+)*(?:\([0-9]+\))?")
    with pdfplumber.open(DIATOMIC_REFERENCE_PATH) as document:
        page_count = len(document.pages)
        for page_number, page in enumerate(document.pages, start=1):
            page_text = page.extract_text(layout=True) or ""
            text_archive.extend((f"\n===== OFFICIAL PDF PAGE {page_number} =====\n", page_text, "\n"))
            page_lines = page_text.splitlines()
            for line_ordinal, line in enumerate(page_lines, start=1):
                marker = re.search(r"\bg\s*J", line, re.IGNORECASE) or re.search(r"\bg/", line)
                tail = line[marker.end():] if marker is not None else ""
                tail = re.sub(r"\bt[oO]\.", "+0.", tail)
                scalars = tuple(scalar_pattern.finditer(tail))
                for scalar_ordinal, scalar in enumerate(scalars, start=1):
                    inscription = clean_text(scalar.group(0))
                    parsed = first_exact_scalar(inscription)
                    if parsed is None or "exact_positive_magnitude" not in parsed:
                        continue
                    target_id = (
                        f"NIST-MOLSPEC-PROP-012-DIATOMIC-PDF-"
                        f"P{page_number:03d}-L{line_ordinal:03d}-V{scalar_ordinal:02d}"
                    )
                    targets.append({
                        "target_id": target_id,
                        "source_id": "NIST-JPCRD-3-609-1974-DIATOMIC-MICROWAVE-SPECTRAL-TABLES",
                        "source_locator": f"{DIATOMIC_REFERENCE_URL}#page={page_number}",
                        "database": "diatomic-reference-pdf",
                        "section": f"official PDF page {page_number}",
                        "table_ordinal": 0,
                        "row_ordinal": line_ordinal,
                        "column_ordinal": scalar_ordinal,
                        "magnetic_parameter": "rotational molecular g_J factor",
                        "identity_context": [f"official PDF page {page_number}", f"extracted line {line_ordinal}"],
                        "measurement_kind": "published-molecular-rotational-g-factor",
                        "source_value_present": True,
                        "source_value_inscription": inscription,
                        "source_row_inscription": clean_text(line),
                        "native_value": parsed,
                    })
            # Some printed tables use a two-column DIPOLE MOMENT / MAGNETIC
            # CONSTANT header and omit the literal g_J label on the value row.
            header_index = None
            for index, line in enumerate(page_lines):
                window = " ".join(page_lines[max(0, index - 1):index + 2]).casefold()
                if "dipole" in window and "magnetic" in window and "constant" in window:
                    header_index = index
                    break
            if header_index is not None:
                for index in range(header_index + 1, min(len(page_lines), header_index + 8)):
                    line_ordinal, line = index + 1, page_lines[index]
                    scalars = tuple(scalar_pattern.finditer(line))
                    if len(scalars) < 2:
                        continue
                    scalar = scalars[-1]
                    inscription = clean_text(scalar.group(0))
                    parsed = first_exact_scalar(inscription)
                    if parsed is None or "exact_positive_magnitude" not in parsed:
                        continue
                    target_id = f"NIST-MOLSPEC-PROP-012-DIATOMIC-PDF-P{page_number:03d}-L{line_ordinal:03d}-MAG"
                    if target_id in {row["target_id"] for row in targets}:
                        continue
                    targets.append({
                        "target_id": target_id,
                        "source_id": "NIST-JPCRD-3-609-1974-DIATOMIC-MICROWAVE-SPECTRAL-TABLES",
                        "source_locator": f"{DIATOMIC_REFERENCE_URL}#page={page_number}",
                        "database": "diatomic-reference-pdf",
                        "section": f"official PDF page {page_number}",
                        "table_ordinal": 0,
                        "row_ordinal": line_ordinal,
                        "column_ordinal": len(scalars),
                        "magnetic_parameter": "printed magnetic constant g_J",
                        "identity_context": [f"official PDF page {page_number}", "DIPOLE MOMENT / MAGNETIC CONSTANT table"],
                        "measurement_kind": "published-molecular-rotational-g-factor",
                        "source_value_present": True,
                        "source_value_inscription": inscription,
                        "source_row_inscription": clean_text(line),
                        "native_value": parsed,
                    })
                    break
    DIATOMIC_TEXT_PATH.write_text("".join(text_archive), encoding="utf-8")
    if page_count != 162 or not targets:
        raise RuntimeError(f"NIST diatomic reference-data boundary changed: pages={page_count}, targets={len(targets)}")
    return tuple(targets), {
        "source_id": "NIST-JPCRD-3-609-1974-DIATOMIC-MICROWAVE-SPECTRAL-TABLES",
        "source_url": DIATOMIC_REFERENCE_URL,
        "pdf_snapshot_path": str(DIATOMIC_REFERENCE_PATH.relative_to(ROOT)),
        "pdf_snapshot_hash": sha256_file(DIATOMIC_REFERENCE_PATH),
        "pdf_page_count": page_count,
        "extracted_text_path": str(DIATOMIC_TEXT_PATH.relative_to(ROOT)),
        "extracted_text_hash": sha256_file(DIATOMIC_TEXT_PATH),
        "rotational_g_factor_scalar_count": len(targets),
    }


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    holdings_manifest: list[dict[str, object]] = []
    molecule_pages: list[tuple[str, str]] = []
    for database, seed_url, expected_group_count, declared_molecule_count in SEEDS:
        source = get(seed_url)
        snapshot = SNAPSHOT_DIR / f"nist-{database}-holdings.html"
        snapshot.write_bytes(source)
        molecule_links = tuple(dict.fromkeys(link for link in links(source, seed_url) if "mole.pl?" in link))
        if len(molecule_links) != expected_group_count:
            raise RuntimeError(f"NIST {database} holdings changed: {len(molecule_links)}")
        holdings_manifest.append({
            "database": database,
            "holdings_url": seed_url,
            "snapshot_path": str(snapshot.relative_to(ROOT)),
            "snapshot_hash": sha256_file(snapshot),
            "holding_group_count": len(molecule_links),
            "nist_declared_molecule_count": declared_molecule_count,
        })
        molecule_pages.extend((database, molecule_url) for molecule_url in molecule_links)

    if RESOLUTION_PATH.exists():
        resolution = json.loads(RESOLUTION_PATH.read_text(encoding="utf-8"))
        if (
            resolution.get("schema") != "sft-v3-nist-molspec-constants-resolution/1"
            or resolution.get("complete_molecule_group_count") != 215
            or len(resolution.get("rows", ())) != 215
        ):
            raise RuntimeError("cached NIST constants-page resolution is incomplete")
        constants_pages = [(str(row["database"]), str(row["constants_url"])) for row in resolution["rows"]]
    else:
        def resolve(item: tuple[str, str]) -> dict[str, str]:
            database, molecule_url = item
            source_page = get(molecule_url)
            table_links = tuple(dict.fromkeys(link for link in links(source_page, molecule_url) if "/Html/Tables/" in link))
            if len(table_links) != 1:
                raise RuntimeError(f"NIST molecule page did not expose exactly one constants table: {molecule_url}")
            return {"database": database, "molecule_url": molecule_url, "constants_url": table_links[0]}

        with ThreadPoolExecutor(max_workers=5) as pool:
            resolved_rows = list(pool.map(resolve, molecule_pages))
        write_json(RESOLUTION_PATH, {
            "schema": "sft-v3-nist-molspec-constants-resolution/1",
            "complete_molecule_group_count": len(resolved_rows),
            "rows": resolved_rows,
        })
        constants_pages = [(row["database"], row["constants_url"]) for row in resolved_rows]
    constants_pages = list(dict.fromkeys(constants_pages))
    if len(constants_pages) != 215:
        raise RuntimeError(f"NIST complete constants-page boundary changed: {len(constants_pages)}")

    prior_unavailable: dict[str, str] = {}
    if PRIMARY_PATH.exists():
        prior = json.loads(PRIMARY_PATH.read_text(encoding="utf-8"))
        prior_unavailable = {
            str(row["source_url"]): str(row["retrieval_status"])
            for row in prior.get("complete_constants_page_manifest", ())
            if int(row.get("byte_count", 0)) == 0
        }

    def retrieve_constants(item: tuple[int, tuple[str, str]]) -> dict[str, object]:
        ordinal, (database, page_url) = item
        snapshot = SNAPSHOT_DIR / safe_name(database, page_url)
        if snapshot.exists() and snapshot.stat().st_size > 1000:
            return {
                "ordinal": ordinal, "database": database, "page_url": page_url,
                "resolved_url": page_url, "snapshot": snapshot, "source": snapshot.read_bytes(),
                "retrieval_status": "preserved-from-completed-capture",
            }
        if page_url in prior_unavailable:
            return {
                "ordinal": ordinal, "database": database, "page_url": page_url,
                "resolved_url": None, "snapshot": snapshot, "source": b"",
                "retrieval_status": prior_unavailable[page_url],
            }
        try:
            source, resolved_url = get_with_host_fallback(page_url)
        except (HTTPError, URLError) as exc:
            return {
                "ordinal": ordinal, "database": database, "page_url": page_url,
                "resolved_url": None, "snapshot": snapshot, "source": b"",
                "retrieval_status": f"official-linked-page-unavailable-{type(exc).__name__}-{getattr(exc, 'code', 'network')}",
            }
        snapshot.write_bytes(source)
        return {
            "ordinal": ordinal, "database": database, "page_url": page_url,
            "resolved_url": resolved_url, "snapshot": snapshot, "source": source,
            "retrieval_status": "preserved-from-official-source",
        }

    print("retrieving all 215 resolved constants pages with bounded concurrency", flush=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        retrieved_pages = list(pool.map(retrieve_constants, enumerate(constants_pages, start=1)))

    page_manifest: list[dict[str, object]] = []
    all_targets: list[dict[str, object]] = []
    for result in retrieved_pages:
        ordinal = int(result["ordinal"])
        database = str(result["database"])
        page_url = str(result["page_url"])
        resolved_url = result["resolved_url"]
        snapshot = result["snapshot"]
        source = result["source"]
        retrieval_status = str(result["retrieval_status"])
        targets: tuple[dict[str, object], ...] = ()
        if source:
            parser = TableParser()
            parser.feed(source.decode("latin1", errors="replace"))
            targets = extract_targets(database, ordinal, page_url, tuple(parser.rows))
        page_manifest.append({
            "page_ordinal": ordinal,
            "database": database,
            "source_url": page_url,
            "resolved_url": resolved_url,
            "retrieval_status": retrieval_status,
            "snapshot_path": str(snapshot.relative_to(ROOT)) if source else None,
            "snapshot_hash": sha256_file(snapshot) if source else None,
            "byte_count": len(source),
            "magnetic_target_cell_count": len(targets),
        })
        all_targets.extend(targets)
        print(
            f"[{ordinal:03d}/215] {retrieval_status} {database} "
            f"{page_url.rsplit('/', 1)[-1]}: {len(targets)} magnetic cells",
            flush=True,
        )

    pdf_targets, diatomic_reference_manifest = diatomic_reference_pdf_targets()
    all_targets.extend(pdf_targets)
    print(f"preserved complete 162-page diatomic reference PDF: {len(pdf_targets)} rotational g-factor scalars", flush=True)

    if not all_targets or len({row["target_id"] for row in all_targets}) != len(all_targets):
        raise RuntimeError("NIST magnetic-response target extraction is empty or non-unique")
    present = sum(bool(row["source_value_present"]) for row in all_targets)
    absent = len(all_targets) - present
    scalar = sum("exact_positive_magnitude" in row["native_value"] for row in all_targets)
    numerical_absence = sum("external_numerical_absence" in row["native_value"] for row in all_targets)
    nonscalar = sum("external_non_scalar_inscription" in row["native_value"] for row in all_targets)
    opposed = sum(row["native_value"].get("external_orientation") == "source-opposed" for row in all_targets)
    aligned = sum(row["native_value"].get("external_orientation") == "source-aligned" for row in all_targets)

    identities = [{
        key: row[key] for key in (
            "target_id", "source_id", "source_locator", "database", "section",
            "table_ordinal", "row_ordinal", "column_ordinal", "magnetic_parameter",
            "identity_context", "measurement_kind",
        )
    } | {"target_value_absent": True} for row in all_targets]
    targets = [{
        "target_id": row["target_id"],
        "source_value_present": row["source_value_present"],
        "source_value_inscription": row["source_value_inscription"],
        "native_value": row["native_value"],
    } for row in all_targets]
    primary = {
        "schema": "sft-v3-nist-molecular-magnetic-response-primary-records/1",
        "source_id": "NIST-MOLECULAR-MICROWAVE-SPECTRAL-DATABASES-SRD-114-115-117",
        "source_role": "complete molecular rotational-g-factor and magnetic-susceptibility cell surface",
        "holdings": holdings_manifest,
        "complete_declared_molecule_count": sum(item[3] for item in SEEDS),
        "complete_holding_group_count": sum(item[2] for item in SEEDS),
        "complete_constants_page_count": len(page_manifest),
        "retrieved_constants_page_count": sum(row["byte_count"] > 0 for row in page_manifest),
        "official_linked_unavailable_page_count": sum(row["byte_count"] == 0 for row in page_manifest),
        "complete_constants_page_manifest": page_manifest,
        "diatomic_reference_pdf": diatomic_reference_manifest,
        "diatomic_reference_pdf_target_count": len(pdf_targets),
        "complete_target_cell_count": len(all_targets),
        "source_value_present_count": present,
        "source_value_absent_count": absent,
        "exact_positive_scalar_count": scalar,
        "external_numerical_absence_count": numerical_absence,
        "external_non_scalar_inscription_count": nonscalar,
        "source_opposed_orientation_count": opposed,
        "source_aligned_orientation_count": aligned,
        "all_signed_and_unsigned_source_inscriptions_preserved": True,
        "rows": all_targets,
    }
    identity_document = {
        "schema": "sft-v3-magnetic-response-identities/1",
        "source_id": primary["source_id"],
        "complete_target_count": len(identities),
        "all_magnetic_values_and_orientations_absent": True,
        "rows": identities,
    }
    target_document = {
        "schema": "sft-v3-magnetic-response-withheld-targets/1",
        "source_id": primary["source_id"],
        "release_requires_prediction_seal": True,
        "complete_target_count": len(targets),
        "rows": targets,
    }
    write_json(PRIMARY_PATH, primary)
    write_json(IDENTITY_PATH, identity_document)
    write_json(TARGET_PATH, target_document)
    print(json.dumps({
        "primary_path": str(PRIMARY_PATH.relative_to(ROOT)),
        "primary_hash": sha256_file(PRIMARY_PATH),
        "identity_path": str(IDENTITY_PATH.relative_to(ROOT)),
        "identity_hash": sha256_file(IDENTITY_PATH),
        "target_path": str(TARGET_PATH.relative_to(ROOT)),
        "target_hash": sha256_file(TARGET_PATH),
        "constants_pages": len(page_manifest),
        "declared_molecules": primary["complete_declared_molecule_count"],
        "target_cells": len(all_targets),
        "present": present,
        "absent": absent,
        "exact_positive_scalars": scalar,
        "external_numerical_absences": numerical_absence,
        "external_non_scalar_inscriptions": nonscalar,
        "source_opposed_orientations": opposed,
        "source_aligned_orientations": aligned,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
