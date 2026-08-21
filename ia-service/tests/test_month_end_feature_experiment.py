"""Pruebas estructurales de T40.3.1; no entrenan modelos."""

import math
import unittest

from scripts.behavioral_features import FEATURE_NAMES, compute_behavioral_features
from scripts.run_month_end_feature_experiment import (
    EXPECTED_FEATURES_A,
    build_experiment_datasets,
    load_experiment_expenses,
    row_key,
    split_development_rows,
)


class MonthEndFeatureExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expenses = load_experiment_expenses()
        cls.datasets = build_experiment_datasets(cls.expenses)

    def test_model_a_has_exactly_sixteen_features(self):
        self.assertEqual(len(EXPECTED_FEATURES_A), 16)
        self.assertTrue(all(len(row["features"]) == 16 for row in self.datasets["A"]))

    def test_model_b_has_exactly_twenty_five_features(self):
        self.assertEqual(len(FEATURE_NAMES), 9)
        self.assertTrue(all(len(row["features"]) == 25 for row in self.datasets["B"]))

    def test_all_variants_have_same_rows_keys_and_targets(self):
        baseline = self.datasets["A"]
        baseline_keys = [row_key(row) for row in baseline]
        baseline_targets = [row["target"] for row in baseline]
        for rows in self.datasets.values():
            self.assertEqual([row_key(row) for row in rows], baseline_keys)
            self.assertEqual([row["target"] for row in rows], baseline_targets)

    def test_no_2026_dates_are_present(self):
        self.assertTrue(all(expense["date"].year < 2026 for expense in self.expenses))
        self.assertTrue(all(
            row["period"] <= "2025-12" and row["cutoff_date"] <= "2025-12-31"
            for rows in self.datasets.values() for row in rows
        ))

    def test_behavioral_features_match_the_dedicated_generator(self):
        enriched = self.datasets["B"][0]
        expected = compute_behavioral_features(
            self.expenses,
            enriched["category"],
            enriched["cutoff_date"],
        )
        self.assertEqual(enriched["features"][-9:], [expected[name] for name in FEATURE_NAMES])

    def test_each_scenario_has_ten_categories_and_unique_keys(self):
        baseline = self.datasets["A"]
        keys = [row_key(row) for row in baseline]
        self.assertEqual(len(keys), len(set(keys)))
        counts = {}
        for row in baseline:
            counts[row["scenario_id"]] = counts.get(row["scenario_id"], 0) + 1
        self.assertTrue(all(count == 10 for count in counts.values()))

    def test_all_numeric_features_are_finite(self):
        self.assertTrue(all(
            isinstance(value, (int, float)) and math.isfinite(value)
            for rows in self.datasets.values() for row in rows for value in row["features"][1:]
        ))

    def test_temporal_split_contains_only_train_and_validation(self):
        split = split_development_rows(self.datasets["B"])
        self.assertTrue(split["train"] and split["validation"])
        self.assertEqual(len(split["train"]) + len(split["validation"]), len(self.datasets["B"]))


if __name__ == "__main__":
    unittest.main()
