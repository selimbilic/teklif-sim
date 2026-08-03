"""
DOA Engineering Man-Hour Estimation Engine for Aircraft Modifications (v2.0.0).

Provides deterministic man-hour estimates per role based on modification category,
EASA Part 21 classification (21.A.91), CS-25 / CS-23 certification basis,
ARP4761 / DO-178C DAL levels (5-tier), EWIS (CS 25.1707), ICA (CS-25.1529),
and NRE/Recurring fleet size scaling with Wright 80% learning curve.

References:
- DO-178C Annex A (Table A-1 → A-7): Objectives per DAL level
- ARP4761: FHA, PSSA, SSA safety assessment process
- ARP4754A: Development Assurance Level assignment
- EASA Part 21.A.91 / GM 21.A.91: Minor/Major change classification
- EASA Part 21.A.239(d): CVE independent verification
- CS-25.1529 / Appendix H to Part 25: ICA requirements
- CS 25.1707-1733 (Subpart H) / AMC 20-21: EWIS compliance
- Wright Learning Curve (T.P. Wright, 1936): Fleet cost scaling
"""

import math
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

class ManhourEstimate(BaseModel):
    cabin_design_engineer: float = Field(0.0, description="Hours for cabin design engineer")
    structural_engineer: float = Field(0.0, description="Hours for structural engineer")
    avionics_design_engineer: float = Field(0.0, description="Hours for avionics design engineer")
    certification_engineer: float = Field(0.0, description="Hours for certification engineer")
    project_manager: float = Field(0.0, description="Hours for project manager")
    
    def total_hours(self) -> float:
        return (
            self.cabin_design_engineer +
            self.structural_engineer +
            self.avionics_design_engineer +
            self.certification_engineer +
            self.project_manager
        )

# Baseline man-hours per modification category & complexity for 1st aircraft
BASELINE_HOURS: Dict[str, Dict[str, Dict[str, float]]] = {
    "cabin": {
        "minor": {"cabin_design_engineer": 25.0, "structural_engineer": 5.0, "avionics_design_engineer": 0.0, "certification_engineer": 10.0, "project_manager": 5.0},
        "standard": {"cabin_design_engineer": 80.0, "structural_engineer": 40.0, "avionics_design_engineer": 10.0, "certification_engineer": 25.0, "project_manager": 15.0},
        "major": {"cabin_design_engineer": 200.0, "structural_engineer": 90.0, "avionics_design_engineer": 30.0, "certification_engineer": 60.0, "project_manager": 40.0}
    },
    "structural": {
        "minor": {"cabin_design_engineer": 5.0, "structural_engineer": 35.0, "avionics_design_engineer": 0.0, "certification_engineer": 15.0, "project_manager": 10.0},
        "standard": {"cabin_design_engineer": 20.0, "structural_engineer": 110.0, "avionics_design_engineer": 15.0, "certification_engineer": 35.0, "project_manager": 15.0},
        "major": {"cabin_design_engineer": 50.0, "structural_engineer": 300.0, "avionics_design_engineer": 30.0, "certification_engineer": 100.0, "project_manager": 50.0}
    },
    "avionics": {
        "minor": {"cabin_design_engineer": 5.0, "structural_engineer": 0.0, "avionics_design_engineer": 30.0, "certification_engineer": 15.0, "project_manager": 10.0},
        "standard": {"cabin_design_engineer": 30.0, "structural_engineer": 20.0, "avionics_design_engineer": 110.0, "certification_engineer": 30.0, "project_manager": 20.0},
        "major": {"cabin_design_engineer": 50.0, "structural_engineer": 50.0, "avionics_design_engineer": 250.0, "certification_engineer": 90.0, "project_manager": 50.0}
    },
    "cargo": {
        "minor": {"cabin_design_engineer": 30.0, "structural_engineer": 100.0, "avionics_design_engineer": 30.0, "certification_engineer": 40.0, "project_manager": 20.0},
        "standard": {"cabin_design_engineer": 60.0, "structural_engineer": 220.0, "avionics_design_engineer": 80.0, "certification_engineer": 80.0, "project_manager": 40.0},
        "major": {"cabin_design_engineer": 100.0, "structural_engineer": 350.0, "avionics_design_engineer": 150.0, "certification_engineer": 120.0, "project_manager": 80.0}
    },
    "ife": {
        "minor": {"cabin_design_engineer": 15.0, "structural_engineer": 5.0, "avionics_design_engineer": 40.0, "certification_engineer": 15.0, "project_manager": 10.0},
        "standard": {"cabin_design_engineer": 45.0, "structural_engineer": 25.0, "avionics_design_engineer": 130.0, "certification_engineer": 35.0, "project_manager": 25.0},
        "major": {"cabin_design_engineer": 90.0, "structural_engineer": 60.0, "avionics_design_engineer": 260.0, "certification_engineer": 80.0, "project_manager": 50.0}
    },
    "ifc": {
        "minor": {"cabin_design_engineer": 10.0, "structural_engineer": 25.0, "avionics_design_engineer": 50.0, "certification_engineer": 20.0, "project_manager": 15.0},
        "standard": {"cabin_design_engineer": 30.0, "structural_engineer": 90.0, "avionics_design_engineer": 140.0, "certification_engineer": 45.0, "project_manager": 30.0},
        "major": {"cabin_design_engineer": 60.0, "structural_engineer": 210.0, "avionics_design_engineer": 280.0, "certification_engineer": 110.0, "project_manager": 60.0}
    },
    "isps": {
        "minor": {"cabin_design_engineer": 15.0, "structural_engineer": 10.0, "avionics_design_engineer": 35.0, "certification_engineer": 15.0, "project_manager": 10.0},
        "standard": {"cabin_design_engineer": 40.0, "structural_engineer": 25.0, "avionics_design_engineer": 100.0, "certification_engineer": 30.0, "project_manager": 20.0},
        "major": {"cabin_design_engineer": 75.0, "structural_engineer": 50.0, "avionics_design_engineer": 190.0, "certification_engineer": 65.0, "project_manager": 40.0}
    },
    "elams": {
        "minor": {"cabin_design_engineer": 0.0, "structural_engineer": 0.0, "avionics_design_engineer": 25.0, "certification_engineer": 10.0, "project_manager": 5.0},
        "standard": {"cabin_design_engineer": 5.0, "structural_engineer": 5.0, "avionics_design_engineer": 60.0, "certification_engineer": 20.0, "project_manager": 10.0},
        "major": {"cabin_design_engineer": 10.0, "structural_engineer": 10.0, "avionics_design_engineer": 120.0, "certification_engineer": 40.0, "project_manager": 20.0}
    },
    "gain": {
        "minor": {"cabin_design_engineer": 20.0, "structural_engineer": 10.0, "avionics_design_engineer": 25.0, "certification_engineer": 15.0, "project_manager": 10.0},
        "standard": {"cabin_design_engineer": 50.0, "structural_engineer": 30.0, "avionics_design_engineer": 70.0, "certification_engineer": 30.0, "project_manager": 20.0},
        "major": {"cabin_design_engineer": 100.0, "structural_engineer": 70.0, "avionics_design_engineer": 130.0, "certification_engineer": 60.0, "project_manager": 40.0}
    },
    "cabin_lopa": {
        "minor": {"cabin_design_engineer": 30.0, "structural_engineer": 10.0, "avionics_design_engineer": 5.0, "certification_engineer": 15.0, "project_manager": 10.0},
        "standard": {"cabin_design_engineer": 90.0, "structural_engineer": 45.0, "avionics_design_engineer": 15.0, "certification_engineer": 35.0, "project_manager": 20.0},
        "major": {"cabin_design_engineer": 220.0, "structural_engineer": 110.0, "avionics_design_engineer": 35.0, "certification_engineer": 75.0, "project_manager": 45.0}
    },
    "structural_repair": {
        "minor": {"cabin_design_engineer": 0.0, "structural_engineer": 40.0, "avionics_design_engineer": 0.0, "certification_engineer": 15.0, "project_manager": 10.0},
        "standard": {"cabin_design_engineer": 10.0, "structural_engineer": 130.0, "avionics_design_engineer": 0.0, "certification_engineer": 35.0, "project_manager": 15.0},
        "major": {"cabin_design_engineer": 25.0, "structural_engineer": 320.0, "avionics_design_engineer": 10.0, "certification_engineer": 90.0, "project_manager": 45.0}
    }
}

# ---------------------------------------------------------------------------
# [2.4] EWIS Additional Hours (CS 25.1707-1733 / AMC 20-21)
# Added to avionics_design_engineer baseline for EWIS-intensive mod types.
# Covers: wiring routing, separation analysis, flammability assessment,
# EZAP (Enhanced Zonal Analysis Procedure), wire harness design.
# ---------------------------------------------------------------------------
EWIS_ADDITIONAL_HOURS: Dict[str, Dict[str, int]] = {
    "ifc":      {"minor": 8,  "standard": 20, "major": 40},
    "ife":      {"minor": 5,  "standard": 15, "major": 30},
    "isps":     {"minor": 5,  "standard": 12, "major": 25},
    "avionics": {"minor": 3,  "standard": 10, "major": 20},
    "elams":    {"minor": 2,  "standard": 5,  "major": 10},
    "cargo":    {"minor": 5,  "standard": 15, "major": 35},
}

# EWIS aircraft category complexity multipliers (v2.1.0 Parametric Model)
# CS 25.1707 EWIS routing analysis scales with aircraft size and harness run lengths
EWIS_AIRCRAFT_WEIGHTS: Dict[str, float] = {
    "widebody": 1.40,   # A330, A350, A380, B777, B787, B747
    "narrowbody": 1.00, # A320, B737, E190, CS300
    "regional": 0.70    # King Air, ATR, Cessna, Beechcraft
}

def get_ewis_complexity_weight(aircraft_type: Optional[str]) -> float:
    """
    Returns EWIS wiring complexity weight based on aircraft size/category.
    """
    if not aircraft_type:
        return 1.0
    ac = aircraft_type.lower().strip()
    if any(wb in ac for wb in ["a330", "a350", "a380", "b777", "b787", "b747", "widebody"]):
        return EWIS_AIRCRAFT_WEIGHTS["widebody"]
    elif any(reg in ac for reg in ["king air", "cessna", "atr", "beechcraft", "piper"]):
        return EWIS_AIRCRAFT_WEIGHTS["regional"]
    return EWIS_AIRCRAFT_WEIGHTS["narrowbody"]


# ---------------------------------------------------------------------------
# [2.1] CVE Hours Table — Mod-type sensitive (Part 21.A.239(d))
# CVE effort scales with number of compliance items, LoI, and discipline depth.
# ---------------------------------------------------------------------------
CVE_HOURS_TABLE: Dict[str, Dict[str, float]] = {
    "minor": {
        "cabin": 4, "structural": 6, "avionics": 8, "cargo": 10,
        "ifc": 10, "ife": 6, "isps": 5, "elams": 4,
        "gain": 5, "cabin_lopa": 5, "structural_repair": 6,
    },
    "major": {
        "cabin": 12, "structural": 20, "avionics": 25, "cargo": 30,
        "ifc": 30, "ife": 18, "isps": 12, "elams": 10,
        "gain": 14, "cabin_lopa": 14, "structural_repair": 18,
    },
    "stc": {
        "cabin": 20, "structural": 40, "avionics": 50, "cargo": 65,
        "ifc": 60, "ife": 35, "isps": 20, "elams": 15,
        "gain": 25, "cabin_lopa": 25, "structural_repair": 35,
    },
}

# ---------------------------------------------------------------------------
# [2.3] ICA Hours Table — CS-25.1529 / Appendix H to Part 25
# Instructions for Continued Airworthiness: AMM Supplement, WM Supplement,
# IPC Update, maintenance task cards, EZAP documentation.
# ---------------------------------------------------------------------------
ICA_HOURS_TABLE: Dict[str, Dict[str, float]] = {
    "minor": {
        "cabin": 3, "structural": 5, "avionics": 6, "cargo": 8,
        "ifc": 8, "ife": 5, "isps": 4, "elams": 3,
        "gain": 4, "cabin_lopa": 4, "structural_repair": 5,
    },
    "major": {
        "cabin": 10, "structural": 18, "avionics": 20, "cargo": 25,
        "ifc": 22, "ife": 15, "isps": 10, "elams": 8,
        "gain": 12, "cabin_lopa": 12, "structural_repair": 16,
    },
    "stc": {
        "cabin": 18, "structural": 35, "avionics": 40, "cargo": 55,
        "ifc": 45, "ife": 28, "isps": 18, "elams": 12,
        "gain": 20, "cabin_lopa": 20, "structural_repair": 30,
    },
}

# ---------------------------------------------------------------------------
# [1.1] DO-178C Annex A Objective-Proportional DAL Multipliers
#
# DO-178C Table A-1 → A-7 objective counts:
#   DAL A (Catastrophic) : 71 objectives — MC/DC + Object Code Verification
#   DAL B (Hazardous)    : 69 objectives — Decision Coverage + Independence
#   DAL C (Major)        : 62 objectives — Statement Coverage
#   DAL D (Minor)        : 26 objectives — Basic verification only
#   DAL E (No Effect)    :  0 objectives — No software process control
#
# Effort relationship is exponential, not linear (industry consensus).
# DAL B→A: incremental (~%20 extra for MC/DC + OCV) [afuzion.com, medium.com]
# DAL D→C: major jump (26→62 objectives, %138 increase)
# ---------------------------------------------------------------------------
DAL_MULTIPLIERS: Dict[str, float] = {
    "A": 2.4,   # Catastrophic: MC/DC + OCV required
    "B": 2.0,   # Hazardous: Decision Coverage + Independence
    "C": 1.5,   # Major: Statement Coverage
    "D": 1.15,  # Minor: Basic verification
    "E": 1.0,   # No Safety Effect
}

# ---------------------------------------------------------------------------
# [2.2] Scope Text → Complexity Inference Keywords (Expanded)
# Reference: EASA FAQ table of design change classification, GM 21.A.91
# ---------------------------------------------------------------------------
MAJOR_SCOPE_KEYWORDS = [
    "stc", "supplemental type certificate",
    "cargo door", "freighter", "p2f", "passenger to freighter",
    "conversion", "major", "glass cockpit", "overhaul",
    "radome", "antenna cutout", "16g seat", "16 g seat",
    "emergency exit", "overwing exit",
    "structural repair doubler", "cockpit upgrade",
    "cargo net", "barrier net", "decompression panel",
    "fuel tank", "auxiliary fuel", "winglet",
    "engine change", "re-engine",
    "floor beam", "cargo floor", "cargo loading system",
]

MINOR_SCOPE_KEYWORDS = [
    "minor", "simple", "carpet", "outlet", "display swap", "label",
    "placard", "decal", "nameplate",
    "non-structural", "non structural", "cosmetic",
    "paint", "livery", "stripe",
    "seat cover", "curtain", "divider",
    "usb", "reading light",
]

# ---------------------------------------------------------------------------
# [1.3] NRE vs Recurring ratios per modification category
# NRE (Non-Recurring Engineering): design + certification + test → done once
# Recurring: adaptation + ICA per aircraft → scales with learning curve
# ---------------------------------------------------------------------------
NRE_RATIO: Dict[str, float] = {
    "cabin": 0.70,
    "structural": 0.60,
    "avionics": 0.65,
    "cargo": 0.55,
    "ifc": 0.60,
    "ife": 0.65,
    "isps": 0.70,
    "elams": 0.75,
    "gain": 0.65,
    "cabin_lopa": 0.65,
    "structural_repair": 0.50,
}

# ---------------------------------------------------------------------------
# [1.4] CS-23 All-Role Reduction Factors
# CS-23 vs CS-25 effort ratio: 3:1 (simple) to 10:1+ (complex)
# CS-23: smaller cabin, single door, simpler EWIS, safe-life structures
# ---------------------------------------------------------------------------
CS23_REDUCTION_FACTORS: Dict[str, float] = {
    "cabin_design_engineer": 0.55,
    "structural_engineer": 0.60,
    "avionics_design_engineer": 0.65,
    "certification_engineer": 0.50,
    "project_manager": 0.70,
}


def resolve_cert_basis(aircraft_type: Optional[str]) -> str:
    """
    Determines fixed-wing Certification Specification basis:
    - CS-25: Large commercial transport aeroplanes (A320, B737, B777, A350, E190, etc.)
    - CS-23: Small / General Aviation / Commuter aeroplanes (Cessna, King Air, Diamond, etc.)
    """
    if not aircraft_type:
        return "CS-25"
    
    act_lower = aircraft_type.lower().strip()
    cs23_keywords = [
        "cessna", "c172", "c182", "c208", "caravan", "king air", "kingair", "b200", "b300", "b350",
        "diamond", "da42", "da62", "baron", "bonanza", "piper", "pa-28", "pa-34", "cirrus", "sr22",
        "tbm", "pc-12", "pc-24", "beechcraft", "piston", "turboprop general"
    ]
    if any(k in act_lower for k in cs23_keywords):
        return "CS-23"
    return "CS-25"


def classify_part21_change(scope_text: Optional[str], mod_type: str, complexity: str) -> Dict[str, Any]:
    """
    EASA Part 21.A.91 Modification Classification:
    Determines if change is Minor or Major (STC) and calculates:
    - Part 21.A.239(d)(2) CVE hours (mod-type sensitive)
    - CS-25.1529 ICA preparation hours (mod-type sensitive)
    """
    scope = (scope_text or "").lower()
    m_type = (mod_type or "cabin").lower()
    c_level = (complexity or "standard").lower()
    
    # [2.2] Expanded major keyword detection
    is_major = (
        (c_level == "major") or
        any(w in scope for w in MAJOR_SCOPE_KEYWORDS) or
        (m_type in ["ifc", "cargo"])
    )
    requires_stc = is_major and (
        c_level == "major" or
        "stc" in scope or
        m_type in ["cargo", "ifc"]
    )
    
    clause = (
        "21.A.91 (Major - STC Required)" if requires_stc
        else ("21.A.91 (Major Change)" if is_major else "21.A.91 (Minor Change)")
    )
    
    # [2.1] CVE hours — mod-type sensitive
    if requires_stc:
        cve_hours = CVE_HOURS_TABLE["stc"].get(m_type, 25.0)
    elif is_major:
        cve_hours = CVE_HOURS_TABLE["major"].get(m_type, 15.0)
    else:
        cve_hours = CVE_HOURS_TABLE["minor"].get(m_type, 6.0)
    
    # [2.3] ICA hours — CS-25.1529 / Appendix H to Part 25
    if requires_stc:
        ica_hours = ICA_HOURS_TABLE["stc"].get(m_type, 18.0)
    elif is_major:
        ica_hours = ICA_HOURS_TABLE["major"].get(m_type, 10.0)
    else:
        ica_hours = ICA_HOURS_TABLE["minor"].get(m_type, 3.0)
    
    return {
        "is_major_change": is_major,
        "requires_stc": requires_stc,
        "clause": clause,
        "cve_hours": float(cve_hours),
        "ica_hours": float(ica_hours),
    }


def get_dal_multiplier(dal_level: Optional[str]) -> float:
    """
    Returns safety assessment engineering multiplier based on ARP4761 / DO-178C DAL level.
    
    5-tier multiplier system derived from DO-178C Annex A objective counts:
    - DAL A (Catastrophic): 71 objectives, MC/DC + OCV → 2.4x
    - DAL B (Hazardous):    69 objectives, Decision Coverage → 2.0x
    - DAL C (Major):        62 objectives, Statement Coverage → 1.5x
    - DAL D (Minor):        26 objectives, Basic verification → 1.15x
    - DAL E (No Effect):     0 objectives → 1.0x
    
    Flexible string matching for 'DAL A', 'Level A', 'A', 'DAL-A', etc.
    """
    if not dal_level:
        return 1.0
    dal = dal_level.upper().strip()
    # Extract single letter from various formats
    for letter in ["A", "B", "C", "D", "E"]:
        if (
            letter == dal or
            f"DAL {letter}" in dal or
            f"LEVEL {letter}" in dal or
            f"DAL-{letter}" in dal
        ):
            return DAL_MULTIPLIERS[letter]
    return 1.0


def calculate_fleet_scaling(fleet_size: int, mod_type: str = "cabin") -> float:
    """
    NRE/Recurring model with Wright 80% learning curve for fleet cost scaling.
    
    NRE (Non-Recurring Engineering): Design + certification + test → done once.
    Recurring: Adaptation + ICA per aircraft → decreases with learning.
    
    Wright Learning Curve: Y_x = a * X^b, b = ln(0.80)/ln(2) ≈ -0.322
    Each time production doubles, cumulative average cost drops to 80%.
    
    Reference: T.P. Wright (1936), METU aerospace cost estimation
    """
    n = max(1, fleet_size)
    if n == 1:
        return 1.0
    
    nre_ratio = NRE_RATIO.get(mod_type, 0.65)
    recurring_ratio = 1.0 - nre_ratio
    
    # NRE component: Fixed, already fully included in 1st aircraft baseline
    nre_component = nre_ratio
    
    # Recurring component: Wright 80% learning curve
    learning_exponent = math.log(0.80) / math.log(2)  # ≈ -0.322
    cumulative_avg = n ** learning_exponent
    total_recurring = cumulative_avg * n
    recurring_component = recurring_ratio * total_recurring
    
    return nre_component + recurring_component


def estimate_manhours(
    modification_type: Optional[str] = "cabin",
    complexity: Optional[str] = "standard",
    fleet_size: Optional[int] = 1,
    scope_text: Optional[str] = None,
    aircraft_type: Optional[str] = None,
    dal_level: Optional[str] = None
) -> ManhourEstimate:
    """
    Estimates engineering man-hours deterministically based on modification category,
    complexity, scope keywords, certification specification (CS-25 / CS-23),
    ARP4761/DO-178C 5-tier DAL safety multipliers, EWIS compliance (CS 25.1707),
    ICA preparation (CS-25.1529), and NRE/Recurring fleet size scaling.
    """
    # 1. Resolve modification type
    mod_type = (modification_type or "cabin").lower().strip()
    if mod_type not in BASELINE_HOURS:
        if "wifi" in mod_type or "connectivity" in mod_type or "satcom" in mod_type:
            mod_type = "ifc"
        elif "ife" in mod_type or "entertainment" in mod_type:
            mod_type = "ife"
        elif "power" in mod_type or "isps" in mod_type or "outlet" in mod_type:
            mod_type = "isps"
        elif "elams" in mod_type or "load analysis" in mod_type:
            mod_type = "elams"
        elif "galley" in mod_type or "oven" in mod_type or "gain" in mod_type:
            mod_type = "gain"
        elif "lopa" in mod_type or "seat layout" in mod_type:
            mod_type = "cabin_lopa"
        elif "cargo" in mod_type or "p2f" in mod_type or "freighter" in mod_type:
            mod_type = "cargo"
        elif "repair" in mod_type or "doubler" in mod_type:
            mod_type = "structural_repair"
        elif "struct" in mod_type:
            mod_type = "structural"
        elif "avion" in mod_type:
            mod_type = "avionics"
        else:
            mod_type = "cabin"

    # 2. Resolve complexity with expanded keyword inference
    c_level = (complexity or "standard").lower().strip()
    if c_level not in ["minor", "standard", "major"]:
        c_level = "standard"

    if scope_text:
        s_lower = scope_text.lower()
        if any(w in s_lower for w in MAJOR_SCOPE_KEYWORDS):
            c_level = "major"
        elif any(w in s_lower for w in MINOR_SCOPE_KEYWORDS):
            c_level = "minor"

    # 3. Get baseline hours
    base_dict = BASELINE_HOURS[mod_type][c_level].copy()

    # 4. [2.4 / 4.5] Add EWIS hours (CS 25.1707-1733 / AMC 20-21) with parametric aircraft weight
    ewis_base_extra = EWIS_ADDITIONAL_HOURS.get(mod_type, {}).get(c_level, 0)
    ewis_weight = get_ewis_complexity_weight(aircraft_type)
    ewis_extra = round(ewis_base_extra * ewis_weight, 1)
    base_dict["avionics_design_engineer"] += ewis_extra

    # 5. [2.1 + 2.3] Add CVE + ICA hours to certification engineer
    part21_info = classify_part21_change(scope_text, mod_type, c_level)
    base_dict["certification_engineer"] += part21_info["cve_hours"]
    base_dict["certification_engineer"] += part21_info["ica_hours"]

    # 6. [1.4] Apply CS-23 vs CS-25 all-role reduction factors
    cert_basis = resolve_cert_basis(aircraft_type)
    if cert_basis == "CS-23":
        for role, factor in CS23_REDUCTION_FACTORS.items():
            if role in base_dict:
                base_dict[role] = round(base_dict[role] * factor, 1)

    # 7. [1.1 + 1.2] Apply ARP4761 / DO-178C 5-tier DAL Safety Multipliers
    dal_mult = get_dal_multiplier(dal_level)
    
    # Certification & Avionics: Full DAL multiplier (DO-178C/DO-254 processes)
    base_dict["certification_engineer"] = round(base_dict["certification_engineer"] * dal_mult, 1)
    base_dict["avionics_design_engineer"] = round(base_dict["avionics_design_engineer"] * dal_mult, 1)
    
    # Structural: Reduced DAL impact (50% ratio)
    # Rationale: Structural analysis depth increases (DT/fatigue) but no DO-178C process
    structural_dal_mult = 1.0 + (dal_mult - 1.0) * 0.5
    base_dict["structural_engineer"] = round(base_dict["structural_engineer"] * structural_dal_mult, 1)

    # 8. [1.3] Fleet size scaling: NRE/Recurring model with Wright 80% learning curve
    flt_sz = max(1, fleet_size if fleet_size is not None else 1)
    fleet_factor = calculate_fleet_scaling(flt_sz, mod_type)

    scaled_hours = {
        role: round(hours * fleet_factor, 1)
        for role, hours in base_dict.items()
    }

    return ManhourEstimate(**scaled_hours)
