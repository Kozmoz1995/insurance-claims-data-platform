"""Insurance claims data platform domain package."""

from .quality import QualityResult, validate_claim

__all__ = ["QualityResult", "validate_claim"]
