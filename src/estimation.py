"""
DOA Engineering Man-Hour Estimation Engine for Aircraft Modifications.
Provides deterministic man-hour estimates per role based on modification category,
scope details, complexity level, and fleet size scaling.
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
        "minor": {
            "cabin_design_engineer": 25.0,
            "structural_engineer": 5.0,
            "avionics_design_engineer": 0.0,
            "certification_engineer": 10.0,
            "project_manager": 5.0,
        },
        "standard": {
            "cabin_design_engineer": 80.0,
            "structural_engineer": 40.0,
            "avionics_design_engineer": 10.0,
            "certification_engineer": 25.0,
            "project_manager": 15.0,
        },
        "major": {
            "cabin_design_engineer": 200.0,
            "structural_engineer": 90.0,
            "avionics_design_engineer": 30.0,
            "certification_engineer": 60.0,
            "project_manager": 40.0,
        }
    },
    "structural": {
        "minor": {
            "cabin_design_engineer": 5.0,
            "structural_engineer": 35.0,
            "avionics_design_engineer": 0.0,
            "certification_engineer": 15.0,
            "project_manager": 10.0,
        },
        "standard": {
            "cabin_design_engineer": 20.0,
            "structural_engineer": 110.0,
            "avionics_design_engineer": 15.0,
            "certification_engineer": 35.0,
            "project_manager": 15.0,
        },
        "major": {
            "cabin_design_engineer": 50.0,
            "structural_engineer": 300.0,
            "avionics_design_engineer": 30.0,
            "certification_engineer": 100.0,
            "project_manager": 50.0,
        }
    },
    "avionics": {
        "minor": {
            "cabin_design_engineer": 5.0,
            "structural_engineer": 0.0,
            "avionics_design_engineer": 30.0,
            "certification_engineer": 15.0,
            "project_manager": 10.0,
        },
        "standard": {
            "cabin_design_engineer": 30.0,
            "structural_engineer": 20.0,
            "avionics_design_engineer": 110.0,
            "certification_engineer": 30.0,
            "project_manager": 20.0,
        },
        "major": {
            "cabin_design_engineer": 50.0,
            "structural_engineer": 50.0,
            "avionics_design_engineer": 250.0,
            "certification_engineer": 90.0,
            "project_manager": 50.0,
        }
    },
    "cargo": {
        "minor": {
            "cabin_design_engineer": 30.0,
            "structural_engineer": 100.0,
            "avionics_design_engineer": 30.0,
            "certification_engineer": 40.0,
            "project_manager": 20.0,
        },
        "standard": {
            "cabin_design_engineer": 60.0,
            "structural_engineer": 220.0,
            "avionics_design_engineer": 80.0,
            "certification_engineer": 80.0,
            "project_manager": 40.0,
        },
        "major": {
            "cabin_design_engineer": 100.0,
            "structural_engineer": 350.0,
            "avionics_design_engineer": 150.0,
            "certification_engineer": 120.0,
            "project_manager": 80.0,
        }
    }
}

def estimate_manhours(
    modification_type: Optional[str] = "cabin",
    complexity: Optional[str] = "standard",
    fleet_size: Optional[int] = 1,
    scope_text: Optional[str] = None
) -> ManhourEstimate:
    """
    Estimates engineering man-hours deterministically based on modification category,
    complexity, scope keywords, and fleet size.
    """
    # Normalize inputs
    mod_type = (modification_type or "cabin").lower().strip()
    if mod_type not in BASELINE_HOURS:
        # Map alternative descriptions
        if "cargo" in mod_type or "p2f" in mod_type or "freighter" in mod_type:
            mod_type = "cargo"
        elif "struct" in mod_type or "repair" in mod_type:
            mod_type = "structural"
        elif "avion" in mod_type or "wifi" in mod_type or "ife" in mod_type:
            mod_type = "avionics"
        else:
            mod_type = "cabin"

    c_level = (complexity or "standard").lower().strip()
    if c_level not in ["minor", "standard", "major"]:
        c_level = "standard"

    # Infer complexity level from scope text if scope text is provided
    if scope_text:
        s_lower = scope_text.lower()
        if any(w in s_lower for w in ["stc", "cargo door", "conversion", "major", "glass cockpit", "overhaul"]):
            c_level = "major"
        elif any(w in s_lower for w in ["minor", "simple", "carpet", "outlet", "display swap", "label"]):
            c_level = "minor"

    # Retrieve baseline hours dictionary
    base_dict = BASELINE_HOURS[mod_type][c_level]

    # Fleet size scaling: 1st aircraft = 1.0, each additional aircraft adds 10% adaptation/verification hours
    flt_sz = max(1, fleet_size if fleet_size is not None else 1)
    fleet_scaling_factor = 1.0 + (flt_sz - 1) * 0.10

    scaled_hours = {
        role: round(hours * fleet_scaling_factor, 1)
        for role, hours in base_dict.items()
    }

    return ManhourEstimate(**scaled_hours)
