"""
authorship_utils.py
Utility functions for extracting authorship data using GitPython.
"""

from git import Repo
from typing import List, Dict
import os


def get_file_authorship(repo_path: str, file_path: str) -> List[Dict[str, str]]:
    """
    Get authorship data for each line in a file using git blame.

    Args:
        repo_path (str): Path to the local git repository.
        file_path (str): Path to the file (relative to repo root).

    Returns:
        List[Dict[str, str]]: List of dicts with line number, author, and commit hash for each line.
    """
    repo = Repo(repo_path)
    rel_path = os.path.relpath(file_path, repo_path)
    blame_data = repo.blame('HEAD', rel_path)
    authorship = []
    line_num = 1
    for commit, lines in blame_data:
        for line in lines:
            authorship.append({
                'line_number': line_num,
                'author': commit.author.name,
                'commit_hash': commit.hexsha,
                'date': commit.committed_datetime.isoformat(),
                'line': line.strip(),
            })
            line_num += 1
    return authorship


def get_repo_authorship(repo_path: str, file_paths: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """
    Get authorship data for all files in the repo.

    Args:
        repo_path (str): Path to the local git repository.
        file_paths (List[str]): List of file paths to process.

    Returns:
        Dict[str, List[Dict[str, str]]]: Mapping of file paths to their line authorship data.
    """
    authorship_data = {}
    for file_path in file_paths:
        authorship_data[file_path] = get_file_authorship(repo_path, file_path)
    return authorship_data
