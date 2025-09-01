"""
churn_utils.py
Utility functions for calculating code churn scores using pandas.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime



def calculate_file_churn_score(commit_history: List[Dict[str, str]], since: Optional[str] = None) -> int:
    """
    Calculate the churn score for a file based on the number of commits that touched any line in the file.

    Args:
        commit_history (List[Dict[str, str]]): List of commit dicts for a file (with 'commit_hash').
        since (Optional[str]): ISO date string. Only count commits after this date. If None, count all.

    Returns:
        int: Churn score (number of commits touching the file).
    """
    df = pd.DataFrame(commit_history)
    if since:
        since_dt = pd.to_datetime(since)
        if 'date' in df:
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= since_dt]
    return df['commit_hash'].nunique() if 'commit_hash' in df else 0



def calculate_repo_churn_scores(file_histories: Dict[str, List[Dict[str, str]]], since: Optional[str] = None) -> Dict[str, int]:
    """
    Calculate churn scores for all files in a repo (file-level).

    Args:
        file_histories (Dict[str, List[Dict[str, str]]]): Mapping of file paths to commit histories.
        since (Optional[str]): ISO date string. Only count commits after this date. If None, count all.

    Returns:
        Dict[str, int]: Mapping of file names to churn scores.
    """
    churn_scores = {}
    for file_path, history in file_histories.items():
        churn_scores[file_path] = calculate_file_churn_score(history, since)
    return churn_scores
