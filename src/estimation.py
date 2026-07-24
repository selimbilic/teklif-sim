"""
DOA Engineering Man-Hour Estimation Engine for Aircraft Modifications.
Provides deterministic man-hour estimates per role based on modification category,
EASA Part 21 classification (21.A.91), CS-25 / CS-23 certification basis, ARP4761 DAL levels,
and fleet size scaling.
"""

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
    Determines if change is Minor or Major (STC) and calculates Part 21.A.239(d)(2) CVE hours.
    """
    scope = (scope_text or "").lower()
    m_type = (mod_type or "cabin").lower()
    c_level = (complexity or "standard").lower()
    
    major_keywords = [
        "stc", "supplemental type certificate", "cargo door", "freighter", "p2f",
        "wi-fi radome", "antenna cutout", "major", "glass cockpit", "overhaul", "16g seat"
    ]
    
    is_major = (c_level == "major") or any(w in scope for w in major_keywords) or (m_type in ["ifc", "cargo"])
    requires_stc = is_major and (c_level == "major" or "stc" in scope or m_type in ["cargo", "ifc"])
    
    clause = "21.A.91 (Major - STC Required)" if requires_stc else ("21.A.91 (Major Change)" if is_major else "21.A.91 (Minor Change)")
    cve_hours = 25.0 if requires_stc else (15.0 if is_major else 6.0)
    
    return {
        "is_major_change": is_major,
        "requires_stc": requires_stc,
        "clause": clause,
        "cve_hours": cve_hours
    }

def get_dal_multiplier(dal_level: Optional[str]) -> float:
    """
    Returns safety assessment engineering multiplier based on ARP4761 / DO-178C DAL level:
    - DAL A / B (Catastrophic / Hazardous): 2.2x
    - DAL C / D (Major / Minor): 1.3x
    - DAL E (No Safety Effect): 1.0x
    """
    if not dal_level:
        return 1.0
    dal = dal_level.upper().strip()
    if "DAL A" in dal or "DAL B" in dal:
        return 2.2
    elif "DAL C" in dal or "DAL D" in dal:
        return 1.3
    return 1.0

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
    ARP4761 safety DAL multipliers, and fleet size scaling.
    """
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

    c_level = (complexity or "standard").lower().strip()
    if c_level not in ["minor", "standard", "major"]:
        c_level = "standard"

    if scope_text:
        s_lower = scope_text.lower()
        if any(w in s_lower for w in ["stc", "cargo door", "conversion", "major", "glass cockpit", "overhaul"]):
            c_level = "major"
        elif any(w in s_lower for w in ["minor", "simple", "carpet", "outlet", "display swap", "label"]):
            c_level = "minor"

    base_dict = BASELINE_HOURS[mod_type][c_level].copy()

    # Apply ARP4761 / DO-178C DAL Safety Multiplier to Certification & Avionics Hours
    dal_mult = get_dal_multiplier(dal_level)
    base_dict["certification_engineer"] = round(base_dict["certification_engineer"] * dal_mult, 1)
    base_dict["avionics_design_engineer"] = round(base_dict["avionics_design_engineer"] * dal_mult, 1)

    # Fleet size scaling: 1st aircraft = 1.0, each additional aircraft adds 10% adaptation/verification hours
    flt_sz = max(1, fleet_size if fleet_size is not None else 1)
    fleet_scaling_factor = 1.0 + (flt_sz - 1) * 0.10

    scaled_hours = {
        role: round(hours * fleet_scaling_factor, 1)
        for role, hours in base_dict.items()
    }

    return ManhourEstimate(**scaled_hours)
