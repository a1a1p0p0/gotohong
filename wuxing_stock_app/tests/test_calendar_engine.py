import unittest

from wuxing_stock_app.modules.calendar_engine import (
    branch_to_element,
    get_period_element,
    load_calendar_rows,
    stem_to_element,
)


class CalendarEngineTest(unittest.TestCase):
    def test_load_calendar_rows(self):
        rows = load_calendar_rows()

        self.assertEqual(len(rows), 5844)
        self.assertEqual(rows[0]["date"], "2020-01-01")
        self.assertEqual(rows[-1]["date"], "2035-12-31")
        self.assertEqual(rows[0]["year_gan"], "己")
        self.assertEqual(rows[0]["day_zhi"], "卯")
        self.assertIn("source", rows[0])
        self.assertIn("verified", rows[0])
        self.assertIn("updated_at", rows[0])
        self.assertIn("confidence", rows[0])

    def test_stem_to_element(self):
        self.assertEqual(stem_to_element("甲"), "wood")
        self.assertEqual(stem_to_element("丙"), "fire")
        self.assertEqual(stem_to_element("戊"), "earth")
        self.assertEqual(stem_to_element("庚"), "metal")
        self.assertEqual(stem_to_element("壬"), "water")

    def test_branch_to_element(self):
        self.assertEqual(branch_to_element("寅"), "wood")
        self.assertEqual(branch_to_element("午"), "fire")
        self.assertEqual(branch_to_element("辰"), "earth")
        self.assertEqual(branch_to_element("申"), "metal")
        self.assertEqual(branch_to_element("子"), "water")

    def test_get_year_element_uses_lichun_year_ganzhi(self):
        result = get_period_element("year", "2026-06-29")

        self.assertEqual(result["main_element"], "fire")
        self.assertEqual(result["secondary_element"], "fire")
        self.assertEqual(result["strength_score"], 100)
        self.assertIn("年度", result["description"])

    def test_get_month_element_uses_jieqi_month(self):
        result = get_period_element("month", "2026-07-01")

        self.assertEqual(result["main_element"], "fire")
        self.assertEqual(result["secondary_element"], "wood")
        self.assertEqual(result["strength_score"], 50)

    def test_get_day_element(self):
        result = get_period_element("day", "2026-06-29")

        self.assertEqual(result["main_element"], "earth")
        self.assertEqual(result["secondary_element"], "wood")
        self.assertEqual(result["strength_score"], 50)
        self.assertIn("日度", result["description"])

    def test_get_week_element_by_7_day_statistics(self):
        result = get_period_element("week", "2026-07-01")

        self.assertEqual(result["main_element"], "earth")
        self.assertEqual(result["secondary_element"], "wood")
        self.assertEqual(result["strength_score"], 36)
        self.assertIn("周度", result["description"])

    def test_invalid_period_type_raises_error(self):
        with self.assertRaises(ValueError):
            get_period_element("quarter", "2026-06-29")

    def test_missing_date_raises_error(self):
        with self.assertRaises(ValueError):
            get_period_element("day", "2036-01-01")


if __name__ == "__main__":
    unittest.main()
