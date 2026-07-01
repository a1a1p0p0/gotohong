import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.classify_astock_boards import classify_astock_boards
from wuxing_stock_app import database


class ClassifyAstockBoardsTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tmpdir.name)
        self.industry_csv = self.base / "astock_industry_raw.csv"
        self.concept_csv = self.base / "astock_concept_raw.csv"
        self.categories_json = self.base / "industry_categories.json"
        self.subcategories_json = self.base / "industry_subcategories.json"
        self.output_csv = self.base / "astock_board_wuxing_profiles.csv"
        self.db_path = self.base / "test.db"
        self.write_fixture_files()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_classify_astock_boards_outputs_required_fields(self):
        rows = classify_astock_boards(
            industry_csv=self.industry_csv,
            concept_csv=self.concept_csv,
            categories_json=self.categories_json,
            subcategories_json=self.subcategories_json,
            output_csv=self.output_csv,
            updated_at="2026-06-29T16:00:00",
            db_path=self.db_path,
        )

        self.assertEqual(len(rows), 3)
        self.assertTrue(self.output_csv.exists())
        with self.output_csv.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            self.assertEqual(
                reader.fieldnames,
                [
                    "board_code",
                    "board_name",
                    "board_type",
                    "category",
                    "subcategory",
                    "main_element",
                    "secondary_element",
                    "wood_score",
                    "fire_score",
                    "earth_score",
                    "metal_score",
                    "water_score",
                    "confidence",
                    "reason",
                    "paid_required",
                    "source",
                    "updated_at",
                    "need_review",
                ],
            )

    def test_semiconductor_board_uses_profile_metadata_not_name_only(self):
        rows = classify_astock_boards(
            industry_csv=self.industry_csv,
            concept_csv=self.concept_csv,
            categories_json=self.categories_json,
            subcategories_json=self.subcategories_json,
            output_csv=self.output_csv,
            updated_at="2026-06-29T16:00:00",
            db_path=self.db_path,
        )
        semiconductor = next(row for row in rows if row["board_code"] == "BK0001")

        self.assertEqual(semiconductor["category"], "科技")
        self.assertEqual(semiconductor["subcategory"], "半导体")
        self.assertEqual(semiconductor["main_element"], "metal")
        self.assertEqual(semiconductor["paid_required"], "true")
        self.assertEqual(semiconductor["source"], "local_industry_mapping_rules")
        self.assertEqual(semiconductor["updated_at"], "2026-06-29T16:00:00")
        self.assertEqual(semiconductor["need_review"], "false")
        self.assertIn("industry_position=", semiconductor["reason"])
        self.assertIn("business_model=", semiconductor["reason"])
        self.assertIn("member_count=26", semiconductor["reason"])

    def test_uncertain_board_is_marked_need_review(self):
        rows = classify_astock_boards(
            industry_csv=self.industry_csv,
            concept_csv=self.concept_csv,
            categories_json=self.categories_json,
            subcategories_json=self.subcategories_json,
            output_csv=self.output_csv,
            updated_at="2026-06-29T16:00:00",
            db_path=self.db_path,
        )
        uncertain = next(row for row in rows if row["board_code"] == "BK9999")

        self.assertEqual(uncertain["category"], "need_review")
        self.assertEqual(uncertain["main_element"], "need_review")
        self.assertEqual(uncertain["need_review"], "true")

    def test_results_are_saved_to_sqlite(self):
        classify_astock_boards(
            industry_csv=self.industry_csv,
            concept_csv=self.concept_csv,
            categories_json=self.categories_json,
            subcategories_json=self.subcategories_json,
            output_csv=self.output_csv,
            updated_at="2026-06-29T16:00:00",
            db_path=self.db_path,
        )

        rows = database.fetch_all("SELECT * FROM astock_board_wuxing_profiles", db_path=self.db_path)
        self.assertGreaterEqual(len(rows), 3)

    def write_fixture_files(self):
        self.write_csv(
            self.industry_csv,
            [
                {
                    "board_type": "industry",
                    "board_code": "BK0001",
                    "board_name": "半导体设备",
                    "source": "test",
                    "member_count": "26",
                    "updated_at": "2026-06-29T16:00:00",
                    "confidence": "100",
                },
                {
                    "board_type": "industry",
                    "board_code": "BK9999",
                    "board_name": "未知主题",
                    "source": "test",
                    "member_count": "0",
                    "updated_at": "2026-06-29T16:00:00",
                    "confidence": "50",
                },
            ],
        )
        self.write_csv(
            self.concept_csv,
            [
                {
                    "board_type": "concept",
                    "board_code": "BK0002",
                    "board_name": "AI应用",
                    "source": "test",
                    "member_count": "88",
                    "updated_at": "2026-06-29T16:00:00",
                    "confidence": "100",
                }
            ],
        )
        self.categories_json.write_text(
            json.dumps(
                [
                    {
                        "category_id": "tech",
                        "category_name": "科技",
                        "main_element": "metal",
                        "secondary_element": "fire",
                        "element_scores": {
                            "wood": 15,
                            "fire": 25,
                            "earth": 10,
                            "metal": 35,
                            "water": 15,
                        },
                        "behavior_description": "科技大类以规则、硬件、算法和技术显化为核心。",
                    }
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.subcategories_json.write_text(
            json.dumps(
                [
                    {
                        "subcategory_id": "tech_semiconductor",
                        "category_id": "tech",
                        "subcategory_name": "半导体",
                        "main_element": "metal",
                        "secondary_element": "fire",
                        "element_scores": {
                            "wood": 10,
                            "fire": 25,
                            "earth": 10,
                            "metal": 40,
                            "water": 15,
                        },
                        "industry_position": "高端制造与核心硬件基础",
                        "business_model": "技术研发、制造交付、设备材料协同、产业链配套",
                        "behavior_description": "半导体以精密制造、规则标准和硬件纪律为主。",
                    },
                    {
                        "subcategory_id": "tech_ai",
                        "category_id": "tech",
                        "subcategory_name": "AI应用",
                        "main_element": "fire",
                        "secondary_element": "wood",
                        "element_scores": {
                            "wood": 30,
                            "fire": 40,
                            "earth": 10,
                            "metal": 10,
                            "water": 10,
                        },
                        "industry_position": "应用层与场景扩散层",
                        "business_model": "软件服务、工具订阅、内容生成、效率提升",
                        "behavior_description": "AI应用以传播、应用、创新扩张为主。",
                    },
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def write_csv(self, path, rows):
        with path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["board_type", "board_code", "board_name", "source", "member_count", "updated_at", "confidence"],
            )
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
