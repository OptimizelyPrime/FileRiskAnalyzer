"""
debt_weights.py
Configurable weights for Debt Score calculation.
"""

# Default weights (can be adjusted)
WEIGHTS = {
    'cyclomatic_complexity': 0.3,
    'churn_score': 0.2,
    'knowledge_concentration_risk': 0.3,
    # Add more signals as needed
}

# You can add a function to update weights if needed

def get_weights():
    return WEIGHTS


def set_weights(new_weights):
    global WEIGHTS
    WEIGHTS.update(new_weights)
