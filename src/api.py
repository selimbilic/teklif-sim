"""
FastAPI Enterprise REST API Module for TEKLİF-Sim (v3.0.0).
Exposes pricing calculation, fact extraction, gap analysis,
and proposal history endpoints for ERP/SAP and CRM integration.
"""

from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query, Body, status
from pydantic import BaseModel, Field

from src.__version__ import __version__
from src.extract import extract_facts, EmailExtraction
from src.gaps import check_gaps
from src.pricing import calculate_quote
from src.forex import convert_currency, format_currency
from src.database import save_proposal, list_proposals

app = FastAPI(
    title="TEKLİF-Sim Enterprise REST API",
    description="EASA Part 21J DOA Aircraft Modification Proposal & Pricing Simulation Engine API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)


class FactExtractionRequest(BaseModel):
    text: str = Field(..., description="Customer request email text or document content", json_schema_extra={"example": "We need to install Wi-Fi IFC on 6 B737-800 aircraft for Flagship Air."})


class QuoteCalculationRequest(BaseModel):
    aircraft_type: str = Field(..., json_schema_extra={"example": "A320-200"})
    customer_class: str = Field("third_party", json_schema_extra={"example": "flagship"})
    pricing_strategy: str = Field("competitive", json_schema_extra={"example": "competitive"})
    fleet_size: int = Field(1, ge=1, le=500, json_schema_extra={"example": 5})
    modification_type: str = Field("cabin", json_schema_extra={"example": "cabin"})
    complexity: str = Field("standard", json_schema_extra={"example": "standard"})
    scope_text: Optional[str] = Field(None, json_schema_extra={"example": "Cabin LOPA refit and seating upgrade"})
    dal_level: Optional[str] = Field(None, json_schema_extra={"example": "DAL D"})
    currency: str = Field("USD", json_schema_extra={"example": "EUR"})
    manhours: Optional[Dict[str, float]] = Field(None, description="Optional customer-provided manhours per role")


@app.get("/health", tags=["System"])
def health_check():
    """Healthcheck endpoint verifying API operational status."""
    return {
        "status": "operational",
        "service": "TEKLİF-Sim Enterprise API",
        "version": __version__
    }


@app.post("/api/v1/extract", tags=["LLM Extraction"])
def extract_facts_endpoint(req: FactExtractionRequest):
    """Extracts structured facts from raw customer RFP text using PII-scrubbed Gemini API."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    facts = extract_facts(req.text)
    gaps = check_gaps(facts)
    return {
        "facts": facts.model_dump(),
        "gaps": gaps,
        "is_ready_for_proposal": len(gaps) == 0
    }


@app.post("/api/v1/quote", tags=["Pricing Engine"])
def calculate_quote_endpoint(req: QuoteCalculationRequest):
    """Calculates a deterministic proposal quote and converts to requested currency."""
    try:
        quote = calculate_quote(
            manhours=req.manhours,
            customer_class=req.customer_class,
            strategy_string=req.pricing_strategy,
            fleet_size=req.fleet_size,
            modification_type=req.modification_type,
            complexity=req.complexity,
            scope_text=req.scope_text,
            aircraft_type=req.aircraft_type,
            dal_level=req.dal_level
        )
        
        total_usd = quote["total_cost"]
        converted_val = convert_currency(total_usd, req.currency)
        formatted_str = format_currency(converted_val, req.currency)
        
        # Save to database
        total_hrs = sum([v for v in quote["manhours_used"].values() if v is not None])
        saved_rec = save_proposal(
            customer_name=None,
            customer_class=req.customer_class,
            aircraft_type=req.aircraft_type,
            fleet_size=req.fleet_size,
            modification_type=req.modification_type,
            pricing_strategy=req.pricing_strategy,
            currency=req.currency,
            total_manhours=total_hrs,
            labor_cost=quote.get("base_labor_cost_adjusted", 0.0),
            contingency_cost=quote.get("contingency", 0.0),
            materials_cost=quote.get("material_allowance", 0.0),
            testing_cost=quote.get("testing_fee", 0.0),
            total_price_usd=total_usd,
            total_price_converted=converted_val,
            deterministic_hash=quote.get("deterministic_hash", "N/A")
        )
        
        return {
            "proposal_id": saved_rec.proposal_id,
            "currency": req.currency.upper(),
            "total_price_converted": converted_val,
            "total_price_formatted": formatted_str,
            "total_price_usd": total_usd,
            "quote_breakdown": quote
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pricing engine error: {e}")


from fastapi.responses import Response
from src.simulation import run_monte_carlo_simulation
from src.export import generate_pdf_proposal, generate_docx_proposal

@app.get("/api/v1/proposals", tags=["Database & CRM"])
def get_proposals_endpoint(
    limit: int = Query(50, ge=1, le=500),
    q: Optional[str] = Query(None, description="Search query by customer, aircraft, ID, or mod type")
):
    """Retrieves saved proposal records from database."""
    return list_proposals(limit=limit, search_query=q)


@app.post("/api/v1/simulate", tags=["Risk Simulation"])
def simulate_risk_endpoint(req: QuoteCalculationRequest):
    """Runs a 1,000-run Monte-Carlo simulation to calculate P10/P50/P90 risk confidence intervals."""
    try:
        quote = calculate_quote(
            manhours=req.manhours,
            customer_class=req.customer_class,
            strategy_string=req.pricing_strategy,
            fleet_size=req.fleet_size,
            modification_type=req.modification_type,
            complexity=req.complexity,
            scope_text=req.scope_text,
            aircraft_type=req.aircraft_type,
            dal_level=req.dal_level
        )
        total_hrs = sum([v for v in quote["manhours_used"].values() if v is not None])
        sim_result = run_monte_carlo_simulation(
            base_manhours=total_hrs,
            base_cost=quote["total_cost"],
            complexity=req.complexity
        )
        return {
            "aircraft_type": req.aircraft_type,
            "fleet_size": req.fleet_size,
            "currency": req.currency,
            "simulation": sim_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {e}")


@app.post("/api/v1/export/pdf", tags=["Document Export"])
def export_pdf_endpoint(proposal_data: Dict[str, Any] = Body(...)):
    """Generates and downloads an official EASA Part 21 format PDF proposal document."""
    try:
        pdf_bytes = generate_pdf_proposal(proposal_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=proposal_quotation.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export error: {e}")


@app.post("/api/v1/export/docx", tags=["Document Export"])
def export_docx_endpoint(proposal_data: Dict[str, Any] = Body(...)):
    """Generates and downloads an official Word DOCX proposal document."""
    try:
        docx_bytes = generate_docx_proposal(proposal_data)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=proposal_quotation.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX export error: {e}")
