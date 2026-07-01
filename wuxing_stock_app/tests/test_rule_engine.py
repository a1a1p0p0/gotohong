import unittest

from wuxing_stock_app.modules.rule_engine import (
    calculate_all_relations,
    calculate_relation,
    get_element_definition,
    load_wuxing_rules,
)


class RuleEngineTest(unittest.TestCase):
    def test_element_definitions_are_energy_behaviors(self):
        rules = load_wuxing_rules()

        self.assertEqual(rules["elements"]["wood"]["energy_type"], "启动型动能")
        self.assertEqual(rules["elements"]["fire"]["energy_type"], "释放型动能")
        self.assertEqual(rules["elements"]["earth"]["energy_type"], "承载型动能")
        self.assertEqual(rules["elements"]["metal"]["energy_type"], "收敛型动能")
        self.assertEqual(rules["elements"]["water"]["energy_type"], "储备型动能")

    def test_get_element_definition(self):
        definition = get_element_definition("wood")

        self.assertEqual(definition["name"], "木")
        self.assertIn("从 0 到 1", definition["description"])

    def test_generating_relation(self):
        result = calculate_relation("water", "wood")

        self.assertEqual(result["relation_type"], "generating")
        self.assertEqual(result["score"], 30)
        self.assertIn("滋养", result["description"])

    def test_controlling_relation(self):
        result = calculate_relation("fire", "metal")

        self.assertEqual(result["relation_type"], "controlling")
        self.assertEqual(result["score"], -30)
        self.assertIn("压制", result["description"])

    def test_consuming_relation(self):
        result = calculate_relation("fire", "wood")

        self.assertEqual(result["relation_type"], "consuming")
        self.assertEqual(result["score"], -10)
        self.assertIn("消耗", result["description"])

    def test_over_controlling_relation(self):
        result = calculate_relation("fire", "metal", time_strength=90, industry_strength=40)

        self.assertEqual(result["relation_type"], "over_controlling")
        self.assertEqual(result["score"], -45)
        self.assertIn("过度", result["description"])

    def test_reverse_controlling_relation(self):
        result = calculate_relation("fire", "metal", time_strength=40, industry_strength=90)

        self.assertEqual(result["relation_type"], "reverse_controlling")
        self.assertEqual(result["score"], -20)
        self.assertIn("反向冲击", result["description"])

    def test_regulating_relation(self):
        result = calculate_relation("water", "earth")

        self.assertEqual(result["relation_type"], "regulating")
        self.assertEqual(result["score"], 8)
        self.assertIn("调节", result["description"])

    def test_transforming_relation_by_same_element(self):
        result = calculate_relation("wood", "wood")

        self.assertEqual(result["relation_type"], "transforming")
        self.assertEqual(result["score"], 20)
        self.assertIn("转化", result["description"])

    def test_transforming_relation_by_chain(self):
        result = calculate_relation("wood", "fire", secondary_element="earth")

        self.assertEqual(result["relation_type"], "transforming")
        self.assertEqual(result["score"], 20)

    def test_calculate_all_relations(self):
        result = calculate_all_relations("water", "wood", "fire")

        self.assertEqual(result["main"]["relation_type"], "generating")
        self.assertEqual(result["secondary"]["relation_type"], "controlling")

    def test_invalid_element_raises_error(self):
        with self.assertRaises(ValueError):
            calculate_relation("wind", "wood")


if __name__ == "__main__":
    unittest.main()
