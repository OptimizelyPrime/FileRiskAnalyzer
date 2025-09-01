import unittest
from common.utils.churn_utils import calculate_file_churn_score, calculate_repo_churn_scores
from datetime import datetime, timedelta
import pandas as pd

class TestChurnUtils(unittest.TestCase):

    def test_calculate_file_churn_score(self):
        commit_history = [
            {'commit_hash': '1', 'date': (datetime.now() - timedelta(days=1)).isoformat()},
            {'commit_hash': '2', 'date': (datetime.now() - timedelta(days=2)).isoformat()},
            {'commit_hash': '1', 'date': (datetime.now() - timedelta(days=3)).isoformat()}
        ]

        # 2 unique commits out of a total of 10
        score = calculate_file_churn_score(commit_history, total_commits=10)
        self.assertAlmostEqual(score, 20.0)

        # With a 'since' date, 1 unique commit out of a total of 5
        since_date = (datetime.now() - timedelta(days=1.5))
        score_since = calculate_file_churn_score(commit_history, total_commits=5, since=since_date.isoformat())
        self.assertAlmostEqual(score_since, 20.0)

    def test_calculate_repo_churn_scores(self):
        file_histories = {
            'a/file1.py': [
                {'commit_hash': '1', 'date': (datetime.now() - timedelta(days=1)).isoformat()},
                {'commit_hash': '2', 'date': (datetime.now() - timedelta(days=2)).isoformat()}
            ],
            'b/file1.py': [
                {'commit_hash': '3', 'date': (datetime.now() - timedelta(days=3)).isoformat()}
            ],
            'file2.py': [
                {'commit_hash': '4', 'date': (datetime.now() - timedelta(days=4)).isoformat()}
            ]
        }

        churn_scores = calculate_repo_churn_scores(file_histories)

        # Total unique commits = 4
        self.assertEqual(len(churn_scores), 3)
        self.assertAlmostEqual(churn_scores['a/file1.py'], 50.0) # 2/4 * 100
        self.assertAlmostEqual(churn_scores['b/file1.py'], 25.0) # 1/4 * 100
        self.assertAlmostEqual(churn_scores['file2.py'], 25.0) # 1/4 * 100

        # With a 'since' date
        since_date = (datetime.now() - timedelta(days=2.5))
        churn_scores_since = calculate_repo_churn_scores(file_histories, since=since_date.isoformat())

        # Total unique commits since date = 2 ('1', '2')
        self.assertEqual(len(churn_scores_since), 3)
        self.assertAlmostEqual(churn_scores_since['a/file1.py'], 100.0) # 2/2 * 100
        self.assertAlmostEqual(churn_scores_since['b/file1.py'], 0.0) # 0/2 * 100
        self.assertAlmostEqual(churn_scores_since['file2.py'], 0.0) # 0/2 * 100

if __name__ == '__main__':
    unittest.main()
