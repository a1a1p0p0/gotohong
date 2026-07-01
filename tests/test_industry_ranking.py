import unittest

from src.industry_ranking import (
    calculate_balance_score,
    calculate_element_relation,
    calculate_favorable_score,
    rank_industries_by_period,
)


class IndustryRankingTest(unittest.TestCase):
    def test_element_relation(self):
        relation = calculate_element_relation("water", "wood", "fire")

        self.assertEqual(relation["main_relation"]["label"], "相生")
        self.assertTrue(relation["is_generating"])

    def test_favorable_score(self):
        score = calculate_favorable_score(
            {"main_element": "water"},
            {
                "subcategory_name": "测试行业",
                "main_element": "wood",
                "secondary_element": "fire",
                "element_scores": {
                    "wood": 35,
                    "fire": 20,
                    "earth": 15,
                    "metal": 10,
                    "water": 20
                },
                "emotion_heat": 80
            },
        )

        self.assertEqual(score["score"], 25)
        self.assertIn("时间五行生行业主五行", [item["reason"] for item in score["details"]])

    def test_balance_score(self):
        score = calculate_balance_score(
            {"main_element": "earth"},
            {
                "subcategory_name": "测试行业",
                "main_element": "metal",
                "secondary_element": "water",
                "element_scores": {
                    "wood": 10,
                    "fire": 10,
                    "earth": 20,
                    "metal": 30,
                    "water": 30
                },
                "emotion_heat": 60
            },
        )

        self.assertGreater(score["score"], 0)

    def test_rank_industries_by_period(self):
        ranking = rank_industries_by_period("day", "2026-06-29", "favorable")

        self.assertLessEqual(len(ranking), 5)
        self.assertEqual(ranking[0]["rank"], 1)
        self.assertIn("subcategory_name", ranking[0])


if __name__ == "__main__":
    unittest.main()
