import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
import shutil
from common.utils.repo_utils import clone_repo, find_source_files

class TestRepoUtils(unittest.TestCase):

    @patch('git.Repo.clone_from')
    def test_clone_repo(self, mock_clone_from):
        mock_repo = MagicMock()
        mock_clone_from.return_value = mock_repo
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('tempfile.mkdtemp', return_value=temp_dir):
                repo_url = "https://github.com/user/repo.git"
                repo, cloned_path = clone_repo(repo_url, 'main')
                mock_clone_from.assert_called_once_with(repo_url, temp_dir, branch='main')
                self.assertEqual(cloned_path, temp_dir)
                self.assertEqual(repo, mock_repo)

    @patch('git.Repo.clone_from')
    def test_clone_repo_with_ignore_revs_file(self, mock_clone_from):
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Create a dummy .git-blame-ignore-revs file
            with open(os.path.join(temp_dir, '.git-blame-ignore-revs'), 'w') as f:
                f.write('some_commit_hash')

            # 2. Mock the repo object and its config_writer
            mock_repo = MagicMock()
            mock_config_writer = MagicMock()
            mock_repo.config_writer.return_value.__enter__.return_value = mock_config_writer
            mock_clone_from.return_value = mock_repo

            with patch('tempfile.mkdtemp', return_value=temp_dir):
                # 3. Call clone_repo
                clone_repo("https://github.com/user/repo.git", 'main')

                # 4. Assert that set_value was called
                mock_config_writer.set_value.assert_called_once_with('blame', 'ignoreRevsFile', '.git-blame-ignore-revs')

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
