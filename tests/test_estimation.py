import pytest
from src.estimation import (
    estimate_manhours, 
    BASELINE_HOURS, 
    ManhourEstimate, 
    resolve_cert_basis, 
    classify_part21_change,
    get_dal_multiplier
)

def test_cabin_standard_fleet_1():
    est = estimate_manhours(modification_type="cabin", complexity="standard", fleet_size=1)
    assert isinstance(est, ManhourEstimate)
    assert est.cabin_design_engineer == 80.0
    assert est.structural_engineer == 40.0
    assert est.avionics_design_engineer == 10.0
    assert est.certification_engineer == 31.0  # 25.0 base + 6.0 CVE minor verification
    assert est.project_manager == 15.0
    assert est.total_hours() == 176.0

def test_fleet_scaling():
    # 5 aircraft fleet size: scaling factor = 1.0 + (5-1)*0.10 = 1.4x
    est = estimate_manhours(modification_type="cabin", complexity="standard", fleet_size=5)
    assert est.cabin_design_engineer == 112.0 # 80 * 1.4
    assert est.structural_engineer == 56.0    # 40 * 1.4
    assert est.certification_engineer == 43.4 # (25 + 6 CVE) * 1.4

def test_scope_keyword_inference():
    # Test major complexity inferred from STC keyword
    est = estimate_manhours(modification_type="structural", scope_text="Major fuselage STC modification for cargo door")
    assert est.structural_engineer == 300.0 # major baseline
    assert est.certification_engineer == 125.0 # 100.0 base + 25.0 STC CVE verification

def test_fallback_defaults():
    est = estimate_manhours(modification_type=None, complexity=None, fleet_size=None)
    assert est.total_hours() > 0

# --- v1.1.0 Fixed-Wing Certification & Part 21 Tests ---

def test_resolve_cert_basis():
    assert resolve_cert_basis("A320-200") == "CS-25"
    assert resolve_cert_basis("Boeing 737-800") == "CS-25"
    assert resolve_cert_basis("Cessna 172 Skyhawk") == "CS-23"
    assert resolve_cert_basis("King Air 350") == "CS-23"

def test_classify_part21_change():
    minor_info = classify_part21_change("Replace cabin carpet and seat covers", "cabin", "minor")
    assert minor_info["is_major_change"] is False
    assert minor_info["requires_stc"] is False
    assert minor_info["cve_hours"] == 6.0

    major_info = classify_part21_change("Install fuselage Wi-Fi radome antenna cutout STC", "ifc", "major")
    assert major_info["is_major_change"] is True
    assert major_info["requires_stc"] is True
    assert major_info["cve_hours"] == 25.0

def test_new_project_types_estimation():
    ifc_est = estimate_manhours(modification_type="ifc", complexity="standard", fleet_size=1)
    assert ifc_est.structural_engineer == 90.0
    assert ifc_est.avionics_design_engineer == 140.0
    
    isps_est = estimate_manhours(modification_type="isps", complexity="minor", fleet_size=1)
    assert isps_est.avionics_design_engineer == 35.0

def test_arp4761_dal_multipliers():
    assert get_dal_multiplier("DAL A") == 2.2
    assert get_dal_multiplier("Level A") == 2.2
    assert get_dal_multiplier("A") == 2.2
    assert get_dal_multiplier("DAL-B") == 2.2
    assert get_dal_multiplier("DAL D") == 1.3
    assert get_dal_multiplier("C") == 1.3
    assert get_dal_multiplier("Level C") == 1.3
    assert get_dal_multiplier("DAL E") == 1.0

    dal_a_est = estimate_manhours(modification_type="avionics", complexity="standard", dal_level="DAL A")
    # Base cert engineer = (30.0 base + 6.0 CVE) * 2.2 = 79.2
    assert dal_a_est.certification_engineer == 79.2

def test_cs23_manhour_factor():
    cs25_est = estimate_manhours(modification_type="avionics", complexity="standard", aircraft_type="A320")
    cs23_est = estimate_manhours(modification_type="avionics", complexity="standard", aircraft_type="King Air 350")
    assert cs23_est.certification_engineer < cs25_est.certification_engineer

def test_zero_fleet_size_gap():
    from src.gaps import check_gaps
    gaps = check_gaps({"aircraft_type": "A320", "fleet_size": 0, "modification_type": "cabin", "customer_name": "Test", "scope": "Valid scope"})
    assert "fleet_size" in gaps
