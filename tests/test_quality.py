import unittest

from claims_platform.quality import validate_claim


def valid_claim():
    return {
        "claim_id": "clm_1",
        "policy_id": "pol_1",
        "vehicle_id": "veh_1",
        "event_time": "2026-05-04T10:15:00Z",
        "accident_date": "2026-05-03",
        "claim_type": "COLLISION",
        "status": "PAID",
        "claim_amount": 10000,
        "paid_amount": 8000,
        "city": "Kocaeli",
        "source_system": "MOBILE",
    }


class QualityTests(unittest.TestCase):
    def test_valid_claim_passes(self):
        self.assertTrue(validate_claim(valid_claim()).valid)

    def test_paid_amount_cannot_exceed_claim(self):
        claim = valid_claim()
        claim["paid_amount"] = 11000
        self.assertIn("paid_exceeds_claim", validate_claim(claim).reasons)

    def test_accident_cannot_be_after_event(self):
        claim = valid_claim()
        claim["accident_date"] = "2026-05-05"
        self.assertIn("accident_after_event", validate_claim(claim).reasons)

    def test_missing_fields_are_reported(self):
        claim = valid_claim()
        claim["vehicle_id"] = ""
        result = validate_claim(claim)
        self.assertFalse(result.valid)
        self.assertIn("missing_required:vehicle_id", result.reasons)


if __name__ == "__main__":
    unittest.main()
