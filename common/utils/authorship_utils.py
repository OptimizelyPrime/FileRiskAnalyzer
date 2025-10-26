```python
"""
authorship_utils.py
Utility functions for extracting authorship data using GitPython.
"""

from git import Repo
from typing import List, Dict


def get_file_authorship(repo_path: str, file_path: str) -> List[Dict[str, str]]:
    """
    Get authorship data for each line in a file using git blame.

    Args:
        repo_path (str): Path to the local git repository.
        file_path (str): Path to the file, relative to the repo root.

    Returns:
        List[Dict[str, str]]: List of dicts with line number, author, and commit hash for each line.
    """
    repo = Repo(repo_path)
    blame_data = repo.blame('HEAD', file_path)

    flat_blame = (
        (commit, line)
        for commit, lines in blame_data
        for line in lines
    )

    return [
        {
            'line_number': line_num,
            'author': commit.author.name,
            'commit_hash': commit.hexsha,
            'date': commit.committed_datetime.isoformat(),
            'line': line.strip(),
        }
        for line_num, (commit, line) in enumerate(flat_blame, 1)
    ]


def get_repo_authorship(repo_path: str, file_paths: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """
    Get authorship data for all files in the repo.

    Args:
        repo_path (str): Path to the local git repository.
        file_paths (List[str]): List of file paths to process.

    Returns:
        Dict[str, List[Dict[str, str]]]: Mapping of file paths to their line authorship data.
    """
    return {
        file_path: get_file_authorship(repo_path, file_path)
        for file_path in file_paths
    }
```