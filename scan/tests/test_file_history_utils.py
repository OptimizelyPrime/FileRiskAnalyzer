import unittest
from unittest.mock import patch, MagicMock
from scan.utils.file_history_utils import get_file_commit_history, get_repo_files_commit_history
from datetime import datetime

class TestFileHistoryUtils(unittest.TestCase):

    @patch('scan.utils.file_history_utils.Repo')
    def test_get_file_commit_history(self, mock_repo):
        mock_commit = MagicMock()
        mock_commit.hexsha = '12345'
        mock_commit.author.name = 'Test Author'
        mock_commit.committed_datetime = datetime.now()
        mock_commit.message = 'Test commit'

        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.iter_commits.return_value = [mock_commit]

        history = get_file_commit_history('dummy_repo_path', 'dummy_file_path')

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['commit_hash'], '12345')

    @patch('scan.utils.file_history_utils.Repo')
    @patch('scan.utils.file_history_utils.get_file_commit_history')
    def test_get_repo_files_commit_history(self, mock_get_commit_history, mock_repo):
        # Mock the tree traversal
        mock_blob = MagicMock()
        mock_blob.type = 'blob'
        mock_blob.path = 'file1.py'

        mock_tree = MagicMock()
        mock_tree.traverse.return_value = [mock_blob]

        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.head.commit.tree = mock_tree

        mock_get_commit_history.return_value = [{'commit_hash': '12345'}]

        histories = get_repo_files_commit_history('dummy_repo_path')

        self.assertIn('file1.py', histories)
        self.assertEqual(len(histories['file1.py']), 1)
        mock_get_commit_history.assert_called_once()

if __name__ == '__main__':
    unittest.main()
