#!/usr/bin/env python3
"""Compute CFD-Applicability Score (CFD-AS) from case-level outcomes."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TRUE_VALUES = {"1", "true", "t", "yes", "y"}
FALSE_VALUES = {"0", "false", "f", "no", "n"}
REQUIRED_COLUMNS = {"case_id", "ground_truth_positive", "predicted_positive"}


def parse_binary(value: str | None, column: str, case_id: str, required: bool) -> bool | None:
    if value is None or not value.strip():
        if required:
            raise ValueError(f"{case_id}: missing required value for '{column}'")
        return None
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"{case_id}: '{column}' must be binary, got {value!r}")


def compute(rows: list[dict[str, str]]) -> dict[str, object]:
    counts = {"TP": 0, "FP": 0, "FN": 0, "TN": 0, "TdP": 0}
    failures = {"VTA": 0, "MGA": 0, "BFA": 0}

    for row_number, row in enumerate(rows, start=2):
        case_id = row.get("case_id", "").strip() or f"row-{row_number}"
        truth = parse_binary(row.get("ground_truth_positive"), "ground_truth_positive", case_id, True)
        prediction = parse_binary(row.get("predicted_positive"), "predicted_positive", case_id, True)

        if truth and prediction:
            counts["TP"] += 1
            outcomes = {
                "VTA": parse_binary(row.get("vta"), "vta", case_id, True),
                "MGA": parse_binary(row.get("mga"), "mga", case_id, True),
                "BFA": parse_binary(row.get("bfa"), "bfa", case_id, True),
            }
            for stage, passed in outcomes.items():
                if not passed:
                    failures[stage] += 1
            if all(outcomes.values()):
                counts["TdP"] += 1
        elif prediction:
            counts["FP"] += 1
        elif truth:
            counts["FN"] += 1
        else:
            counts["TN"] += 1

    denominator = counts["TP"] + counts["FP"] + counts["FN"]
    cfd_as = counts["TdP"] / denominator if denominator else None
    return {
        "formula": "TdP / (TP + FP + FN)",
        "counts": counts,
        "stage_failures_among_true_positives": failures,
        "denominator": denominator,
        "cfd_as": cfd_as,
        "cfd_as_percent": None if cfd_as is None else 100.0 * cfd_as,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Case-level CSV file")
    parser.add_argument("--output", type=Path, help="Optional JSON summary path")
    args = parser.parse_args()

    with args.input.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {', '.join(sorted(missing))}")
        summary = compute(list(reader))

    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
