import math

def calculate_file_health_score(func_metrics, raw_churn, raw_kc_pct):
    """
    Calculate a file health score based on maintainability, churn, and knowledge concentration.
    The formula is: Maintainability Score - Churn Score - Knowledge Concentration Score
    Higher scores are better.
    Args:
        func_metrics (dict): A dictionary of function-level metrics for a file.
        raw_churn (int): The raw churn count for the file.
        raw_kc_pct (float): The raw knowledge concentration percentage for the file.
    Returns:
        float: Health score (can be negative, higher is better)
    """
    # 1. Calculate Maintainability Score (weighted average MI)
    ams_vals = []
    total_loc = 0
    for m in func_metrics.values():
        loc = m.get('lines_of_code')
        if m.get('maintainability_index') not in (None, 'N/A') and loc not in (None, 'N/A'):
            ams_vals.append((m['maintainability_index'], loc))
            total_loc += loc

    if ams_vals and total_loc > 0:
        ams_score = sum(idx * (loc / total_loc) for idx, loc in ams_vals)
    elif ams_vals:
        ams_score = sum(idx for idx, _ in ams_vals) / len(ams_vals)
    else:
        ams_score = 0

    # 2. Calculate scaled Churn and Knowledge Concentration scores
    # Formula: 3.26 * ln(raw_value + 1)
    scaled_churn = 3.26 * math.log(raw_churn + 1) if raw_churn > 0 else 0
    scaled_kc = 3.26 * math.log(raw_kc_pct + 1) if raw_kc_pct > 0 else 0

    # 3. Calculate final health score
    health_score = ams_score - scaled_churn - scaled_kc

    return round(health_score, 2)
