import tempfile
import unittest
from pathlib import Path

from wuxing_stock_app.modules.auth_engine import has_access, use_unlock_code
from wuxing_stock_app.modules.payment_engine import (
    confirm_payment,
    create_payment_order,
    get_payment_order,
)


class PaymentEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test.db"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_create_alipay_order(self):
        order = create_payment_order(
            "PAID_DAY",
            "day:2026-06-29",
            990,
            "ALIPAY",
            db_path=self.db_path,
        )

        self.assertEqual(order["access_type"], "PAID_DAY")
        self.assertEqual(order["payment_channel"], "ALIPAY")
        self.assertEqual(order["status"], "PENDING")
        self.assertEqual(get_payment_order(order["order_no"], db_path=self.db_path)["amount"], 990)

    def test_create_wechat_order_and_confirm_payment_creates_unlock_code(self):
        order = create_payment_order(
            "PAID_SUBCATEGORY_SINGLE",
            "subcategory:tech_semiconductor",
            1990,
            "WECHAT",
            db_path=self.db_path,
        )
        result = confirm_payment(
            order["order_no"],
            "WX-TRADE-001",
            max_use_count=2,
            db_path=self.db_path,
        )

        self.assertEqual(result["order"]["status"], "PAID")
        self.assertEqual(result["order"]["external_trade_no"], "WX-TRADE-001")
        self.assertEqual(result["unlock_code"]["max_use_count"], 2)
        self.assertEqual(result["unlock_code"]["used_count"], 0)

    def test_unlock_code_records_use_count(self):
        order = create_payment_order(
            "PAID_DAY_RANKING",
            "ranking:day:2026-06-29",
            990,
            "ALIPAY",
            db_path=self.db_path,
        )
        result = confirm_payment(order["order_no"], "ALI-TRADE-001", max_use_count=2, db_path=self.db_path)
        code = result["unlock_code"]["code"]

        first_use = use_unlock_code(code, "PAID_DAY_RANKING", "ranking:day:2026-06-29", db_path=self.db_path)
        second_use = use_unlock_code(code, "PAID_DAY_RANKING", "ranking:day:2026-06-29", db_path=self.db_path)

        self.assertEqual(first_use["used_count"], 1)
        self.assertEqual(second_use["used_count"], 2)
        self.assertEqual(second_use["status"], "USED")

    def test_free_access_types_do_not_need_unlock_code(self):
        self.assertTrue(has_access("FREE_YEAR", "year:2026", db_path=self.db_path))
        self.assertTrue(has_access("FREE_WEEK", "week:2026-W27", db_path=self.db_path))
        self.assertTrue(has_access("FREE_CATEGORY", "category:tech", db_path=self.db_path))

    def test_paid_access_requires_unlock_code(self):
        self.assertFalse(has_access("PAID_DAY", "day:2026-06-29", db_path=self.db_path))

    def test_invalid_payment_channel_raises_error(self):
        with self.assertRaises(ValueError):
            create_payment_order("PAID_DAY", "day:2026-06-29", 990, "CARD", db_path=self.db_path)

    def test_free_access_type_cannot_create_payment_order(self):
        with self.assertRaises(ValueError):
            create_payment_order("FREE_YEAR", "year:2026", 990, "ALIPAY", db_path=self.db_path)


if __name__ == "__main__":
    unittest.main()
