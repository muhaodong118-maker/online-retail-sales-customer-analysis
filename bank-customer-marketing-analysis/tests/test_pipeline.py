import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import clean_and_engineer, conversion_summary  # noqa: E402


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.sample = pd.DataFrame([
            {"age": 24, "job": "student", "marital": "single", "education": "tertiary", "default": "no", "balance": 1200, "housing": "no", "loan": "no", "contact": "cellular", "day": 5, "month": "may", "duration": 120, "campaign": 1, "pdays": -1, "previous": 0, "poutcome": "unknown", "y": "yes"},
            {"age": 42, "job": "technician", "marital": "married", "education": "secondary", "default": "no", "balance": -20, "housing": "yes", "loan": "no", "contact": "telephone", "day": 8, "month": "jun", "duration": 80, "campaign": 4, "pdays": 12, "previous": 1, "poutcome": "success", "y": "no"},
            {"age": 67, "job": "retired", "marital": "married", "education": "unknown", "default": "no", "balance": 8000, "housing": "no", "loan": "no", "contact": "cellular", "day": 10, "month": "jul", "duration": 200, "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown", "y": "yes"},
        ])

    def test_engineered_fields(self):
        out = clean_and_engineer(self.sample)
        self.assertEqual(out["target"].tolist(), [1, 0, 1])
        self.assertEqual(out["age_group"].tolist(), ["18-24", "35-44", "65+"])
        self.assertEqual(out["previous_contacted"].tolist(), ["No previous contact", "Previously contacted", "No previous contact"])
        self.assertEqual(out["campaign_group"].tolist(), ["1 contact", "4-5 contacts", "2 contacts"])

    def test_conversion_summary_counts(self):
        out = clean_and_engineer(self.sample)
        result = conversion_summary(out, "job")
        self.assertEqual(int(result["marketing_records"].sum()), 3)
        self.assertEqual(int(result["subscribed_records"].sum()), 2)

    def test_unexpected_target_raises(self):
        bad = self.sample.copy()
        bad.loc[0, "y"] = "maybe"
        with self.assertRaises(ValueError):
            clean_and_engineer(bad)


if __name__ == "__main__":
    unittest.main()
