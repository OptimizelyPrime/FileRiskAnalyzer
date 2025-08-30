import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
from scan.utils.repo_utils import clone_repo, find_source_files

class TestRepoUtils(unittest.TestCase):

    @patch('git.Repo.clone_from')
    def test_clone_repo(self, mock_clone_from):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('tempfile.mkdtemp', return_value=temp_dir):
                repo_url = "https://github.com/user/repo.git"
                cloned_path = clone_repo(repo_url)
                mock_clone_from.assert_called_once_with(repo_url, temp_dir)
                self.assertEqual(cloned_path, temp_dir)

    def test_find_source_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy directory structure
            os.makedirs(os.path.join(temp_dir, 'dir1'))
            with open(os.path.join(temp_dir, 'file1.py'), 'w') as f:
                f.write('pass')
            with open(os.path.join(temp_dir, 'dir1', 'file2.py'), 'w') as f:
                f.write('pass')

            # Create a .git directory to be ignored
            os.makedirs(os.path.join(temp_dir, '.git'))
            with open(os.path.join(temp_dir, '.git', 'config'), 'w') as f:
                f.write('[core]')

            found_files = find_source_files(temp_dir)

            # Use relative paths for comparison
            relative_files = sorted([os.path.relpath(p, temp_dir) for p in found_files])

            self.assertEqual(len(relative_files), 2)
            self.assertIn('file1.py', relative_files)
            self.assertIn(os.path.join('dir1', 'file2.py'), relative_files)

if __name__ == '__main__':
    unittest.main()
