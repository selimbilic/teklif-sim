"""
Unit and Integration Tests for v3.0.0 Phase 4 & Phase 5:
- Monte-Carlo Risk Simulation (P10 / P50 / P90 confidence intervals)
- Corporate PDF (ReportLab) and Word (python-docx) Proposal Export Engine
"""

import pytest
from src.simulation import run_monte_carlo_simulation
from src.export import generate_pdf_proposal, generate_docx_proposal


def test_monte_carlo_simulation():
    res = run_monte_carlo_simulation(base_manhours=500.0, base_cost=50000.0, complexity="standard")
    assert "p10" in res
    assert "p50" in res
    assert "p90" in res
    assert res["p10"]["cost"] <= res["p50"]["cost"] <= res["p90"]["cost"]
    assert res["p10"]["manhours"] <= res["p50"]["manhours"] <= res["p90"]["manhours"]
    assert res["risk_buffer_usd"] >= 0.0


def test_generate_pdf_proposal():
    payload = {
        "customer_name": "Flagship Air",
        "aircraft_type": "A320-200",
        "fleet_size": 5,
        "modification_type": "cabin",
        "currency": "USD",
        "scope_text": "Cabin LOPA seating refit",
        "total_price_usd": 45000.0,
        "total_price_formatted": "$45,000.00 USD",
        "quote_breakdown": {
            "base_labor_cost_adjusted": 30000.0,
            "contingency": 3000.0,
            "material_allowance": 7500.0,
            "testing_fee": 4500.0,
            "volume_discount": 0.0,
            "volume_discount_rate": 0.0
        }
    }
    pdf_bytes = generate_pdf_proposal(payload)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_generate_docx_proposal():
    payload = {
        "customer_name": "Flagship Air",
        "aircraft_type": "A320-200",
        "fleet_size": 5,
        "modification_type": "cabin",
        "currency": "EUR",
        "scope_text": "Cabin LOPA seating refit",
        "total_price_usd": 45000.0,
        "total_price_formatted": "€39,150.00 EUR",
        "quote_breakdown": {}
    }
    docx_bytes = generate_docx_proposal(payload)
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 500
    # ZIP PK magic header for docx files
    assert docx_bytes.startswith(b"PK")
