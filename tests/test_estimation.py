import math
import pytest
from src.estimation import (
    estimate_manhours, 
    BASELINE_HOURS, 
    ManhourEstimate, 
    resolve_cert_basis, 
    classify_part21_change,
    get_dal_multiplier,
    calculate_fleet_scaling,
    DAL_MULTIPLIERS,
    CS23_REDUCTION_FACTORS,
    CVE_HOURS_TABLE,
    ICA_HOURS_TABLE,
    EWIS_ADDITIONAL_HOURS,
    NRE_RATIO,
)

# === v1.x Legacy Equivalent Tests (updated expected values) ===

def test_cabin_standard_fleet_1():
    """Cabin standard, 1 aircraft, no DAL, CS-25 default."""
    est = estimate_manhours(modification_type="cabin", complexity="standard", fleet_size=1)
    assert isinstance(est, ManhourEstimate)
    assert est.cabin_design_engineer == 80.0
    assert est.structural_engineer == 40.0
    # Avionics: 10 base + 0 EWIS (cabin has no EWIS entry)
    assert est.avionics_design_engineer == 10.0
    # Cert: 25 base + 4 CVE(minor cabin) + 3 ICA(minor cabin) = 32.0
    # Wait: classify_part21_change("", "cabin", "standard") → standard is NOT major,
    # so it's minor → CVE=4, ICA=3
    # Actually, let's check: c_level="standard", m_type="cabin" → not major keywords
    # is_major = False (c_level != "major", no major keywords, cabin not in [ifc, cargo])
    # So minor → CVE=4, ICA=3 → cert = 25 + 4 + 3 = 32.0
    assert est.certification_engineer == 32.0
    assert est.project_manager == 15.0
    assert est.total_hours() == 177.0

def test_fleet_scaling_learning_curve():
    """Test NRE/Recurring model produces reasonable scaling for various fleet sizes."""
    # 1 aircraft → factor = 1.0
    assert calculate_fleet_scaling(1, "cabin") == 1.0
    
    # 5 aircraft, cabin (NRE=0.70): should be > 1.0 and < 5.0
    factor_5 = calculate_fleet_scaling(5, "cabin")
    assert factor_5 > 1.0
    assert factor_5 < 5.0
    
    # 50 aircraft should show economies of scale (factor < linear 5.9)
    factor_50 = calculate_fleet_scaling(50, "cabin")
    assert factor_50 < 5.9  # Linear model would give 5.9
    assert factor_50 > 3.0  # But still substantial
    
    # Cargo (NRE=0.55) should scale more than cabin (more recurring)
    factor_cargo_10 = calculate_fleet_scaling(10, "cargo")
    factor_cabin_10 = calculate_fleet_scaling(10, "cabin")
    assert factor_cargo_10 > factor_cabin_10

def test_scope_keyword_inference_expanded():
    """Test expanded scope keywords trigger correct complexity inference."""
    # Major keyword: "radome" (new in v2.0.0)
    est_radome = estimate_manhours(modification_type="structural", scope_text="Radome antenna cutout modification")
    # Should be classified as major
    assert est_radome.structural_engineer >= BASELINE_HOURS["structural"]["major"]["structural_engineer"]
    
    # Minor keyword: "placard" (new in v2.0.0)
    est_placard = estimate_manhours(modification_type="cabin", scope_text="Replace placard labels")
    assert est_placard.cabin_design_engineer == BASELINE_HOURS["cabin"]["minor"]["cabin_design_engineer"]

def test_fallback_defaults():
    est = estimate_manhours(modification_type=None, complexity=None, fleet_size=None)
    assert est.total_hours() > 0

# === v2.0.0 DAL 5-Tier Tests ===

def test_dal_5_tier_multipliers():
    """Verify all 5 DAL levels return correct multipliers."""
    assert get_dal_multiplier("DAL A") == 2.4
    assert get_dal_multiplier("Level A") == 2.4
    assert get_dal_multiplier("A") == 2.4
    assert get_dal_multiplier("DAL-A") == 2.4
    
    assert get_dal_multiplier("DAL B") == 2.0
    assert get_dal_multiplier("B") == 2.0
    assert get_dal_multiplier("DAL-B") == 2.0
    
    assert get_dal_multiplier("DAL C") == 1.5
    assert get_dal_multiplier("C") == 1.5
    assert get_dal_multiplier("Level C") == 1.5
    
    assert get_dal_multiplier("DAL D") == 1.15
    assert get_dal_multiplier("D") == 1.15
    assert get_dal_multiplier("DAL-D") == 1.15
    
    assert get_dal_multiplier("DAL E") == 1.0
    assert get_dal_multiplier("E") == 1.0
    assert get_dal_multiplier(None) == 1.0
    assert get_dal_multiplier("") == 1.0

def test_dal_a_vs_b_different():
    """DAL A and DAL B must produce different results (unlike v1.x where both were 2.2x)."""
    est_a = estimate_manhours(modification_type="avionics", complexity="standard", dal_level="DAL A")
    est_b = estimate_manhours(modification_type="avionics", complexity="standard", dal_level="DAL B")
    assert est_a.certification_engineer > est_b.certification_engineer
    assert est_a.avionics_design_engineer > est_b.avionics_design_engineer

def test_dal_c_vs_d_different():
    """DAL C and DAL D must produce different results (unlike v1.x where both were 1.3x)."""
    est_c = estimate_manhours(modification_type="avionics", complexity="standard", dal_level="DAL C")
    est_d = estimate_manhours(modification_type="avionics", complexity="standard", dal_level="DAL D")
    assert est_c.certification_engineer > est_d.certification_engineer
    assert est_c.avionics_design_engineer > est_d.avionics_design_engineer

# === Structural DAL Impact Tests ===

def test_structural_dal_impact():
    """Structural engineer should get 50% DAL impact."""
    est_e = estimate_manhours(modification_type="structural", complexity="standard", dal_level="E")
    est_a = estimate_manhours(modification_type="structural", complexity="standard", dal_level="DAL A")
    # Structural hours should increase with DAL A, but less than cert/avionics
    assert est_a.structural_engineer > est_e.structural_engineer
    # The increase should be 50% of full DAL multiplier effect
    # Full DAL A mult = 2.4, so structural mult = 1.0 + (2.4-1.0)*0.5 = 1.7
    # Ratio should be approximately 1.7
    ratio = est_a.structural_engineer / est_e.structural_engineer
    assert abs(ratio - 1.7) < 0.1

# === CS-23 All-Role Reduction Tests ===

def test_cs23_all_roles_reduction():
    """CS-23 should reduce ALL roles, not just certification."""
    est_cs25 = estimate_manhours(modification_type="avionics", complexity="standard", aircraft_type="A320")
    est_cs23 = estimate_manhours(modification_type="avionics", complexity="standard", aircraft_type="King Air 350")
    
    # All roles should be lower for CS-23
    assert est_cs23.cabin_design_engineer < est_cs25.cabin_design_engineer
    assert est_cs23.structural_engineer < est_cs25.structural_engineer
    assert est_cs23.avionics_design_engineer < est_cs25.avionics_design_engineer
    assert est_cs23.certification_engineer < est_cs25.certification_engineer
    assert est_cs23.project_manager < est_cs25.project_manager

def test_resolve_cert_basis():
    assert resolve_cert_basis("A320-200") == "CS-25"
    assert resolve_cert_basis("Boeing 737-800") == "CS-25"
    assert resolve_cert_basis("Cessna 172 Skyhawk") == "CS-23"
    assert resolve_cert_basis("King Air 350") == "CS-23"

# === CVE Mod-Type Sensitivity Tests ===

def test_cve_mod_type_sensitivity():
    """CVE hours should differ by modification type."""
    info_cabin_minor = classify_part21_change("Replace carpet", "cabin", "minor")
    info_ifc_stc = classify_part21_change("Install Wi-Fi STC radome", "ifc", "major")
    
    assert info_cabin_minor["cve_hours"] == CVE_HOURS_TABLE["minor"]["cabin"]
    assert info_ifc_stc["cve_hours"] == CVE_HOURS_TABLE["stc"]["ifc"]
    assert info_ifc_stc["cve_hours"] > info_cabin_minor["cve_hours"]

def test_classify_part21_change():
    minor_info = classify_part21_change("Replace cabin carpet and seat covers", "cabin", "minor")
    assert minor_info["is_major_change"] is False
    assert minor_info["requires_stc"] is False
    assert minor_info["cve_hours"] == CVE_HOURS_TABLE["minor"]["cabin"]
    
    major_info = classify_part21_change("Install fuselage Wi-Fi radome antenna cutout STC", "ifc", "major")
    assert major_info["is_major_change"] is True
    assert major_info["requires_stc"] is True
    assert major_info["cve_hours"] == CVE_HOURS_TABLE["stc"]["ifc"]

# === ICA Hours Tests ===

def test_ica_hours_included():
    """ICA hours should be included in classify_part21_change output."""
    info = classify_part21_change("Standard avionics upgrade", "avionics", "standard")
    assert "ica_hours" in info
    assert info["ica_hours"] > 0

def test_ica_hours_scale_with_classification():
    """STC projects should have more ICA hours than minor changes."""
    minor_info = classify_part21_change("Simple carpet swap", "cabin", "minor")
    stc_info = classify_part21_change("Cargo door STC conversion", "cargo", "major")
    assert stc_info["ica_hours"] > minor_info["ica_hours"]

# === EWIS Hours Tests ===

def test_ewis_hours_addition():
    """IFC/IFE/ISPS/avionics should include EWIS additional hours."""
    # IFC standard: avionics baseline=140 + EWIS=20 = 160 (before DAL/CS23/fleet)
    est_ifc = estimate_manhours(modification_type="ifc", complexity="standard", fleet_size=1)
    ifc_avionics_base = BASELINE_HOURS["ifc"]["standard"]["avionics_design_engineer"]
    ewis_extra = EWIS_ADDITIONAL_HOURS["ifc"]["standard"]
    # Without DAL, the avionics hours should be base + EWIS
    assert est_ifc.avionics_design_engineer == ifc_avionics_base + ewis_extra

def test_ewis_no_hours_for_cabin():
    """Pure cabin mods should have no EWIS additional hours."""
    assert "cabin" not in EWIS_ADDITIONAL_HOURS

# === Fleet Scaling Model Tests ===

def test_fleet_scaling_single_aircraft():
    assert calculate_fleet_scaling(1) == 1.0
    assert calculate_fleet_scaling(0) == 1.0  # Edge case: 0 → clamped to 1

def test_fleet_scaling_diminishing_returns():
    """Marginal cost per aircraft should decrease with fleet size."""
    factor_10 = calculate_fleet_scaling(10)
    factor_20 = calculate_fleet_scaling(20)
    factor_40 = calculate_fleet_scaling(40)
    
    marginal_10_20 = (factor_20 - factor_10) / 10  # cost per additional aircraft
    marginal_20_40 = (factor_40 - factor_20) / 20
    assert marginal_20_40 < marginal_10_20  # Diminishing returns

# === New Project Types ===

def test_new_project_types_estimation():
    ifc_est = estimate_manhours(modification_type="ifc", complexity="standard", fleet_size=1)
    assert ifc_est.structural_engineer == 90.0
    # Avionics = 140 base + 20 EWIS = 160
    assert ifc_est.avionics_design_engineer == 160.0
    
    isps_est = estimate_manhours(modification_type="isps", complexity="minor", fleet_size=1)
    # Avionics = 35 base + 5 EWIS = 40
    assert isps_est.avionics_design_engineer == 40.0

# === Gap Detection ===

def test_zero_fleet_size_gap():
    from src.gaps import check_gaps
    gaps = check_gaps({"aircraft_type": "A320", "fleet_size": 0, "modification_type": "cabin", "customer_name": "Test", "scope": "Valid scope"})
    assert "fleet_size" in gaps
