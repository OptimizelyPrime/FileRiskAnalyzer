def calculate_overall_risk(ams_score, churn_norm, kc_norm, weights=None):
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
