import unittest
from typing import Dict

# 🧠 Import your graph
from sale_graph import graph  # Replace with your actual module or script

class TestSalesAgent(unittest.TestCase):
    def setUp(self):
        """Setup minimal input data for validation."""
        self.input_data: Dict = {
            "data": {
                "sales": 12000,
                "cost": 4000,
                "customers": 100,
                "yesterday": {
                    "sales": 10000,
                    "cost": 3500,
                    "CAC": 35.0
                }
            }
        }

        self.expected_profit = 8000
        self.expected_cac = 40.0
        self.expected_alerts = [
            '⚠️ CAC has increased compared to yesterday.',
            '✅ Sales have increased compared to yesterday.'
        ]
        self.expected_recommendations = [
            '🟢 You are making a profit.',
            '📉 Consider improving your acquisition channels.',
            '📈 You may increase the marketing budget to leverage momentum.'
        ]

    def test_output_structure(self):
        """Ensure the graph returns all expected fields."""
        result = graph.invoke(self.input_data)
        self.assertIn("result", result)
        self.assertIn("alerts", result)
        self.assertIn("recommendations", result)

    def test_profit_and_cac_calculation(self):
        """Test logic accuracy: profit and CAC are correct."""
        result = graph.invoke(self.input_data)
        self.assertEqual(result["result"]["profit"], self.expected_profit)
        self.assertAlmostEqual(result["result"]["CAC"], self.expected_cac)

    def test_alert_generation(self):
        """Validate alerts logic and content."""
        result = graph.invoke(self.input_data)
        self.assertCountEqual(result["alerts"], self.expected_alerts)

    def test_recommendation_quality(self):
        """Assess the clarity and usefulness of recommendations."""
        result = graph.invoke(self.input_data)
        recs = result["recommendations"]

        # ✅ Ensure all expected recommendations are present
        self.assertCountEqual(recs, self.expected_recommendations)

        # ✅ Ensure recommendations are clear and actionable
        for rec in recs:
            self.assertIsInstance(rec, str)
            self.assertTrue(len(rec) > 10)  # not vague/empty

    def test_edge_case_zero_customers(self):
        """Ensure logic handles zero customers (avoid divide by zero)."""
        input_data = {
            "data": {
                "sales": 5000,
                "cost": 3000,
                "customers": 0,
                "yesterday": {"sales": 6000, "cost": 2800, "CAC": 28.0}
            }
        }
        result = graph.invoke(input_data)
        self.assertNotEqual(result["result"]["CAC"], float("inf"))
        self.assertTrue(isinstance(result["result"]["CAC"], float))

if __name__ == "__main__":
    unittest.main()
