import unittest
from scan.utils.file_health_utils import calculate_file_health_score

class TestFileHealthUtils(unittest.TestCase):

    def test_calculate_file_health_score(self):
        func_metrics = {
            'func1': {'maintainability_index': 80, 'lines_of_code': 20},
            'func2': {'maintainability_index': 60, 'lines_of_code': 30}
        }
        raw_churn = 10
        raw_kc_pct = 50.0

        # Expected AMS score: ((80 * 20) + (60 * 30)) / 50 = 68
        # Expected scaled churn: 3.26 * ln(11) = 7.82
        # Expected scaled kc: 3.26 * ln(51) = 12.8
        # Expected health score: 68 - 7.82 - 12.8 = 47.38

        health_score = calculate_file_health_score(func_metrics, raw_churn, raw_kc_pct)

        self.assertAlmostEqual(health_score, 47.37, places=2)

    def test_calculate_file_health_score_no_metrics(self):
        func_metrics = {}
        raw_churn = 0
        raw_kc_pct = 0

        # Expected AMS score: 100 (default)
        # Expected scaled churn: 0
        # Expected scaled kc: 0
        # Expected health score: 100

        health_score = calculate_file_health_score(func_metrics, raw_churn, raw_kc_pct)

        self.assertAlmostEqual(health_score, 100.0, places=2)

if __name__ == '__main__':
    unittest.main()
