import unittest
from common.utils.knowledge_concentration_utils import calculate_knowledge_concentration, calculate_repo_knowledge_concentration
from datetime import datetime, timedelta

class TestKnowledgeConcentrationUtils(unittest.TestCase):

    def test_calculate_knowledge_concentration(self):
        authorship_data = [
            {'author': 'A', 'date': (datetime.now() - timedelta(days=1)).isoformat()},
            {'author': 'A', 'date': (datetime.now() - timedelta(days=2)).isoformat()},
            {'author': 'B', 'date': (datetime.now() - timedelta(days=3)).isoformat()}
        ]

        result = calculate_knowledge_concentration(authorship_data)
        self.assertEqual(result['top_author'], 'A')
        self.assertAlmostEqual(result['top_author_pct'], 66.67, places=2)

        since_date = datetime.now() - timedelta(days=1.5)
        result_since = calculate_knowledge_concentration(authorship_data, since=since_date)
        self.assertEqual(result_since['top_author'], 'A')
        self.assertAlmostEqual(result_since['top_author_pct'], 100.0, places=2)

    def test_calculate_repo_knowledge_concentration(self):
        authorship_data = {
            'file1.py': [
                {'author': 'A'}, {'author': 'B'}
            ],
            'file2.py': [
                {'author': 'C'}, {'author': 'C'}, {'author': 'C'}
            ]
        }

        scores = calculate_repo_knowledge_concentration(authorship_data)

        self.assertEqual(scores['file1.py']['top_author'], 'A') # or B, depending on pandas implementation
        self.assertAlmostEqual(scores['file1.py']['top_author_pct'], 50.0, places=2)
        self.assertEqual(scores['file2.py']['top_author'], 'C')
        self.assertAlmostEqual(scores['file2.py']['top_author_pct'], 100.0, places=2)

if __name__ == '__main__':
    unittest.main()
