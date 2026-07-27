import os
import csv
import json
from typing import Dict, Union, Any, Optional
from pydantic import BaseModel
from src.estimation import estimate_manhours, ManhourEstimate

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
    If manhours are provided by customer, uses customer hours.
    Otherwise, uses AeroDesign DOA Estimation Engine to deterministically calculate manhours.
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

    # 2. Validate inputs
    for role, hours in manhours_dict.items():
        if hours is not None and hours < 0:
            raise ValueError(f"manhours for '{role}' cannot be negative: {hours}")

    rates, customer_classes = load_data_files()
    
    if customer_class not in customer_classes:
        raise ValueError(f"Unknown customer class: '{customer_class}'. Available: {list(customer_classes.keys())}")

    # 3. Calculate Base Labor Cost
    base_labor_cost = 0.0
    for role, hours in manhours_dict.items():
        if hours is not None:
            rate = rates.get(role, 0.0)
            base_labor_cost += hours * rate

    # 4. Map Strategy to Margin Band
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
        margin_applied = default_margin - 0.02
    else:
        margin_applied = default_margin

    # Round margin applied to avoid precision errors in comparison
    margin_applied = round(margin_applied, 4)

    # 5. Itemized Quote Calculation
    margin_amount = round(base_labor_cost * margin_applied, 2)
    contingency = round(base_labor_cost * 0.05, 2)
    testing_fee = 1500.00
    material_allowance = float(max(1, fleet_size) * 500)
    
    total_cost = round(
        base_labor_cost + margin_amount + contingency + testing_fee + material_allowance, 
        2
    )

    return {
        "manhour_source": manhour_source,
        "manhours_used": manhours_dict,
        "base_labor_cost": round(base_labor_cost, 2),
        "margin_applied": margin_applied,
        "margin_amount": margin_amount,
        "contingency": contingency,
        "testing_fee": testing_fee,
        "material_allowance": material_allowance,
        "total_cost": total_cost
    }
