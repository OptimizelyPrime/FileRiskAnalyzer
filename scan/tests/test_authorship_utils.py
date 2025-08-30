import unittest
from unittest.mock import patch, MagicMock
from scan.utils.authorship_utils import get_file_authorship, get_repo_authorship
from datetime import datetime

class TestAuthorshipUtils(unittest.TestCase):

    @patch('scan.utils.authorship_utils.Repo')
    def test_get_file_authorship(self, mock_repo):
        # Mock the blame data
        mock_commit = MagicMock()
        mock_commit.author.name = 'Test Author'
        mock_commit.hexsha = '12345'
        mock_commit.committed_datetime = datetime.now()

        blame_entry = (mock_commit, ['line 1', 'line 2'])

        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.blame.return_value = [blame_entry]

        # The Repo object is now mocked, so the path doesn't matter
        authorship = get_file_authorship('dummy_repo_path', 'dummy_file_path')

        self.assertEqual(len(authorship), 2)
        self.assertEqual(authorship[0]['author'], 'Test Author')
        self.assertEqual(authorship[1]['line'], 'line 2')

    @patch('scan.utils.authorship_utils.get_file_authorship')
    def test_get_repo_authorship(self, mock_get_file_authorship):
        mock_get_file_authorship.return_value = [{'author': 'Test Author'}]

        file_paths = ['file1.py', 'file2.py']
        authorship_data = get_repo_authorship('dummy_repo_path', file_paths)

        self.assertEqual(len(authorship_data), 2)
        self.assertIn('file1.py', authorship_data)
        self.assertEqual(mock_get_file_authorship.call_count, 2)

if __name__ == '__main__':
    unittest.main()
