"""
Unit and Integration Tests for v3.0.0 Phase 3:
- FastAPI Enterprise REST API Endpoints (/health, /api/v1/quote, /api/v1/proposals)
- OpenAPI / Swagger documentation compliance
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "TEKLİF-Sim Enterprise API" in data["service"]


def test_calculate_quote_endpoint_success():
    payload = {
        "aircraft_type": "B737-800",
        "customer_class": "flagship",
        "pricing_strategy": "competitive",
        "fleet_size": 6,
        "modification_type": "ifc",
        "complexity": "standard",
        "currency": "EUR"
    }
    response = client.post("/api/v1/quote", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "proposal_id" in data
    assert data["currency"] == "EUR"
    assert data["total_price_converted"] > 0
    assert "total_price_formatted" in data
    assert "quote_breakdown" in data
    assert data["quote_breakdown"]["margin_applied"] > 0


def test_calculate_quote_endpoint_invalid_role():
    payload = {
        "aircraft_type": "A320-200",
        "customer_class": "third_party",
        "pricing_strategy": "competitive",
        "fleet_size": 1,
        "modification_type": "cabin",
        "complexity": "standard",
        "manhours": {
            "unknown_role_xyz": 50.0
        }
    }
    response = client.post("/api/v1/quote", json=payload)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Unknown engineering role" in detail


def test_get_proposals_endpoint():
    response = client.get("/api/v1/proposals?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
