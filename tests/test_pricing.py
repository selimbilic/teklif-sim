import os
import pytest
from src.pricing import (
    calculate_quote, get_testing_fee, get_material_allowance,
    get_contingency_rate, get_urgency_surcharge, get_volume_discount,
    TESTING_FEE_TABLE, MATERIAL_PER_AIRCRAFT, CONTINGENCY_RATES,
)

# === v2.0.0 Pricing Engine Tests ===

# Test Case 1: Flagship customer, cheapest strategy, 5 aircraft, cabin standard
def test_case_1_flagship_cheapest_cabin():
    manhours = {
        "cabin_design_engineer": 80,
        "structural_engineer": 40,
        "certification_engineer": 20,
        "project_manager": 10
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="flagship",
        strategy_string="cheapest possible",
        fleet_size=5,
        modification_type="cabin",
        complexity="standard"
    )
    assert quote["base_labor_cost"] == 14800.00
    assert quote["margin_applied"] == 0.05
    assert quote["urgency_multiplier"] == 1.0
    assert quote["base_labor_cost_adjusted"] == 14800.00
    # Testing fee: cabin standard = 2500
    assert quote["testing_fee"] == 2500.00
    # Material: cabin standard = 1500 * 5 = 7500
    assert quote["material_allowance"] == 7500.00
    # Contingency: standard, no STC (cabin standard doesn't trigger STC) = 7%
    assert quote["contingency_rate"] == 0.07
    assert quote["total_cost"] > 0

# Test Case 2: Third-party, rush/AOG strategy → urgency surcharge
def test_case_2_third_party_aog():
    manhours = {
        "structural_engineer": 60,
        "certification_engineer": 15,
        "project_manager": 5
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="third_party",
        strategy_string="AOG critical situation",
        fleet_size=1,
        modification_type="structural",
        complexity="standard"
    )
    # AOG → urgency_multiplier = 1.50
    assert quote["urgency_multiplier"] == 1.50
    assert quote["base_labor_cost_adjusted"] == round(quote["base_labor_cost"] * 1.50, 2)
    # Margin: premium/rush/aog → max_margin for third_party = 0.50
    assert quote["margin_applied"] == 0.50

# Test Case 3: Testing fee varies by mod type
def test_testing_fee_by_mod_type():
    assert get_testing_fee("cabin", "minor") == 800
    assert get_testing_fee("cargo", "major") == 40000
    assert get_testing_fee("avionics", "standard") == 8500
    assert get_testing_fee("ifc", "major") == 25000
    # Unknown mod type should fallback to cabin
    assert get_testing_fee("unknown_type", "standard") == 2500

# Test Case 4: Material allowance varies by mod type and fleet
def test_material_allowance_by_mod_type():
    assert get_material_allowance("cabin", "minor", 1) == 250
    assert get_material_allowance("cargo", "major", 10) == 800000  # 80000 * 10
    assert get_material_allowance("ifc", "standard", 5) == 75000  # 15000 * 5

# Test Case 5: Risk-based contingency rates
def test_contingency_risk_based():
    assert get_contingency_rate("minor", False) == 0.04
    assert get_contingency_rate("minor", True) == 0.06
    assert get_contingency_rate("standard", False) == 0.07
    assert get_contingency_rate("standard", True) == 0.10
    assert get_contingency_rate("major", False) == 0.10
    assert get_contingency_rate("major", True) == 0.15
    # Fallback for unknown
    assert get_contingency_rate("unknown", False) == 0.07

# Test Case 6: Urgency surcharge detection
def test_urgency_surcharge():
    assert get_urgency_surcharge("cheapest possible") == 1.0
    assert get_urgency_surcharge("normal project") == 1.0
    assert get_urgency_surcharge("AOG critical") == 1.50
    assert get_urgency_surcharge("rush delivery acil") == 1.25
    assert get_urgency_surcharge("hızlı teslimat") == 1.25
    assert get_urgency_surcharge("") == 1.0

# Test Case 7: Volume discount
def test_volume_discount():
    assert get_volume_discount(1) == 0.0
    assert get_volume_discount(10) == 0.0
    assert get_volume_discount(19) == 0.0
    assert get_volume_discount(20) == 0.05
    assert get_volume_discount(49) == 0.05
    assert get_volume_discount(50) == 0.10
    assert get_volume_discount(100) == 0.10

# Test Case 8: Volume discount applied in quote
def test_volume_discount_in_quote():
    quote_small = calculate_quote(
        manhours={"cabin_design_engineer": 100},
        customer_class="partner",
        strategy_string="standard",
        fleet_size=5,
        modification_type="cabin",
        complexity="standard"
    )
    quote_large = calculate_quote(
        manhours={"cabin_design_engineer": 100},
        customer_class="partner",
        strategy_string="standard",
        fleet_size=25,
        modification_type="cabin",
        complexity="standard"
    )
    assert quote_small["volume_discount_rate"] == 0.0
    assert quote_small["volume_discount"] == 0.0
    assert quote_large["volume_discount_rate"] == 0.05
    assert quote_large["volume_discount"] > 0

# Test Case 9: Negative hours still raise ValueError
def test_negative_manhours():
    manhours = {"cabin_design_engineer": -10}
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_quote(manhours, "flagship", "cheapest")

# Test Case 10: Unknown customer class still raises ValueError
def test_unknown_customer_class():
    manhours = {"cabin_design_engineer": 10}
    with pytest.raises(ValueError, match="Unknown customer class"):
        calculate_quote(manhours, "unknown_class", "cheapest")

# Test Case 11: Empty manhours → DOA Estimation Engine auto-engages
def test_empty_manhours_doa_engine():
    quote = calculate_quote(
        manhours={},
        customer_class="third_party",
        strategy_string="cheapest",
        fleet_size=1,
        modification_type="cabin",
        complexity="standard"
    )
    assert quote["manhour_source"] == "DOA Estimation Engine"
    assert quote["base_labor_cost"] > 0.00
    assert quote["total_cost"] > 0.00

# Test Case 12: DAL affects DOA engine quote
def test_quote_dal_affects_total():
    quote_default = calculate_quote(
        manhours={},
        customer_class="third_party",
        strategy_string="standard",
        fleet_size=1,
        modification_type="avionics",
        complexity="standard"
    )
    quote_dal_a = calculate_quote(
        manhours={},
        customer_class="third_party",
        strategy_string="standard",
        fleet_size=1,
        modification_type="avionics",
        complexity="standard",
        dal_level="DAL A"
    )
    assert quote_dal_a["base_labor_cost"] > quote_default["base_labor_cost"]
    assert quote_dal_a["total_cost"] > quote_default["total_cost"]

# Test Case 13: Cargo major STC triggers high contingency rate
def test_cargo_major_stc_contingency():
    quote = calculate_quote(
        manhours={},
        customer_class="partner",
        strategy_string="standard",
        fleet_size=3,
        modification_type="cargo",
        complexity="major",
        scope_text="P2F cargo door conversion STC"
    )
    # Cargo major STC → contingency_rate should be 0.15
    assert quote["contingency_rate"] == 0.15
    # Testing fee: cargo major = 40000
    assert quote["testing_fee"] == 40000

# Test Case 14: Quote output has all v2.0.0 fields
def test_quote_output_fields():
    quote = calculate_quote(
        manhours={"cabin_design_engineer": 50},
        customer_class="flagship",
        strategy_string="standard",
        fleet_size=1
    )
    required_fields = [
        "manhour_source", "manhours_used", "base_labor_cost",
        "urgency_multiplier", "base_labor_cost_adjusted",
        "margin_applied", "margin_amount",
        "contingency_rate", "contingency",
        "testing_fee", "material_allowance",
        "volume_discount_rate", "volume_discount",
        "total_cost"
    ]
    for field in required_fields:
        assert field in quote, f"Missing field: {field}"

# Test Case 15: CVE + ICA hours added to customer-provided cert hours
def test_cve_ica_added_to_customer_hours():
    quote = calculate_quote(
        manhours={"certification_engineer": 20},
        customer_class="flagship",
        strategy_string="standard",
        fleet_size=1,
        modification_type="ifc",
        complexity="major",
        scope_text="Wi-Fi STC installation"
    )
    # IFC major STC → CVE=60, ICA=45 → total cert = 20 + 60 + 45 = 125
    assert quote["manhours_used"]["certification_engineer"] == 125.0
