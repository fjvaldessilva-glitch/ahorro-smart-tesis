"""Pruebas estructurales de T40.3.3; no entrenan modelos."""

import math
import unittest

from scripts.run_month_end_feature_experiment_b3 import (
    EXPECTED_FEATURE_COUNTS,
    FEATURE_GROUPS,
    build_experiment_datasets,
    build_pretraining_summary,
    load_experiment_expenses,
    row_key,
    split_development_rows,
)
from scripts.train_month_end_model import CATEGORIES


class MonthEndSelectiveFeatureExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expenses = load_experiment_expenses()
        cls.datasets = build_experiment_datasets(cls.expenses)

    def test_feature_counts_are_exact(self):
        self.assertEqual(
            EXPECTED_FEATURE_COUNTS,
            {"A": 16, "B3": 19, "C1": 17, "C2": 17, "C3": 18, "C4": 19},
        )
        for variant, expected in EXPECTED_FEATURE_COUNTS.items():
            self.assertTrue(
                all(len(row["features"]) == expected for row in self.datasets[variant])
            )

    def test_feature_groups_match_the_selective_design(self):
        self.assertEqual(FEATURE_GROUPS["C1"], ("previous_month_comparable_spend",))
        self.assertEqual(
            FEATURE_GROUPS["C2"],
            ("category_previous_month_comparable_spend",),
        )
        self.assertEqual(
            FEATURE_GROUPS["C3"],
            (
                "previous_month_comparable_spend",
                "category_previous_month_comparable_spend",
            ),
        )
        self.assertEqual(
            FEATURE_GROUPS["C4"],
            (
                "previous_month_comparable_spend",
                "category_previous_month_comparable_spend",
                "transactions_last_7_days",
            ),
        )

    def test_all_variants_have_same_rows_keys_and_targets(self):
        baseline = self.datasets["A"]
        baseline_keys = [row_key(row) for row in baseline]
        baseline_targets = [row["target"] for row in baseline]
        for rows in self.datasets.values():
            self.assertEqual([row_key(row) for row in rows], baseline_keys)
            self.assertEqual([row["target"] for row in rows], baseline_targets)

    def test_no_nan_infinity_or_missing_numeric_features(self):
        self.assertTrue(
            all(
                isinstance(value, (int, float)) and math.isfinite(value)
                for rows in self.datasets.values()
                for row in rows
                for value in row["features"][1:]
            )
        )

    def test_reserved_2026_is_not_loaded_or_generated(self):
        self.assertTrue(all(expense["date"].year < 2026 for expense in self.expenses))
        self.assertTrue(
            all(
                row["period"] <= "2025-12" and row["cutoff_date"] <= "2025-12-31"
                for rows in self.datasets.values()
                for row in rows
            )
        )

    def test_each_scenario_contains_all_official_categories(self):
        scenarios = {}
        for row in self.datasets["A"]:
            scenarios.setdefault(row["scenario_id"], set()).add(row["category"])
        self.assertTrue(scenarios)
        self.assertTrue(all(categories == set(CATEGORIES) for categories in scenarios.values()))

    def test_temporal_split_is_identical_between_variants(self):
        expected = split_development_rows(self.datasets["A"])
        for rows in self.datasets.values():
            split = split_development_rows(rows)
            self.assertEqual(len(split["train"]), len(expected["train"]))
            self.assertEqual(len(split["validation"]), len(expected["validation"]))
            self.assertTrue(all(row["period"] <= "2025-06" for row in split["train"]))
            self.assertTrue(
                all("2025-07" <= row["period"] <= "2025-12" for row in split["validation"])
            )

    def test_summary_confirms_preparation_without_training(self):
        summary = build_pretraining_summary(self.datasets)
        self.assertFalse(summary["uses_reserved_2026"])
        self.assertFalse(summary["training_executed"])
        self.assertEqual(summary["target"], "category_month_end_total")


if __name__ == "__main__":
    unittest.main()
