import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.sync_astock_industries import clean_board, sync_astock_industries
from wuxing_stock_app import database


class SyncAstockIndustriesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test.db"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_clean_board(self):
        board = clean_board(
            board_type="industry",
            board_code=" BK0428 ",
            board_name=" 电力行业 ",
            member_count=3,
            updated_at="2026-06-29T16:00:00",
        )

        self.assertEqual(board["board_code"], "BK0428")
        self.assertEqual(board["board_name"], "电力行业")
        self.assertEqual(board["source"], "eastmoney_push2_clist")
        self.assertEqual(board["confidence"], 100)

    def test_sync_with_injected_fetchers_writes_sqlite_and_csv(self):
        def fake_boards(board_type):
            if board_type == "industry":
                return [{"board_code": "BK0001", "board_name": "测试行业"}]
            return [{"board_code": "BK0002", "board_name": "测试概念"}]

        def fake_members(board):
            return [
                {
                    "board_code": board["board_code"],
                    "board_name": board["board_name"],
                    "stock_code": "600000",
                    "stock_name": "浦发银行",
                    "updated_at": "",
                },
                {
                    "board_code": board["board_code"],
                    "board_name": board["board_name"],
                    "stock_code": "000001",
                    "stock_name": "平安银行",
                    "updated_at": "",
                },
            ]

        with patch("scripts.sync_astock_industries.INDUSTRY_CSV", Path(self.tmpdir.name) / "astock_industry_raw.csv"), patch(
            "scripts.sync_astock_industries.CONCEPT_CSV", Path(self.tmpdir.name) / "astock_concept_raw.csv"
        ), patch("scripts.sync_astock_industries.MEMBERS_CSV", Path(self.tmpdir.name) / "astock_board_members.csv"):
            result = sync_astock_industries(
                db_path=self.db_path,
                board_fetcher=fake_boards,
                member_fetcher=fake_members,
                updated_at="2026-06-29T16:00:00",
            )

            self.assertEqual(result["industry_count"], 1)
            self.assertEqual(result["concept_count"], 1)
            self.assertEqual(result["member_count"], 4)

            boards = database.fetch_all("SELECT * FROM astock_boards ORDER BY board_code", db_path=self.db_path)
            members = database.fetch_all("SELECT * FROM astock_board_members ORDER BY board_code, stock_code", db_path=self.db_path)
            self.assertEqual(len(boards), 2)
            self.assertEqual(boards[0]["member_count"], 2)
            self.assertEqual(boards[0]["confidence"], 100)
            self.assertEqual(len(members), 4)
            self.assertEqual(members[0]["source"], "eastmoney_push2_clist")
            self.assertEqual(members[0]["confidence"], 100)

            self.assert_csv_has_fields(Path(self.tmpdir.name) / "astock_industry_raw.csv")
            self.assert_csv_has_fields(Path(self.tmpdir.name) / "astock_concept_raw.csv")
            with (Path(self.tmpdir.name) / "astock_board_members.csv").open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                self.assertEqual(
                    reader.fieldnames,
                    ["board_code", "board_name", "stock_code", "stock_name", "source", "updated_at", "confidence"],
                )
                self.assertEqual(len(list(reader)), 4)

    def assert_csv_has_fields(self, path):
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            self.assertEqual(
                reader.fieldnames,
                ["board_type", "board_code", "board_name", "source", "member_count", "updated_at", "confidence"],
            )
            self.assertEqual(len(list(reader)), 1)


if __name__ == "__main__":
    unittest.main()
