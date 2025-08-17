def calculate_file_risk(func_metrics, churn_norm, kc_norm, weights=None):
    """
    Calculate a holistic file risk score from code quality, churn, and knowledge concentration.
    This function computes a weighted average of the maintainability index (MI) for all functions
    in a file, and then combines it with churn and knowledge concentration scores.
    Args:
        func_metrics (dict): A dictionary of function-level metrics for a file.
        churn_norm (float): Normalized churn (0-1)
        kc_norm (float): Normalized knowledge concentration (0-1)
        weights (dict): Dict with keys 'quality', 'churn', 'kc' summing to 1.0
    Returns:
        float: Risk score (0-100, higher is riskier)
    """
    ams_vals = []
    total_loc = 0
    for m in func_metrics.values():
        loc = m.get('lines_of_code')
        if m.get('maintainability_index') not in (None, 'N/A') and loc not in (None, 'N/A'):
            ams_vals.append((m['maintainability_index'], loc))
            total_loc += loc

    if ams_vals and total_loc > 0:
        ams_score = sum(idx * (loc / total_loc) for idx, loc in ams_vals)
        risk_weights = weights
    elif ams_vals:
        ams_score = sum(idx for idx, _ in ams_vals) / len(ams_vals)
        risk_weights = weights
    else:
        ams_score = 0
        # If no functions, set quality weight to 0, distribute rest proportionally
        risk_weights = {'quality': 0.0, 'churn': 0.5, 'kc': 0.5}

    return _calculate_risk_from_scores(ams_score, churn_norm, kc_norm, weights=risk_weights)


def _calculate_risk_from_scores(ams_score, churn_norm, kc_norm, weights=None):
    """
    Calculate a holistic file risk score from code quality, churn, and knowledge concentration.
    Args:
        ams_score (float): Average maintainability score (0-100, higher is better)
        churn_norm (float): Normalized churn (0-1)
        kc_norm (float): Normalized knowledge concentration (0-1)
        weights (dict): Dict with keys 'quality', 'churn', 'kc' summing to 1.0
    Returns:
        float: Risk score (0-100, higher is riskier)
    """
    if weights is None:
        weights = {'quality': 0.50, 'churn': 0.25, 'kc': 0.25}
    if not all(k in weights for k in ('quality', 'churn', 'kc')):
        raise ValueError("Weights must have 'quality', 'churn', and 'kc' keys.")
    if not abs(sum(weights.values()) - 1.0) < 1e-6:
        raise ValueError("Weights must sum to 1.0")
    ams_score = max(0, min(100, ams_score))
    churn_norm = max(0, min(1, churn_norm))
    kc_norm = max(0, min(1, kc_norm))
    risk = (
        weights['quality'] * (100 - ams_score)
        + weights['churn'] * churn_norm * 100
        + weights['kc'] * kc_norm * 100
    )
    return round(risk, 2)
