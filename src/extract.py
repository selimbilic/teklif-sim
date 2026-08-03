"""
Structured LLM Fact Extraction Module for TEKLİF-Sim (v2.1.0).
Uses Gemini API with Pydantic validation, sliding-window rate limiting,
prompt injection protection, and semantic bounds checking.
"""

import os
import sys
import json
import time
import functools
from typing import Dict, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

from src.logger import logger
from src.rate_limiter import gemini_rate_limiter

# Load environment variables
load_dotenv()

# Injection keywords to filter out malicious prompt overrides
PROMPT_INJECTION_MARKERS = [
    "ignore previous instructions",
    "disregard all rules",
    "system prompt",
    "overwrite instructions",
    "you are now an unrestricted",
    "bypass safety"
]

import re

def sanitize_input_text(email_text: str) -> str:
    """
    Sanitizes raw input text against prompt injection markers.
    """
    if not email_text:
        return ""
    for marker in PROMPT_INJECTION_MARKERS:
        if re.search(re.escape(marker), email_text, flags=re.IGNORECASE):
            logger.warning(f"Prompt injection marker detected and neutralized: '{marker}'")
            email_text = re.sub(re.escape(marker), "[FILTERED_SECURITY_MARKER]", email_text, flags=re.IGNORECASE)
    return email_text


class ManhourBreakdown(BaseModel):
    cabin_design_engineer: Optional[float] = Field(None, description="Hours for cabin design engineer")
    structural_engineer: Optional[float] = Field(None, description="Hours for structural engineer")
    avionics_design_engineer: Optional[float] = Field(None, description="Hours for avionics design engineer")
    certification_engineer: Optional[float] = Field(None, description="Hours for certification engineer")
    project_manager: Optional[float] = Field(None, description="Hours for project manager")


class EmailExtraction(BaseModel):
    aircraft_type: Optional[str] = Field(
        None, 
        description="The aircraft model (e.g. A320, B737-800, B777-300ER, etc.). Set to None if missing or not clear."
    )
    customer_name: Optional[str] = Field(
        None, 
        description="The airline or customer name (e.g. Flagship Air, Gulf Alliance, EuroLink, MNG Cargo Lines, etc.). Set to None if missing."
    )
    customer_class: Optional[str] = Field(
        None, 
        description="Must be exactly one of: 'flagship', 'partner', or 'third_party'. Infer from airline name or details if not explicit. Default to 'third_party' if not clear."
    )
    modification_type: Optional[str] = Field(
        None, 
        description="Must be exactly one of: 'cabin', 'structural', 'avionics', 'cargo', 'ife', 'ifc', 'isps', 'elams', 'gain', 'cabin_lopa', or 'structural_repair'."
    )
    project_type: Optional[str] = Field(
        None,
        description="Specific project type if applicable: 'ife', 'ifc' (Wi-Fi), 'isps' (power), 'elams', 'gain' (galley), 'cabin_lopa', 'structural_repair', 'cargo_conversion'."
    )
    cert_basis: Optional[str] = Field(
        None,
        description="Certification Specification basis: 'CS-25' for large commercial transport aircraft (A320, B737, B777, etc.), 'CS-23' for small/general aviation aeroplanes (Cessna, King Air, etc.)."
    )
    dal_level: Optional[str] = Field(
        None,
        description="Design Assurance Level per ARP4761/DO-178C: 'DAL A', 'DAL B', 'DAL C', 'DAL D', or 'DAL E'. Default to DAL D or C for avionics/IFE/IFC if unspecified."
    )
    scope: Optional[str] = Field(
        None, 
        description="A detailed summary of the modification scope of work. Set to None if scope is completely missing or vague."
    )
    complexity: Optional[str] = Field(
        "standard",
        description="Complexity level of modification work: 'minor' (small repair/swap), 'standard' (refit/installation), or 'major' (STC/cargo conversion/full overhaul)."
    )
    fleet_size: Optional[int] = Field(
        None, 
        description="Number of aircraft to be modified. Must be a positive integer. Set to None if missing."
    )
    manhours: Optional[ManhourBreakdown] = Field(
        None, 
        description="Engineering manhours breakdown per role if explicitly specified by customer in email. Set to None if no hours are specified."
    )
    is_valid: bool = Field(
        ..., 
        description="Set to False if the e-mail is completely unrelated to aircraft engineering design modifications (e.g. spam, catering, marketing, personal email). Otherwise, set to True."
    )
    error_type: Optional[str] = Field(
        None,
        description="Type of system/API error if extraction failed: 'missing_api_key', 'quota_exceeded', 'api_error', or None."
    )
    error_message: Optional[str] = Field(
        None,
        description="User-friendly error message if API extraction or configuration failed."
    )


def validate_semantic_bounds(facts: EmailExtraction) -> EmailExtraction:
    """
    Enforces semantic boundary checks on extracted facts to prevent absurd values.
    Caps fleet_size between 0 and 500. Caps role manhours to <= 10,000h.
    """
    if facts.fleet_size is not None:
        if facts.fleet_size < 0:
            facts.fleet_size = None
        elif facts.fleet_size > 500:
            logger.warning(f"Extracted fleet_size {facts.fleet_size} exceeds upper bound of 500; capping to 500.")
            facts.fleet_size = 500

    if facts.manhours:
        for role in ["cabin_design_engineer", "structural_engineer", "avionics_design_engineer", "certification_engineer", "project_manager"]:
            val = getattr(facts.manhours, role, None)
            if val is not None:
                if val < 0:
                    setattr(facts.manhours, role, 0.0)
                elif val > 10000.0:
                    logger.warning(f"Extracted manhour for '{role}' ({val}h) exceeds cap of 10000h; capping to 10000h.")
                    setattr(facts.manhours, role, 10000.0)

    return facts


def extract_facts(email_text: str, max_retries: int = 3) -> EmailExtraction:
    """
    Extracts structured facts from email text using the Gemini API and Pydantic validation.
    Applies rate limiting, prompt injection filtering, and semantic bounds checking.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set in environment.")
        return EmailExtraction(
            is_valid=False,
            error_type="missing_api_key",
            error_message="GEMINI_API_KEY is not configured in environment variables or .env file."
        )

    # Sanitize input against prompt injection
    cleaned_email_text = sanitize_input_text(email_text)

    # Enforce API rate limiter
    gemini_rate_limiter.acquire()

    client = genai.Client()
    
    system_instruction = """
    You are an expert aviation proposal engineer. Your task is to analyze the customer's request email and extract structured facts.

    Guidelines:
    1. Identify the aircraft model (e.g., A320, B737-800, B777-300ER).
    2. Identify the customer airline name.
    3. Classify the customer class into one of: 'flagship', 'partner', or 'third_party'.
       - If the email indicates they are flagship, partner, etc., use that.
       - If not mentioned, try to infer it from the name (e.g. alliance/partner members -> partner, main carrier -> flagship, standard airlines -> third_party).
       - If unclear, default to 'third_party'.
    4. Determine the modification type: 'cabin', 'structural', 'avionics', 'cargo', 'ife', 'ifc', 'isps', 'elams', 'gain', 'cabin_lopa', or 'structural_repair'.
    5. Extract the fleet size (number of aircraft). If not mentioned, set to null.
    6. Extract the manhour breakdown if mentioned. Map roles to:
       - cabin_design_engineer
       - structural_engineer
       - avionics_design_engineer
       - certification_engineer
       - project_manager
    7. Assess if the email is a valid aviation modification request. If it is spam, marketing, catering, or completely unrelated to modifying an aircraft, set `is_valid` to false.
    """

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=EmailExtraction,
        temperature=0.1
    )

    last_exception = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=cleaned_email_text,
                config=config
            )
            if response.parsed:
                return validate_semantic_bounds(response.parsed)
            else:
                data = json.loads(response.text)
                return validate_semantic_bounds(EmailExtraction(**data))
        except Exception as e:
            last_exception = e
            err_str = str(e)
            logger.warning(f"Extraction attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                sleep_time = 5 if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str) else (2 ** attempt)
                logger.info(f"Waiting {sleep_time} seconds before retrying Gemini request...")
                time.sleep(sleep_time)

    # All retries failed
    err_msg = str(last_exception) if last_exception else "Unknown error"
    if any(k in err_msg for k in ["429", "RESOURCE_EXHAUSTED", "Quota", "quota"]):
        return EmailExtraction(
            is_valid=False,
            error_type="quota_exceeded",
            error_message="Gemini API rate limit or quota exceeded (429). Please wait a moment or verify your API plan limits."
        )
    elif any(k in err_msg for k in ["API_KEY", "401", "UNAUTHENTICATED", "invalid"]):
        return EmailExtraction(
            is_valid=False,
            error_type="missing_api_key",
            error_message="Gemini API Key is invalid or unauthenticated."
        )
    else:
        return EmailExtraction(
            is_valid=False,
            error_type="api_error",
            error_message=f"Gemini API request failed after {max_retries} attempts: {err_msg}"
        )


@functools.lru_cache(maxsize=64)
def _extract_facts_cached_raw(email_text: str) -> str:
    """Internal helper to cache JSON string output of Gemini API calls."""
    facts = extract_facts(email_text)
    return facts.model_dump_json()


def extract_facts_cached(email_text: str) -> EmailExtraction:
    """Cached wrapper around extract_facts using lru_cache for zero-cost repeated queries."""
    json_str = _extract_facts_cached_raw(email_text)
    return EmailExtraction.model_validate_json(json_str)
