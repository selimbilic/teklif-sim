"""
Unit and Integration Tests for v3.0.0 Phase 2:
- Free Public FX Rates (ECB XML & Fallback Rates)
- Currency Conversion & Formatting (USD, EUR, GBP, TRY)
- Database Persistence & Proposal History CRUD (SQLAlchemy)
"""

import pytest
import os
from src.forex import convert_currency, format_currency, fetch_ecb_rates, FALLBACK_RATES
from src.database import save_proposal, list_proposals, ProposalRecord


def test_fetch_ecb_rates():
    rates = fetch_ecb_rates()
    assert "USD" in rates
    assert "EUR" in rates
    assert "GBP" in rates
    assert "TRY" in rates
    assert rates["USD"] == 1.0
    assert rates["EUR"] > 0.0
    assert rates["TRY"] > 0.0


def test_currency_conversion():
    usd_val = 1000.0
    eur_val = convert_currency(usd_val, "EUR")
    gbp_val = convert_currency(usd_val, "GBP")
    try_val = convert_currency(usd_val, "TRY")

    assert eur_val > 0
    assert gbp_val > 0
    assert try_val > 0
    assert convert_currency(usd_val, "USD") == 1000.0


def test_format_currency():
    assert "$" in format_currency(1234.56, "USD")
    assert "€" in format_currency(1234.56, "EUR")
    assert "£" in format_currency(1234.56, "GBP")
    assert "₺" in format_currency(1234.56, "TRY")


def test_database_save_and_list_proposal():
    rec = save_proposal(
        customer_name="Test Airline",
        customer_class="flagship",
        aircraft_type="A320-200",
        fleet_size=5,
        modification_type="cabin",
        pricing_strategy="competitive",
        currency="EUR",
        total_manhours=250.0,
        labor_cost=25000.0,
        contingency_cost=1000.0,
        materials_cost=500.0,
        testing_cost=800.0,
        total_price_usd=27300.0,
        total_price_converted=25116.0,
        deterministic_hash="abc123hash"
    )

    assert rec.proposal_id.startswith("PROP-")
    assert rec.customer_name == "Test Airline"
    assert rec.aircraft_type == "A320-200"

    # Verify retrieval
    proposals = list_proposals(search_query="Test Airline")
    assert len(proposals) >= 1
    found = [p for p in proposals if p["customer_name"] == "Test Airline"]
    assert len(found) >= 1
    assert found[0]["currency"] == "EUR"
