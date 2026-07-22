import json
import tempfile
import unittest
from pathlib import Path

from claims_platform.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_pipeline_quarantines_invalid_and_duplicate_records(self):
        fixture = Path("data/sample/claims.jsonl")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "curated.jsonl"
            report_path = root / "quality.json"
            report = run_pipeline(fixture, output, report_path)

            self.assertEqual(4, report["total_records"])
            self.assertEqual(2, report["valid_records"])
            self.assertEqual(1, report["errors"]["accident_after_event"])
            self.assertEqual(1, report["errors"]["duplicate_claim_id"])
            self.assertEqual(report, json.loads(report_path.read_text()))


if __name__ == "__main__":
    unittest.main()
