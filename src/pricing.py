"""
Deterministic Pricing Engine for Aircraft Modification Proposals (v2.0.0).

Calculates itemized quotes with mod-type-aware testing fees, material allowances,
risk-based contingency, AOG/rush urgency surcharges, and volume discounts.

References:
- AACE International: Cost estimation contingency standards
- CS-25.1309: Testing requirements by system classification
- DO-160G: EMI/EMC environmental testing requirements
"""

import os
import csv
import json
from typing import Dict, Union, Any, Optional
from pydantic import BaseModel
from src.estimation import (
    estimate_manhours, ManhourEstimate, classify_part21_change,
    calculate_fleet_scaling
)

# ---------------------------------------------------------------------------
# [1.5] Testing & Certification Fee Table (USD)
# Mod-type and complexity sensitive.
# Reference: CS-25.1309, DO-160G EMI/EMC, structural test matrices
# Values: Generic industry practice (clean-room)
# ---------------------------------------------------------------------------
TESTING_FEE_TABLE: Dict[str, Dict[str, float]] = {
    "cabin":             {"minor": 800,   "standard": 2500,  "major": 6000},
    "structural":        {"minor": 2000,  "standard": 7000,  "major": 18000},
    "avionics":          {"minor": 2500,  "standard": 8500,  "major": 20000},
    "cargo":             {"minor": 5000,  "standard": 18000, "major": 40000},
    "ifc":               {"minor": 3500,  "standard": 12000, "major": 25000},
    "ife":               {"minor": 2000,  "standard": 7000,  "major": 16000},
    "isps":              {"minor": 1500,  "standard": 5000,  "major": 12000},
    "elams":             {"minor": 1000,  "standard": 3500,  "major": 8000},
    "gain":              {"minor": 1200,  "standard": 4000,  "major": 10000},
    "cabin_lopa":        {"minor": 1000,  "standard": 3000,  "major": 7000},
    "structural_repair": {"minor": 1500,  "standard": 5000,  "major": 14000},
}

# ---------------------------------------------------------------------------
# [1.6] Material Allowance per Aircraft (USD)
# Mod-type and complexity sensitive.
# Reference: Generic industry material kit costs (clean-room)
# ---------------------------------------------------------------------------
MATERIAL_PER_AIRCRAFT: Dict[str, Dict[str, float]] = {
    "cabin":             {"minor": 250,   "standard": 1500,  "major": 5000},
    "structural":        {"minor": 800,   "standard": 4000,  "major": 15000},
    "avionics":          {"minor": 1000,  "standard": 5000,  "major": 12000},
    "cargo":             {"minor": 5000,  "standard": 25000, "major": 80000},
    "ifc":               {"minor": 3000,  "standard": 15000, "major": 30000},
    "ife":               {"minor": 1500,  "standard": 8000,  "major": 20000},
    "isps":              {"minor": 500,   "standard": 2500,  "major": 6000},
    "elams":             {"minor": 200,   "standard": 1000,  "major": 3000},
    "gain":              {"minor": 800,   "standard": 3500,  "major": 9000},
    "cabin_lopa":        {"minor": 300,   "standard": 2000,  "major": 6000},
    "structural_repair": {"minor": 600,   "standard": 3000,  "major": 10000},
}

# ---------------------------------------------------------------------------
# [1.7] Risk-Based Contingency Rate Table
# Reference: AACE International, aerospace project estimation practice
# Proposal phase = FEED/Detailed Engineering level
# (complexity, requires_stc) → contingency rate
# ---------------------------------------------------------------------------
CONTINGENCY_RATES: Dict[tuple, float] = {
    ("minor", False): 0.04,
    ("minor", True):  0.06,
    ("standard", False): 0.07,
    ("standard", True):  0.10,
    ("major", False): 0.10,
    ("major", True):  0.15,
}

# ---------------------------------------------------------------------------
# [3.1] AOG/Rush Urgency Surcharge
# Applied to base_labor_cost, independent of margin.
# Covers overtime labor, mobilization, express authority approval fees.
# ---------------------------------------------------------------------------
URGENCY_SURCHARGE: Dict[str, float] = {
    "normal": 1.0,
    "rush": 1.25,
    "aog": 1.50,
}


def get_testing_fee(mod_type: str, complexity: str) -> float:
    """Returns testing & certification fee based on modification type and complexity."""
    fees = TESTING_FEE_TABLE.get(mod_type, TESTING_FEE_TABLE.get("cabin", {}))
    return float(fees.get(complexity, fees.get("standard", 3000)))


def get_material_allowance(mod_type: str, complexity: str, fleet_size: int) -> float:
    """Returns material allowance based on modification type, complexity, and fleet size."""
    materials = MATERIAL_PER_AIRCRAFT.get(mod_type, MATERIAL_PER_AIRCRAFT.get("cabin", {}))
    per_aircraft = float(materials.get(complexity, materials.get("standard", 2000)))
    return per_aircraft * max(1, fleet_size)


def get_contingency_rate(complexity: str, requires_stc: bool) -> float:
    """Returns risk-based contingency rate for the project."""
    return CONTINGENCY_RATES.get((complexity, requires_stc), 0.07)


def get_urgency_surcharge(strategy_string: str) -> float:
    """Returns urgency surcharge multiplier based on pricing strategy."""
    s = (strategy_string or "").lower()
    if "aog" in s:
        return URGENCY_SURCHARGE["aog"]
    elif any(k in s for k in ["rush", "acil", "hızlı", "hizli", "urgent"]):
        return URGENCY_SURCHARGE["rush"]
    return URGENCY_SURCHARGE["normal"]


def get_volume_discount(fleet_size: int) -> float:
    """Returns volume discount rate for large fleet orders."""
    if fleet_size >= 50:
        return 0.10
    elif fleet_size >= 20:
        return 0.05
    return 0.0


def load_data_files():
    """
    Loads rate_card.csv and customer_classes.json dynamically.
    Uses relative paths from this script to locate the data directory.
    """
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    
    rate_card_path = os.path.join(project_root, "data", "rate_card.csv")
    customer_classes_path = os.path.join(project_root, "data", "customer_classes.json")
    
    # 1. Parse rate card
    rates = {}
    if os.path.exists(rate_card_path):
        with open(rate_card_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rates[row["role"].strip()] = float(row["hourly_rate"])
    else:
        # Fallback if file not found
        rates = {
            "cabin_design_engineer": 95.00,
            "structural_engineer": 110.00,
            "avionics_design_engineer": 105.00,
            "certification_engineer": 80.00,
            "project_manager": 120.00
        }

    # 2. Parse customer classes
    if os.path.exists(customer_classes_path):
        with open(customer_classes_path, "r", encoding="utf-8") as f:
            customer_classes = json.load(f)
    else:
        # Fallback if file not found
        customer_classes = {
            "flagship": {"min_margin": 0.05, "max_margin": 0.15, "default_margin": 0.10},
            "partner": {"min_margin": 0.15, "max_margin": 0.30, "default_margin": 0.22},
            "third_party": {"min_margin": 0.30, "max_margin": 0.50, "default_margin": 0.40}
        }
        
    return rates, customer_classes

def calculate_quote(
    manhours: Union[Dict[str, float], Any, None], 
    customer_class: str, 
    strategy_string: str, 
    fleet_size: int = 1,
    modification_type: Optional[str] = "cabin",
    complexity: Optional[str] = "standard",
    scope_text: Optional[str] = None,
    aircraft_type: Optional[str] = None,
    dal_level: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates an itemized quote for an aircraft modification project.
    
    v2.0.0 enhancements:
    - Mod-type-aware testing fees (CS-25.1309, DO-160G)
    - Mod-type-aware material allowances
    - Risk-based contingency (AACE standards)
    - AOG/Rush urgency surcharge on base labor
    - Volume discount for large fleets (20+/50+)
    """
    manhour_source = "Customer Provided"
    manhours_dict = {}

    if hasattr(manhours, "model_dump"):
        manhours_dict = manhours.model_dump()
    elif isinstance(manhours, dict):
        manhours_dict = dict(manhours)

    # 1. Validate inputs (check for negative hours first)
    for role, hours in manhours_dict.items():
        if hours is not None and hours < 0:
            raise ValueError(f"manhours for '{role}' cannot be negative: {hours}")

    # Resolve modification type and complexity for pricing tables
    mod_type_resolved = (modification_type or "cabin").lower().strip()
    complexity_resolved = (complexity or "standard").lower().strip()
    if complexity_resolved not in ["minor", "standard", "major"]:
        complexity_resolved = "standard"

    # Check if customer provided valid non-zero hours
    has_customer_hours = any(v is not None and v > 0 for v in manhours_dict.values()) if manhours_dict else False

    if not has_customer_hours:
        manhour_source = "DOA Estimation Engine"
        est = estimate_manhours(
            modification_type=modification_type,
            complexity=complexity,
            fleet_size=fleet_size,
            scope_text=scope_text,
            aircraft_type=aircraft_type,
            dal_level=dal_level
        )
        manhours_dict = est.model_dump()
    elif scope_text:
        # Add mandatory EASA Part 21.A.239 CVE + ICA hours to customer certification engineering hours
        part21_info = classify_part21_change(scope_text, modification_type or "cabin", complexity or "standard")
        cve_hours = part21_info["cve_hours"]
        ica_hours = part21_info["ica_hours"]
        manhours_dict["certification_engineer"] = (manhours_dict.get("certification_engineer") or 0.0) + cve_hours + ica_hours

    # 2. Parse rates and customer classes
    rates, customer_classes = load_data_files()
    
    if customer_class not in customer_classes:
        raise ValueError(f"Unknown customer class: '{customer_class}'. Available: {list(customer_classes.keys())}")

    # 3. Calculate Base Labor Cost
    base_labor_cost = 0.0
    for role, hours in manhours_dict.items():
        if hours is not None and hours > 0:
            if role not in rates:
                raise ValueError(f"Unknown engineering role '{role}' in manhours. Available roles in rate card: {list(rates.keys())}")
            base_labor_cost += hours * rates[role]

    # 4. [3.1] Apply AOG/Rush Urgency Surcharge to base labor
    urgency_mult = get_urgency_surcharge(strategy_string)
    base_labor_cost_adjusted = round(base_labor_cost * urgency_mult, 2)

    # 5. Map Strategy to Margin Band
    strategy_lower = strategy_string.lower() if strategy_string else ""
    class_bands = customer_classes[customer_class]
    
    min_margin = class_bands["min_margin"]
    max_margin = class_bands["max_margin"]
    default_margin = class_bands["default_margin"]

    if any(k in strategy_lower for k in ["cheap", "ucuz"]):
        margin_applied = min_margin
    elif any(k in strategy_lower for k in ["premium", "rush", "aog", "acil", "hızlı", "hizli"]):
        margin_applied = max_margin
    elif any(k in strategy_lower for k in ["comp", "rekabet"]):
        margin_applied = max(min_margin, default_margin - 0.02)
    else:
        margin_applied = default_margin

    # Ensure margin_applied is strictly within [min_margin, max_margin]
    margin_applied = max(min_margin, min(max_margin, margin_applied))
    margin_applied = round(margin_applied, 4)

    # 6. Get Part 21 info for contingency calculation
    part21_info = classify_part21_change(scope_text, mod_type_resolved, complexity_resolved)

    # 7. Itemized Quote Calculation (all based on adjusted base labor)
    margin_amount = round(base_labor_cost_adjusted * margin_applied, 2)
    
    # [1.7] Risk-based contingency
    contingency_rate = get_contingency_rate(complexity_resolved, part21_info["requires_stc"])
    contingency = round(base_labor_cost_adjusted * contingency_rate, 2)
    
    # [1.5] Mod-type-aware testing fee
    testing_fee = get_testing_fee(mod_type_resolved, complexity_resolved)
    
    # [1.6] Mod-type-aware material allowance
    fleet_sz = max(1, fleet_size)
    material_allowance = get_material_allowance(mod_type_resolved, complexity_resolved, fleet_sz)
    
    subtotal = round(
        base_labor_cost_adjusted + margin_amount + contingency + testing_fee + material_allowance,
        2
    )
    
    # [3.3] Volume discount for large fleets
    volume_discount_rate = get_volume_discount(fleet_sz)
    volume_discount = round(subtotal * volume_discount_rate, 2)
    
    total_cost = round(subtotal - volume_discount, 2)

    return {
        "manhour_source": manhour_source,
        "manhours_used": manhours_dict,
        "base_labor_cost": round(base_labor_cost, 2),
        "urgency_multiplier": urgency_mult,
        "base_labor_cost_adjusted": base_labor_cost_adjusted,
        "margin_applied": margin_applied,
        "margin_amount": margin_amount,
        "contingency_rate": contingency_rate,
        "contingency": contingency,
        "testing_fee": testing_fee,
        "material_allowance": material_allowance,
        "volume_discount_rate": volume_discount_rate,
        "volume_discount": volume_discount,
        "total_cost": total_cost
    }
