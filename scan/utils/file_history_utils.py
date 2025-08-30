"""
file_history_utils.py
Utility functions for extracting file commit history using GitPython.
"""

from git import Repo
from typing import List, Dict
import os


from typing import Optional
from datetime import datetime

def get_file_commit_history(repo_path: str, file_path: str, since: Optional[datetime] = None) -> List[Dict[str, str]]:
    """
    Get the commit history for a specific file in a git repository.

    Args:
        repo_path (str): Path to the local git repository.
        file_path (str): Path to the file (relative to repo root).
        since (Optional[datetime]): A datetime object to filter commits since.

    Returns:
        List[Dict[str, str]]: List of commit hashes and messages that modified the file.
    """
    repo = Repo(repo_path)
    commits = []
    rel_path = os.path.relpath(file_path, repo_path)
    for commit in repo.iter_commits(paths=rel_path, since=since):
        commits.append({
            'commit_hash': commit.hexsha,
            'author': commit.author.name,
            'date': commit.committed_datetime.isoformat(),
            'message': commit.message.strip(),
        })
    return commits


def get_repo_files_commit_history(repo_path: str, since: Optional[datetime] = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Get the commit history for every file in the current branch of a git repository.

    Args:
        repo_path (str): Path to the local git repository.
        since (Optional[datetime]): A datetime object to filter commits since.

    Returns:
        Dict[str, List[Dict[str, str]]]: Mapping of file paths to their commit histories.
    """
    repo = Repo(repo_path)
    file_histories = {}
    tree = repo.head.commit.tree
    for blob in tree.traverse():
        if blob.type == 'blob':
            file_path = os.path.join(repo_path, blob.path)
            file_histories[blob.path] = get_file_commit_history(repo_path, file_path, since=since)
    return file_histories
