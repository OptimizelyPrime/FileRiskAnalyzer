"""
churn_utils.py
Utility functions for calculating code churn scores without heavy dependencies.
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone



def _parse_datetime(value: Any) -> Optional[datetime]:
    """Best-effort ISO parser that tolerates timezone 'Z'."""
    if isinstance(value, datetime):
        return value
    if value is None:
        return None
    try:
        s = str(value)
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        return datetime.fromisoformat(s)
    except Exception:
        return None

def _to_aware_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


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
    since_dt = _to_aware_utc(_parse_datetime(since)) if since is not None else None

    commits: Set[str] = set()
    for entry in commit_history or []:
        commit_hash = entry.get('commit_hash') if isinstance(entry, dict) else None
        if not commit_hash:
            continue
        if since_dt is not None:
            dt = _to_aware_utc(_parse_datetime(entry.get('date'))) if isinstance(entry, dict) else None
            if dt is None or dt < since_dt:
                continue
        commits.add(commit_hash)

    file_commits = len(commits)

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
    churn_scores: Dict[str, float] = {}

    # Determine the total number of unique commits in the given histories, respecting 'since'
    since_dt = _to_aware_utc(_parse_datetime(since)) if since is not None else None
    repo_commits: Set[str] = set()
    for history in (file_histories or {}).values():
        for entry in history or []:
            commit_hash = entry.get('commit_hash') if isinstance(entry, dict) else None
            if not commit_hash:
                continue
            if since_dt is not None:
                dt = _to_aware_utc(_parse_datetime(entry.get('date'))) if isinstance(entry, dict) else None
                if dt is None or dt < since_dt:
                    continue
            repo_commits.add(commit_hash)

    total_repo_commits = len(repo_commits)

    for file_path, history in (file_histories or {}).items():
        churn_scores[file_path] = calculate_file_churn_score(history, total_repo_commits, since)

    return churn_scores
