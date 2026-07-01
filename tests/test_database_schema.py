import tempfile
import unittest
from pathlib import Path

from wuxing_stock_app import database


class DatabaseSchemaTest(unittest.TestCase):
    def test_required_business_tables_are_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "schema.db"
            database.initialize_database(db_path)
            rows = database.fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table'",
                db_path=db_path,
            )
            table_names = {row["name"] for row in rows}

        self.assertTrue(
            {
                "calendar_ganzhi",
                "astock_boards",
                "astock_board_members",
                "industry_categories",
                "industry_subcategories",
                "astock_board_wuxing_profiles",
                "period_industry_rankings",
            }.issubset(table_names)
        )


if __name__ == "__main__":
    unittest.main()
