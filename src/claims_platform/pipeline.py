"""Small local runner mirroring the platform's validate/curate stages."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .quality import validate_claim


def run_pipeline(input_path: Path, output_path: Path, report_path: Path) -> dict[str, Any]:
    seen: set[str] = set()
    valid_records: list[dict[str, Any]] = []
    errors: Counter[str] = Counter()
    total = 0

    with input_path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            total += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                errors["invalid_json"] += 1
                continue

            result = validate_claim(record)
            claim_id = record.get("claim_id")
            if claim_id in seen:
                errors["duplicate_claim_id"] += 1
                continue
            if not result.valid:
                errors.update(result.reasons)
                continue

            seen.add(claim_id)
            record["claim_amount"] = round(float(record["claim_amount"]), 2)
            record["paid_amount"] = round(float(record["paid_amount"]), 2)
            record["source_line"] = line_number
            valid_records.append(record)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as target:
        for record in valid_records:
            target.write(json.dumps(record, sort_keys=True) + "\n")

    report = {
        "total_records": total,
        "valid_records": len(valid_records),
        "invalid_records": total - len(valid_records),
        "validity_rate": round(len(valid_records) / total, 4) if total else 0,
        "errors": dict(sorted(errors.items())),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quality-report", type=Path, required=True)
    args = parser.parse_args()
    report = run_pipeline(args.input, args.output, args.quality_report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
