import unittest

from wuxing_stock_app.modules.industry_engine import (
    get_category_profile,
    get_subcategory_profile,
    list_categories,
    list_subcategories,
)


class IndustryEngineTest(unittest.TestCase):
    def test_list_categories_returns_free_profiles(self):
        categories = list_categories()

        self.assertGreaterEqual(len(categories), 1)
        self.assertTrue(categories[0]["is_free"])
        self.assertTrue(categories[0]["access_granted"])
        self.assertIn("main_element", categories[0])
        self.assertIn("secondary_element", categories[0])
        self.assertIn("element_scores", categories[0])
        self.assertIn("behavior_description", categories[0])
        self.assertIn("risk_tags", categories[0])

    def test_get_category_profile_is_free(self):
        category = get_category_profile("tech")

        self.assertEqual(category["category_id"], "tech")
        self.assertFalse(category["paid_required"])
        self.assertTrue(category["access_granted"])
        self.assertEqual(category["main_element"], "metal")

    def test_get_subcategory_profile_without_access_returns_locked_preview(self):
        subcategory = get_subcategory_profile("tech_semiconductor")

        self.assertEqual(subcategory["subcategory_id"], "tech_semiconductor")
        self.assertTrue(subcategory["paid_required"])
        self.assertFalse(subcategory["access_granted"])
        self.assertTrue(subcategory["locked"])
        self.assertNotIn("element_scores", subcategory)
        self.assertIn("unlock_hint", subcategory)

    def test_get_subcategory_profile_with_access_returns_full_profile(self):
        subcategory = get_subcategory_profile("tech_semiconductor", has_access=True)

        self.assertEqual(subcategory["subcategory_id"], "tech_semiconductor")
        self.assertTrue(subcategory["paid_required"])
        self.assertTrue(subcategory["access_granted"])
        self.assertFalse(subcategory["locked"])
        self.assertEqual(subcategory["main_element"], "metal")
        self.assertEqual(subcategory["secondary_element"], "fire")
        self.assertIn("element_scores", subcategory)
        self.assertIn("behavior_description", subcategory)
        self.assertIn("risk_tags", subcategory)

    def test_get_subcategory_profile_with_unlocked_ids_returns_full_profile(self):
        subcategory = get_subcategory_profile(
            "tech_semiconductor",
            unlocked_subcategory_ids=["tech_semiconductor"],
        )

        self.assertTrue(subcategory["access_granted"])
        self.assertIn("element_scores", subcategory)

    def test_list_subcategories_can_filter_by_category(self):
        subcategories = list_subcategories("tech", has_access=True)

        self.assertGreaterEqual(len(subcategories), 1)
        self.assertTrue(all(item["category_id"] == "tech" for item in subcategories))
        self.assertTrue(all(item["access_granted"] for item in subcategories))

    def test_unknown_category_raises_error(self):
        with self.assertRaises(ValueError):
            get_category_profile("unknown")

    def test_unknown_subcategory_raises_error(self):
        with self.assertRaises(ValueError):
            get_subcategory_profile("unknown")


if __name__ == "__main__":
    unittest.main()
