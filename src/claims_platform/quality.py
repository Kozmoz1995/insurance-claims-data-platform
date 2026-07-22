"""Data contract and deterministic quality checks for claim events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Mapping

REQUIRED_FIELDS = {
    "claim_id",
    "policy_id",
    "vehicle_id",
    "event_time",
    "accident_date",
    "claim_type",
    "status",
    "claim_amount",
    "paid_amount",
    "city",
    "source_system",
}
CLAIM_TYPES = {"COLLISION", "THEFT", "FIRE", "GLASS", "NATURAL_DISASTER"}
STATUSES = {"OPEN", "UNDER_REVIEW", "APPROVED", "REJECTED", "PAID"}


@dataclass(frozen=True)
class QualityResult:
    valid: bool
    reasons: tuple[str, ...]


def _parse_datetime(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("not a string")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_date(value: Any) -> date:
    if not isinstance(value, str):
        raise ValueError("not a string")
    return date.fromisoformat(value)


def validate_claim(claim: Mapping[str, Any]) -> QualityResult:
    reasons: list[str] = []
    missing = sorted(field for field in REQUIRED_FIELDS if claim.get(field) in (None, ""))
    if missing:
        reasons.append("missing_required:" + ",".join(missing))

    if claim.get("claim_type") not in CLAIM_TYPES:
        reasons.append("invalid_claim_type")
    if claim.get("status") not in STATUSES:
        reasons.append("invalid_status")

    try:
        claim_amount = float(claim.get("claim_amount"))
        paid_amount = float(claim.get("paid_amount"))
        if claim_amount < 0 or paid_amount < 0:
            reasons.append("negative_amount")
        if paid_amount > claim_amount:
            reasons.append("paid_exceeds_claim")
    except (TypeError, ValueError):
        reasons.append("invalid_amount")

    try:
        accident_date = _parse_date(claim.get("accident_date"))
        event_date = _parse_datetime(claim.get("event_time")).date()
        if accident_date > event_date:
            reasons.append("accident_after_event")
    except ValueError:
        reasons.append("invalid_date")

    return QualityResult(valid=not reasons, reasons=tuple(reasons))
