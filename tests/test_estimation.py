import pytest
from src.estimation import estimate_manhours, BASELINE_HOURS, ManhourEstimate

def test_cabin_standard_fleet_1():
    est = estimate_manhours(modification_type="cabin", complexity="standard", fleet_size=1)
    assert isinstance(est, ManhourEstimate)
    assert est.cabin_design_engineer == 80.0
    assert est.structural_engineer == 40.0
    assert est.avionics_design_engineer == 10.0
    assert est.certification_engineer == 25.0
    assert est.project_manager == 15.0
    assert est.total_hours() == 170.0

def test_fleet_scaling():
    # 5 aircraft fleet size: scaling factor = 1.0 + (5-1)*0.10 = 1.4x
    est = estimate_manhours(modification_type="cabin", complexity="standard", fleet_size=5)
    assert est.cabin_design_engineer == 112.0 # 80 * 1.4
    assert est.structural_engineer == 56.0    # 40 * 1.4
    assert est.certification_engineer == 35.0 # 25 * 1.4

def test_scope_keyword_inference():
    # Test major complexity inferred from STC keyword
    est = estimate_manhours(modification_type="structural", scope_text="Major fuselage STC modification for cargo door")
    assert est.structural_engineer == 300.0 # major baseline
    assert est.certification_engineer == 100.0

def test_fallback_defaults():
    est = estimate_manhours(modification_type=None, complexity=None, fleet_size=None)
    assert est.total_hours() > 0
