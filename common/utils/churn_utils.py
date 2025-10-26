```python
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
    except (ValueError, TypeError):
        return None

def _to_aware_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Converts a datetime object to an aware UTC datetime."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def _is_commit_after(entry: Dict[str, Any], since_dt: datetime) -> bool:
    """Check if a commit entry's date is at or after since_dt."""
    commit_date = _to_aware_utc(_parse_datetime(entry.get('date')))
    return commit_date is not None and commit_date >= since_dt

def _get_filtered_commit_hashes(
    history: List[Dict[str, Any]], since_dt: Optional[datetime]
) -> Set[str]:
    """Extracts unique, valid commit hashes from a history, filtered by date."""
    if not history:
        return set()

    return {
        entry['commit_hash']
        for entry in history
        if isinstance(entry, dict)
        and entry.get('commit_hash')
        and (since_dt is None or _is_commit_after(entry, since_dt))
    }

def calculate_file_churn_score(
    commit_history: List[Dict[str, Any]], total_commits: int, since: Optional[str] = None
) -> float:
    """
    Calculate the normalized churn score for a file as a percentage of total commits.

    Args:
        commit_history (List[Dict[str, Any]]): List of commit dicts for a file.
        total_commits (int): The total number of commits in the repo for normalization.
        since (Optional[str]): ISO date string. Only count commits after this date.

    Returns:
        float: Normalized churn score as a percentage.
    """
    if total_commits == 0:
        return 0.0

    since_dt = _to_aware_utc(_parse_datetime(since)) if since else None
    file_commits_count = len(_get_filtered_commit_hashes(commit_history, since_dt))

    churn_percentage = (file_commits_count / total_commits) * 100
    return round(churn_percentage, 2)

def calculate_repo_churn_scores(
    file_histories: Dict[str, List[Dict[str, Any]]], since: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate normalized churn scores for all files in a repo.

    Args:
        file_histories (Dict[str, List[Dict[str, Any]]]): File paths to commit histories.
        since (Optional[str]): ISO date string. Only count commits after this date.

    Returns:
        Dict[str, float]: Mapping of file names to normalized churn scores (%).
    """
    since_dt = _to_aware_utc(_parse_datetime(since)) if since else None
    histories = file_histories or {}

    file_commit_sets = {
        file_path: _get_filtered_commit_hashes(history, since_dt)
        for file_path, history in histories.items()
    }

    all_repo_commits = set.union(*file_commit_sets.values()) if file_commit_sets else set()
    total_repo_commits = len(all_repo_commits)

    if total_repo_commits == 0:
        return {file_path: 0.0 for file_path in histories}

    return {
        file_path: round((len(commit_set) / total_repo_commits) * 100, 2)
        for file_path, commit_set in file_commit_sets.items()
    }
```