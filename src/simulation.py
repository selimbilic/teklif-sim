"""
Monte-Carlo Uncertainty & Risk Engineering Simulation Module for TEKLİF-Sim (v3.0.0).
Calculates P10 (Optimistic), P50 (Expected), and P90 (Conservative/Worst Case)
manhour and cost confidence intervals for risk engineering using triangular distribution.
"""

import math
import random
from typing import Dict, Any, List

def run_monte_carlo_simulation(
    base_manhours: float,
    base_cost: float,
    complexity: str = "standard",
    num_simulations: int = 1000,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Runs a 1,000-iteration Monte-Carlo simulation over project parameters
    using triangular distribution around base manhours and cost volatility.
    
    Returns:
    - P10 (Best Case / Optimistic): 10th percentile cost & hours
    - P50 (Expected Case / Median): 50th percentile cost & hours
    - P90 (Worst Case / Conservative): 90th percentile cost & hours
    - risk_buffer_usd: Risk contingency difference between P90 and P50
    - spread_pct: Percentage spread between P10 and P90
    """
    rng = random.Random(seed)
    
    # Volatility factors based on project complexity
    comp_lower = (complexity or "standard").lower().strip()
    if comp_lower == "minor":
        low_mult, mode_mult, high_mult = 0.90, 1.00, 1.15
    elif comp_lower == "major":
        low_mult, mode_mult, high_mult = 0.85, 1.02, 1.35
    else: # standard
        low_mult, mode_mult, high_mult = 0.88, 1.01, 1.25

    simulated_hours: List[float] = []
    simulated_costs: List[float] = []

    for _ in range(num_simulations):
        mult = rng.triangular(low_mult, high_mult, mode_mult)
        sim_h = round(base_manhours * mult, 2)
        sim_c = round(base_cost * mult, 2)
        simulated_hours.append(sim_h)
        simulated_costs.append(sim_c)

    simulated_hours.sort()
    simulated_costs.sort()

    idx_p10 = int(num_simulations * 0.10)
    idx_p50 = int(num_simulations * 0.50)
    idx_p90 = int(num_simulations * 0.90)

    p10_hours = simulated_hours[idx_p10]
    p50_hours = simulated_hours[idx_p50]
    p90_hours = simulated_hours[idx_p90]

    p10_cost = simulated_costs[idx_p10]
    p50_cost = simulated_costs[idx_p50]
    p90_cost = simulated_costs[idx_p90]

    return {
        "p10": {"manhours": p10_hours, "cost": p10_cost, "label": "P10 (Optimistic)"},
        "p50": {"manhours": p50_hours, "cost": p50_cost, "label": "P50 (Expected)"},
        "p90": {"manhours": p90_hours, "cost": p90_cost, "label": "P90 (Conservative / Risk Contingency)"},
        "risk_buffer_usd": round(p90_cost - p50_cost, 2),
        "spread_pct": round(((p90_cost - p10_cost) / (p50_cost or 1.0)) * 100, 1)
    }
