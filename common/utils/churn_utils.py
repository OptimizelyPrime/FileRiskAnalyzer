"""
churn_utils.py
Utility functions for calculating code churn scores using pandas.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime



def calculate_file_churn_score(commit_history: List[Dict[str, str]], total_commits: int, since: Optional[str] = None) -> float:
    """
    Calculate the normalized churn score for a file as a percentage of total commits.

    Args:
        commit_history (List[Dict[str, str]]): List of commit dicts for a file (with 'commit_hash').
        total_commits (int): The total number of commits in the repo for normalization.
        since (Optional[str]): ISO date string. Only count commits after this date. If None, count all.

    Returns:
        float: Normalized churn score as a percentage.
    """
    df = pd.DataFrame(commit_history)
    if since:
        since_dt = pd.to_datetime(since)
        if 'date' in df:
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= since_dt]

    file_commits = df['commit_hash'].nunique() if 'commit_hash' in df else 0

    if total_commits == 0:
        return 0.0

    churn_percentage = (file_commits / total_commits) * 100
    return round(churn_percentage, 2)


def calculate_repo_churn_scores(file_histories: Dict[str, List[Dict[str, str]]], since: Optional[str] = None) -> Dict[str, float]:
    """
    Calculate normalized churn scores for all files in a repo.

    Args:
        file_histories (Dict[str, List[Dict[str, str]]]): Mapping of file paths to commit histories.
        since (Optional[str]): ISO date string. Only count commits after this date. If None, count all.

    Returns:
        Dict[str, float]: Mapping of file names to normalized churn scores (%).
    """
    churn_scores = {}

    # First, determine the total number of unique commits in the given histories, respecting 'since'
    all_commits_df_list = []
    for history in file_histories.values():
        all_commits_df_list.append(pd.DataFrame(history))

    if not all_commits_df_list:
        return {}

    repo_df = pd.concat(all_commits_df_list)

    if since:
        since_dt = pd.to_datetime(since)
        if 'date' in repo_df:
            repo_df['date'] = pd.to_datetime(repo_df['date'])
            repo_df = repo_df[repo_df['date'] >= since_dt]

    total_repo_commits = repo_df['commit_hash'].nunique() if 'commit_hash' in repo_df else 0

    for file_path, history in file_histories.items():
        # The file-level calculation also filters by 'since', so we pass it down.
        churn_scores[file_path] = calculate_file_churn_score(history, total_repo_commits, since)

    return churn_scores
