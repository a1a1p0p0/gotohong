import unittest

from wuxing_stock_app.modules.ranking_engine import rank_industries


class RankingEngineTest(unittest.TestCase):
    def test_rank_favorable_industries(self):
        result = rank_industries("day", "2026-06-29", "favorable")

        self.assertGreaterEqual(len(result), 1)
        self.assertLessEqual(len(result), 5)
        self.assertEqual(result[0]["rank"], 1)
        self.assertIn("industry_name", result[0])
        self.assertIn("main_element", result[0])
        self.assertIn("secondary_element", result[0])
        self.assertIn("score", result[0])
        self.assertIn("reason", result[0])
        self.assertIn("顺势", result[0]["reason"])

    def test_rank_balanced_industries(self):
        result = rank_industries("week", "2026-07-01", "balanced")

        self.assertGreaterEqual(len(result), 1)
        self.assertLessEqual(len(result), 5)
        self.assertEqual(result[0]["rank"], 1)
        self.assertIn("industry_name", result[0])
        self.assertIn("main_element", result[0])
        self.assertIn("secondary_element", result[0])
        self.assertIn("score", result[0])
        self.assertIn("reason", result[0])
        self.assertIn("结构", result[0]["reason"])

    def test_supports_month_week_day(self):
        for period_type, date_text in [
            ("month", "2026-07-01"),
            ("week", "2026-07-01"),
            ("day", "2026-06-29"),
        ]:
            with self.subTest(period_type=period_type):
                result = rank_industries(period_type, date_text, "favorable")
                self.assertGreaterEqual(len(result), 1)

    def test_invalid_period_type_raises_error(self):
        with self.assertRaises(ValueError):
            rank_industries("year", "2026-06-29", "favorable")

    def test_invalid_ranking_type_raises_error(self):
        with self.assertRaises(ValueError):
            rank_industries("day", "2026-06-29", "hot")


if __name__ == "__main__":
    unittest.main()
