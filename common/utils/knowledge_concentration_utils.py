"""
knowledge_concentration_utils.py
Utility functions for scoring knowledge concentration risk using pandas.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import pytz


def calculate_knowledge_concentration(authorship_data: List[Dict[str, str]], since: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Calculate the percentage of lines owned by the top author and a risk score for a function.

    Args:
        authorship_data (List[Dict[str, str]]): List of line authorship dicts for a function.
        since (Optional[datetime]): A datetime object. Only count lines authored after this date.

    Returns:
        Dict[str, Any]: Dict with top author, percentage, and risk score (0-1).
    """
    df = pd.DataFrame(authorship_data)
    if since:
        since_utc = since.replace(tzinfo=pytz.UTC)
        if 'date' in df:
            df['date'] = pd.to_datetime(df['date'], utc=True)
            df = df[df['date'] >= since_utc]
    if df.empty or 'author' not in df:
        return {'top_author': None, 'top_author_pct': 0.0, 'risk_score': 0.0}
    author_counts = df['author'].value_counts()
    top_author = author_counts.idxmax()
    top_author_pct = author_counts.max() / len(df)
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
