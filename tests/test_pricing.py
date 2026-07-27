import os
import pytest
from src.pricing import calculate_quote

# Test Case 1: Flagship Müşteri - En Ucuz Strateji - 5 Uçak
def test_case_1_flagship_cheapest():
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
        fleet_size=5
    )
    assert quote["base_labor_cost"] == 14800.00
    assert quote["margin_applied"] == 0.05
    assert quote["margin_amount"] == 740.00
    assert quote["contingency"] == 740.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 2500.00
    assert quote["total_cost"] == 20280.00

# Test Case 2: Flagship Müşteri - Rekabetçi Strateji - 5 Uçak
def test_case_2_flagship_competitive():
    manhours = {
        "cabin_design_engineer": 80,
        "structural_engineer": 40,
        "certification_engineer": 20,
        "project_manager": 10
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="flagship",
        strategy_string="keep it competitive for them",
        fleet_size=5
    )
    assert quote["base_labor_cost"] == 14800.00
    assert quote["margin_applied"] == 0.08
    assert quote["margin_amount"] == 1184.00
    assert quote["contingency"] == 740.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 2500.00
    assert quote["total_cost"] == 20724.00

# Test Case 3: Third Party Müşteri - Acil (Rush) Strateji - 1 Uçak
def test_case_3_third_party_rush():
    manhours = {
        "structural_engineer": 60,
        "certification_engineer": 15,
        "project_manager": 5
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="third_party",
        strategy_string="premium / rush strategy",
        fleet_size=1
    )
    assert quote["base_labor_cost"] == 8400.00
    assert quote["margin_applied"] == 0.50
    assert quote["margin_amount"] == 4200.00
    assert quote["contingency"] == 420.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 500.00
    assert quote["total_cost"] == 15020.00

# Test Case 4: Partner Müşteri - Belirsiz Strateji (Varsayılan Marj) - 8 Uçak
def test_case_4_partner_default():
    manhours = {
        "structural_engineer": 150,
        "avionics_design_engineer": 100,
        "certification_engineer": 40,
        "project_manager": 20
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="partner",
        strategy_string="normal project flow",
        fleet_size=8
    )
    assert quote["base_labor_cost"] == 32600.00
    assert quote["margin_applied"] == 0.22
    assert quote["margin_amount"] == 7172.00
    assert quote["contingency"] == 1630.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 4000.00
    assert quote["total_cost"] == 46902.00

# Test Case 5: Third Party Müşteri - En Ucuz Strateji - 12 Uçak
def test_case_5_third_party_cheapest():
    manhours = {
        "cabin_design_engineer": 120,
        "certification_engineer": 30,
        "project_manager": 10
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="third_party",
        strategy_string="make it the cheapest possible",
        fleet_size=12
    )
    assert quote["base_labor_cost"] == 15000.00
    assert quote["margin_applied"] == 0.30
    assert quote["margin_amount"] == 4500.00
    assert quote["contingency"] == 750.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 6000.00
    assert quote["total_cost"] == 27750.00

# Test Case 6: Partner Müşteri - Rekabetçi Strateji - 2 Uçak
def test_case_6_partner_competitive():
    manhours = {
        "cabin_design_engineer": 50,
        "avionics_design_engineer": 50,
        "certification_engineer": 15,
        "project_manager": 5
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="partner",
        strategy_string="rekabetçi fiyat verilsin",
        fleet_size=2
    )
    assert quote["base_labor_cost"] == 11800.00
    assert quote["margin_applied"] == 0.20
    assert quote["margin_amount"] == 2360.00
    assert quote["contingency"] == 590.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 1000.00
    assert quote["total_cost"] == 17250.00

# Test Case 7: Third Party Müşteri - Varsayılan Strateji - 1 Uçak
def test_case_7_third_party_default():
    manhours = {
        "avionics_design_engineer": 100,
        "certification_engineer": 25,
        "project_manager": 10
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="third_party",
        strategy_string="",
        fleet_size=1
    )
    assert quote["base_labor_cost"] == 13700.00
    assert quote["margin_applied"] == 0.40
    assert quote["margin_amount"] == 5480.00
    assert quote["contingency"] == 685.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 500.00
    assert quote["total_cost"] == 21865.00

# Test Case 8: Flagship Müşteri - Acil (Rush) Strateji - 3 Uçak
def test_case_8_flagship_rush():
    manhours = {
        "cabin_design_engineer": 150,
        "structural_engineer": 100,
        "avionics_design_engineer": 50,
        "certification_engineer": 30,
        "project_manager": 20
    }
    quote = calculate_quote(
        manhours=manhours,
        customer_class="flagship",
        strategy_string="acil AOG durumuna göre hızlı fiyatlandırın",
        fleet_size=3
    )
    assert quote["base_labor_cost"] == 35300.00
    assert quote["margin_applied"] == 0.15
    assert quote["margin_amount"] == 5295.00
    assert quote["contingency"] == 1765.00
    assert quote["testing_fee"] == 1500.00
    assert quote["material_allowance"] == 1500.00
    assert quote["total_cost"] == 45360.00

# Edge Case 9: Negatif saat kontrolü
def test_negative_manhours():
    manhours = {"cabin_design_engineer": -10}
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_quote(manhours, "flagship", "cheapest")

# Edge Case 10: Bilinmeyen müşteri sınıfı
def test_unknown_customer_class():
    manhours = {"cabin_design_engineer": 10}
    with pytest.raises(ValueError, match="Unknown customer class"):
        calculate_quote(manhours, "unknown_class", "cheapest")

# Edge Case 11: Boş saat sözlüğü -> DOA Tahmin Motoru otomatik devreye girer
def test_empty_manhours():
    quote = calculate_quote(
        manhours={},
        customer_class="third_party",
        strategy_string="cheapest",
        fleet_size=1
    )
    assert quote["manhour_source"] == "DOA Estimation Engine"
    assert quote["base_labor_cost"] > 0.00
    assert quote["total_cost"] > 0.00

def test_quote_passes_dal_and_aircraft_type():
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
    # Quote with DAL A should have higher labor cost than default due to 2.2x safety multiplier
    assert quote_dal_a["base_labor_cost"] > quote_default["base_labor_cost"]
    assert quote_dal_a["total_cost"] > quote_default["total_cost"]
