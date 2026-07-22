"""Generate deterministic, synthetic motor-insurance claim events."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CLAIM_TYPES = ["COLLISION", "THEFT", "FIRE", "GLASS", "NATURAL_DISASTER"]
STATUSES = ["OPEN", "UNDER_REVIEW", "APPROVED", "REJECTED", "PAID"]
CITIES = ["Istanbul", "Ankara", "Izmir", "Kocaeli", "Bursa", "Antalya"]


def _identifier(prefix: str, value: int) -> str:
    digest = hashlib.sha256(f"{prefix}:{value}".encode()).hexdigest()[:12]
    return f"{prefix}_{digest}"


def generate_claims(count: int, seed: int = 42) -> list[dict[str, object]]:
    rng = random.Random(seed)
    base = date(2026, 1, 1)
    claims: list[dict[str, object]] = []
    for index in range(count):
        accident = base + timedelta(days=rng.randrange(180))
        event_time = datetime.combine(
            accident + timedelta(days=rng.randrange(0, 5)),
            datetime.min.time(),
            tzinfo=timezone.utc,
        ) + timedelta(seconds=rng.randrange(86_400))
        amount = round(rng.uniform(1_000, 250_000), 2)
        status = rng.choice(STATUSES)
        paid = round(rng.uniform(0, amount), 2) if status in {"APPROVED", "PAID"} else 0.0
        claims.append(
            {
                "claim_id": _identifier("clm", index),
                "policy_id": _identifier("pol", rng.randrange(max(1, count // 2))),
                "vehicle_id": _identifier("veh", rng.randrange(max(1, count // 2))),
                "event_time": event_time.isoformat().replace("+00:00", "Z"),
                "accident_date": accident.isoformat(),
                "claim_type": rng.choice(CLAIM_TYPES),
                "status": status,
                "claim_amount": amount,
                "paid_amount": paid,
                "city": rng.choice(CITIES),
                "source_system": rng.choice(["MOBILE", "AGENCY", "CALL_CENTER", "PARTNER_API"]),
            }
        )
    return claims


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as target:
        for claim in generate_claims(args.count, args.seed):
            target.write(json.dumps(claim) + "\n")


if __name__ == "__main__":
    main()
