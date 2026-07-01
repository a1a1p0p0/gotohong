import unittest

from wuxing_stock_app.modules.user_engine import record_user_action


class UserEngineTest(unittest.TestCase):
    def test_record_user_action_placeholder(self):
        result = record_user_action("view", "home")
        self.assertEqual(result["action"], "view")


if __name__ == "__main__":
    unittest.main()
