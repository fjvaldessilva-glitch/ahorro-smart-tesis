"""Pruebas unitarias del generador conductual de T40.2.1."""

import math
import unittest

from scripts.behavioral_features import (
    CATEGORIES,
    build_enriched_feature_rows,
    compute_behavioral_features,
)


class BehavioralFeatureTests(unittest.TestCase):
    def setUp(self):
        self.cutoff = "2025-08-15"
        self.movements = [
            {"date": "2025-07-05", "category": "Alimentación", "amount": 10000, "type": "Gasto"},
            {"date": "2025-07-15", "category": "Transporte", "amount": 20000, "type": "Gasto"},
            {"date": "2025-07-20", "category": "Vivienda", "amount": 900000, "type": "Gasto"},
            {"date": "2025-08-09", "category": "Alimentación", "amount": 12000, "type": "Gasto"},
            {"date": "2025-08-10", "category": "Alimentación", "amount": 18000, "type": "Gasto"},
            {"date": "2025-08-15", "category": "Transporte", "amount": 30000, "type": "Gasto"},
        ]

    def features(self, category="Alimentación", movements=None):
        selected_movements = self.movements if movements is None else movements
        return compute_behavioral_features(selected_movements, category, self.cutoff)

    def test_expense_after_cutoff_does_not_change_features(self):
        original = self.features()
        future = [*self.movements,
                  {"date": "2025-08-16", "category": "Alimentación", "amount": 999999, "type": "Gasto"}]
        self.assertEqual(original, self.features(movements=future))

    def test_income_does_not_change_features(self):
        original = self.features()
        with_income = [*self.movements,
                       {"date": "2025-08-15", "category": "Alimentación", "amount": 500000, "type": "Ingreso"}]
        self.assertEqual(original, self.features(movements=with_income))

    def test_category_without_expenses_has_controlled_values(self):
        result = self.features(category="Mascotas", movements=[
            item for item in self.movements if item["category"] != "Mascotas"
        ])
        self.assertEqual(result["median_transaction_amount"], 0)
        self.assertEqual(result["days_since_last_expense"], 15)
        self.assertEqual(result["has_category_expense_history"], 0)
        self.assertEqual(result["category_previous_month_comparable_spend"], 0)
        self.assertTrue(all(not isinstance(value, float) or math.isfinite(value) for value in result.values()))

    def test_previous_month_uses_equivalent_days_only(self):
        result = self.features()
        self.assertEqual(result["previous_month_comparable_spend"], 30000)
        self.assertEqual(result["previous_month_comparable_transactions"], 2)
        self.assertEqual(result["category_previous_month_comparable_spend"], 10000)

    def test_last_seven_days_are_inclusive(self):
        result = self.features()
        self.assertEqual(result["spend_last_7_days"], 60000)
        self.assertEqual(result["transactions_last_7_days"], 3)
        self.assertEqual(result["median_transaction_amount"], 15000)
        self.assertEqual(result["active_spending_days"], 3)
        self.assertEqual(result["days_since_last_expense"], 5)
        self.assertEqual(result["has_category_expense_history"], 1)

    def test_category_with_exactly_one_expense(self):
        result = self.features(category="Transporte")
        self.assertEqual(result["median_transaction_amount"], 30000)
        self.assertEqual(result["days_since_last_expense"], 0)
        self.assertEqual(result["has_category_expense_history"], 1)

    def test_history_indicator_distinguishes_equal_recency(self):
        without_history = self.features(category="Mascotas", movements=[])
        with_same_recency = self.features(category="Mascotas", movements=[
            {"date": "2025-07-31", "category": "Mascotas", "amount": 10000, "type": "Gasto"},
        ])
        self.assertEqual(without_history["days_since_last_expense"], 15)
        self.assertEqual(with_same_recency["days_since_last_expense"], 15)
        self.assertEqual(without_history["has_category_expense_history"], 0)
        self.assertEqual(with_same_recency["has_category_expense_history"], 1)

    def test_user_without_expenses_in_last_seven_days(self):
        result = self.features(movements=[
            {"date": "2025-08-01", "category": "Alimentación", "amount": 10000, "type": "Gasto"},
        ])
        self.assertEqual(result["spend_last_7_days"], 0)
        self.assertEqual(result["transactions_last_7_days"], 0)

    def test_user_without_previous_month_movements(self):
        result = self.features(movements=[
            {"date": "2025-08-10", "category": "Alimentación", "amount": 10000, "type": "Gasto"},
        ])
        self.assertEqual(result["previous_month_comparable_spend"], 0)
        self.assertEqual(result["previous_month_comparable_transactions"], 0)
        self.assertEqual(result["category_previous_month_comparable_spend"], 0)

    def test_cutoff_day_one_uses_calendar_window_and_one_comparable_day(self):
        movements = [
            {"date": "2024-12-01", "category": "Alimentación", "amount": 1000, "type": "Gasto"},
            {"date": "2024-12-26", "category": "Alimentación", "amount": 2000, "type": "Gasto"},
            {"date": "2024-12-31", "category": "Transporte", "amount": 3000, "type": "Gasto"},
            {"date": "2025-01-01", "category": "Alimentación", "amount": 4000, "type": "Gasto"},
        ]
        result = compute_behavioral_features(movements, "Alimentación", "2025-01-01")
        self.assertEqual(result["spend_last_7_days"], 9000)
        self.assertEqual(result["transactions_last_7_days"], 3)
        self.assertEqual(result["previous_month_comparable_spend"], 1000)
        self.assertEqual(result["previous_month_comparable_transactions"], 1)

    def test_cutoff_days_five_and_twenty_five_use_equivalent_previous_ranges(self):
        movements = [
            {"date": "2025-07-05", "category": "Alimentación", "amount": 5000, "type": "Gasto"},
            {"date": "2025-07-06", "category": "Alimentación", "amount": 6000, "type": "Gasto"},
            {"date": "2025-07-25", "category": "Transporte", "amount": 25000, "type": "Gasto"},
        ]
        day_five = compute_behavioral_features(movements, "Alimentación", "2025-08-05")
        day_twenty_five = compute_behavioral_features(movements, "Alimentación", "2025-08-25")
        self.assertEqual(day_five["previous_month_comparable_spend"], 5000)
        self.assertEqual(day_five["previous_month_comparable_transactions"], 1)
        self.assertEqual(day_twenty_five["previous_month_comparable_spend"], 36000)
        self.assertEqual(day_twenty_five["previous_month_comparable_transactions"], 3)

    def test_previous_month_handles_year_change(self):
        result = compute_behavioral_features([
            {"date": "2024-12-10", "category": "Alimentación", "amount": 10000, "type": "Gasto"},
            {"date": "2024-12-20", "category": "Alimentación", "amount": 20000, "type": "Gasto"},
        ], "Alimentación", "2025-01-10")
        self.assertEqual(result["previous_month_comparable_spend"], 10000)
        self.assertEqual(result["previous_month_comparable_transactions"], 1)

    def test_february_non_leap_and_leap_year_are_capped_correctly(self):
        non_leap = compute_behavioral_features([
            {"date": "2025-02-28", "category": "Alimentación", "amount": 28000, "type": "Gasto"},
        ], "Alimentación", "2025-03-31")
        leap = compute_behavioral_features([
            {"date": "2024-02-28", "category": "Alimentación", "amount": 28000, "type": "Gasto"},
            {"date": "2024-02-29", "category": "Alimentación", "amount": 29000, "type": "Gasto"},
        ], "Alimentación", "2024-03-31")
        self.assertEqual(non_leap["previous_month_comparable_spend"], 28000)
        self.assertEqual(non_leap["previous_month_comparable_transactions"], 1)
        self.assertEqual(leap["previous_month_comparable_spend"], 57000)
        self.assertEqual(leap["previous_month_comparable_transactions"], 2)

    def test_same_input_is_reproducible(self):
        self.assertEqual(self.features(), self.features())

    def test_2026_cutoff_is_rejected_and_2026_records_are_not_used(self):
        with_2026 = [*self.movements,
                     {"date": "2026-01-01", "category": "Alimentación", "amount": 999999, "type": "Gasto"}]
        self.assertEqual(self.features(), self.features(movements=with_2026))
        with self.assertRaises(ValueError):
            compute_behavioral_features(self.movements, "Alimentación", "2026-01-05")

    def test_generated_rows_are_before_2026_and_cover_all_categories(self):
        rows = build_enriched_feature_rows()
        self.assertTrue(rows)
        self.assertTrue(all(row["period"] <= "2025-12" for row in rows))
        self.assertEqual({row["category"] for row in rows}, set(CATEGORIES))


if __name__ == "__main__":
    unittest.main()
