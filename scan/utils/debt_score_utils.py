"""
debt_score_utils.py
Utility functions for calculating unified Debt Score using pandas and configurable weights.
"""

import pandas as pd
from typing import Dict, Any, List
from utils.debt_weights import get_weights


def calculate_debt_scores(
    complexity_data: Dict[str, Dict[str, Any]],
    churn_scores: Dict[str, int],
    knowledge_concentration_scores: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """
    Calculate the unified Debt Score for each file and function.

    Args:
        complexity_data (Dict[str, Dict[str, Any]]): Dict mapping file path to function-metrics dict.
        churn_scores (Dict[str, int]): Churn scores per file.
        knowledge_concentration_scores (Dict[str, Dict[str, Any]]): Knowledge concentration scores per file.

    Returns:
        pd.DataFrame: DataFrame sorted by Debt Score.
    """
    weights = get_weights()
    rows = []
    for file_path, func_metrics in complexity_data.items():
        churn = churn_scores.get(file_path, 0)
        kc_score = knowledge_concentration_scores.get(file_path, {}).get('risk_score', 0)
        # func_metrics is now a dict: {function_name: {metric_dict}}
        for func_name, metrics in func_metrics.items():
            cc = metrics.get('cyclomatic_complexity', 0)
            # Normalize scores (simple min-max, can be improved)
            norm_cc = cc / 10 if cc <= 10 else 1.0
            norm_churn = churn / 20 if churn <= 20 else 1.0
            norm_kc = kc_score  # Already 0-1
            debt_score = (
                weights['cyclomatic_complexity'] * norm_cc +
                weights['churn_score'] * norm_churn +
                weights['knowledge_concentration_risk'] * norm_kc
            )
            rows.append({
                'file': file_path,
                'function': func_name,
                'cyclomatic_complexity': cc,
                'churn_score': churn,
                'knowledge_concentration_risk': kc_score,
                'debt_score': round(debt_score, 3)
            })
    df = pd.DataFrame(rows)
    df = df.sort_values(by='debt_score', ascending=False)
    return df
