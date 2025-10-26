"""
knowledge_concentration_utils.py
Utility functions for scoring knowledge concentration risk without heavy dependencies.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


def _parse_datetime(value) -> Optional[datetime]:
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


def calculate_knowledge_concentration(authorship_data: List[Dict[str, str]], since: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Calculate the percentage of lines owned by the top author and a risk score for a function.

    Args:
        authorship_data (List[Dict[str, str]]): List of line authorship dicts for a function.
        since (Optional[datetime]): A datetime object. Only count lines authored after this date.

    Returns:
        Dict[str, Any]: Dict with top author, percentage, and risk score (0-1).
    """
    # Optional filter by since; exclude entries without a parseable date when filtering is requested
    rows = authorship_data or []
    if since is not None:
        since_dt = _to_aware_utc(_parse_datetime(since))
        if since_dt is not None:
            filtered = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                dt = _to_aware_utc(_parse_datetime(row.get('date')))
                if dt is not None and dt >= since_dt:
                    filtered.append(row)
            rows = filtered

    # Count authors
    author_counts: Dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        author = row.get('author')
        if author is None:
            continue
        author_counts[author] = author_counts.get(author, 0) + 1

    total = sum(author_counts.values())
    if total == 0:
        return {'top_author': None, 'top_author_pct': 0.0, 'risk_score': 0.0}

    top_author = max(author_counts, key=lambda a: author_counts[a])
    top_author_pct = author_counts[top_author] / total
    # Risk score: higher percentage = higher risk (siloed knowledge)
    risk_score = top_author_pct
    return {
        'top_author': top_author,
        'top_author_pct': round(top_author_pct * 100, 2),
        'risk_score': round(risk_score, 2)
    }


def calculate_repo_knowledge_concentration(authorship_data: Dict[str, Dict[str, List[Dict[str, str]]]], since: Optional[datetime] = None) -> Dict[str, Dict[str, Any]]:
    """
    Calculate knowledge concentration scores for all functions in all files in a repo.

    Args:
        authorship_data (Dict[str, Dict[str, List[Dict[str, str]]]]): Mapping of file paths to function names to line authorship data.
        since (Optional[datetime]): A datetime object. Only count lines authored after this date.

    Returns:
        Dict[str, Dict[str, Any]]: Mapping of file paths to function names to knowledge concentration scores.
    """
    scores = {}
    for file_path, func_map in authorship_data.items():
        # If func_map is a list, treat as file-level authorship
        if isinstance(func_map, list):
            scores[file_path] = calculate_knowledge_concentration(func_map, since)
        elif isinstance(func_map, dict):
            # Merge all lines from all functions for file-level metric
            all_lines = []
            for lines in func_map.values():
                all_lines.extend(lines)
            scores[file_path] = calculate_knowledge_concentration(all_lines, since)
        else:
            scores[file_path] = {'top_author': None, 'top_author_pct': 0.0, 'risk_score': 0.0}
    return scores
