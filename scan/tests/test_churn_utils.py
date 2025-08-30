import unittest
from scan.utils.churn_utils import calculate_file_churn_score, calculate_repo_churn_scores
from datetime import datetime, timedelta
import pandas as pd

class TestChurnUtils(unittest.TestCase):

    def test_calculate_file_churn_score(self):
        commit_history = [
            {'commit_hash': '1', 'date': (datetime.now() - timedelta(days=1)).isoformat()},
            {'commit_hash': '2', 'date': (datetime.now() - timedelta(days=2)).isoformat()},
            {'commit_hash': '1', 'date': (datetime.now() - timedelta(days=3)).isoformat()}
        ]

        score = calculate_file_churn_score(commit_history)
        self.assertEqual(score, 2)

        since_date = (datetime.now() - timedelta(days=1.5))
        score_since = calculate_file_churn_score(commit_history, since=since_date.isoformat())
        self.assertEqual(score_since, 1)

    def test_calculate_repo_churn_scores(self):
        file_histories = {
            'file1.py': [{'commit_hash': '1'}, {'commit_hash': '2'}],
            'file2.py': [{'commit_hash': '3'}]
        }

        churn_scores = calculate_repo_churn_scores(file_histories)

        self.assertEqual(len(churn_scores), 2)
        self.assertEqual(churn_scores['file1.py'], 2)
        self.assertEqual(churn_scores['file2.py'], 1)

if __name__ == '__main__':
    unittest.main()
