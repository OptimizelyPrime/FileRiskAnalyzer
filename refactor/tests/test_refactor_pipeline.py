import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime

# Add the project root to the Python path to allow for imports from src and common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from refactor.src.business_logic import refactor_pipeline

class TestRefactorPipeline(unittest.TestCase):

    @patch('refactor.src.business_logic.refactor_pipeline.clone_repo')
    @patch('refactor.src.business_logic.refactor_pipeline.extract_code_from_files')
    @patch('refactor.src.business_logic.refactor_pipeline.refactor_code_using_gemini')
    @patch('refactor.src.business_logic.refactor_pipeline.save_refactored_code')
    @patch('refactor.src.business_logic.refactor_pipeline.create_pull_request')
    @patch('shutil.rmtree')
    @patch('os.path.exists', return_value=True)
    @patch('refactor.src.business_logic.refactor_pipeline.datetime')
    def test_run_pipeline(self, mock_datetime, mock_exists, mock_rmtree, mock_create_pr, mock_save_refactored_code, mock_refactor_code, mock_extract_code, mock_clone_repo):
        # Arrange
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        mock_clone_repo.return_value = (mock_repo, 'temp_dir')
        mock_extract_code.return_value = {'file1.py': 'print("hello")'}
        mock_refactor_code.return_value = 'print("hello world")'

        mock_now = MagicMock()
        mock_now.strftime.return_value = "20230101"
        mock_datetime.now.return_value = mock_now

        expected_branch_name = "ai-refactor-20230101"
        expected_refactored_code = {'file1.py': 'print("hello world")'}

        repo_url = 'https://github.com/example/repo.git'
        branch = 'main'
        files = ['file1.py']

        # Act
        refactor_pipeline.run(repo_url, branch, files)

        # Assert
        mock_clone_repo.assert_called_once_with(repo_url, branch)
        mock_repo.create_head.assert_called_once_with(expected_branch_name)
        mock_extract_code.assert_called_once_with('temp_dir', files)
        mock_refactor_code.assert_called_once_with('print("hello")')
        mock_save_refactored_code.assert_called_once_with('temp_dir', expected_refactored_code)
        mock_repo.git.add.assert_called_once_with(all=True)
        mock_repo.index.commit.assert_called_once_with("AI-powered refactoring")
        mock_remote.push.assert_called_once_with(expected_branch_name)
        mock_create_pr.assert_called_once_with(repo_url, expected_branch_name, branch)
        mock_rmtree.assert_called_once_with('temp_dir')

if __name__ == '__main__':
    unittest.main()
