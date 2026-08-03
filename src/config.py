"""
Centralized Configuration Loader for TEKLİF-Sim (v2.1.0).
Loads application settings from config/settings.yaml with safe defaults.
"""

import os
import json
from typing import Dict, Any

# Resolve configuration file path
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "settings.yaml")

DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {"name": "TEKLİF-Sim", "version": "2.1.0", "environment": "production"},
    "pricing": {
        "hourly_rate_default": 120.00,
        "contingency_default": 0.05,
        "urgency_surcharges": {"normal": 1.00, "rush": 1.25, "aog": 1.50}
    },
    "volume_discounts": {
        "tier_1": {"min_fleet": 20, "discount_rate": 0.05},
        "tier_2": {"min_fleet": 50, "discount_rate": 0.10}
    },
    "ewis_complexity_weights": {
        "widebody": 1.40,
        "narrowbody": 1.00,
        "regional": 0.70
    },
    "rate_card_defaults": {
        "cabin_design_engineer": 95.00,
        "structural_engineer": 110.00,
        "avionics_design_engineer": 105.00,
        "certification_engineer": 80.00,
        "project_manager": 120.00
    }
}

def load_config() -> Dict[str, Any]:
    """
    Loads YAML configuration from config/settings.yaml.
    Falls back gracefully to DEFAULT_CONFIG if PyYAML or file is unavailable.
    """
    if os.path.exists(CONFIG_PATH):
        try:
            import yaml
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                if isinstance(cfg, dict):
                    return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG

# Active configuration instance
CONFIG = load_config()
