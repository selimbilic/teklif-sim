---
name: gemini-structured-extraction
description: Guides structured JSON data extraction and prompt engineering with the Gemini API. Crucial for mapping emails to Pydantic schemas and writing request drafts.
---

# Gemini Structured Extraction Guide

This skill ensures that all LLM calls to the Gemini API are structured, robust, and use Pydantic validation to avoid parsing errors.

## 1. Pydantic Model Integration
To ensure the Gemini API returns valid JSON that conforms to a specific structure, always use the `response_schema` parameter with a Pydantic model:

```python
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class ManhourBreakdown(BaseModel):
    cabin_design_engineer: Optional[float] = Field(description="Hours for cabin design engineer")
    structural_engineer: Optional[float] = Field(description="Hours for structural engineer")
    avionics_design_engineer: Optional[float] = Field(description="Hours for avionics design engineer")
    certification_engineer: Optional[float] = Field(description="Hours for certification engineer")
    project_manager: Optional[float] = Field(description="Hours for project manager")

class EmailExtraction(BaseModel):
    aircraft_type: Optional[str] = Field(description="Aircraft model, e.g. A320, B737-800")
    customer_name: Optional[str] = Field(description="Airline or customer name")
    customer_class: Optional[str] = Field(description="flagship, partner, or third_party")
    modification_type: Optional[str] = Field(description="cabin, structural, or avionics")
    scope: Optional[str] = Field(description="Detailed scope description")
    fleet_size: Optional[int] = Field(description="Number of aircraft to modify")
    manhours: Optional[ManhourBreakdown] = Field(description="Engineering manhours breakdown per role")
    is_valid: bool = Field(description="Set to false if email is spam or completely unrelated to aviation modification projects")
```

## 2. API Configuration (google-genai SDK)
Always use the `google-genai` SDK interface with the correct configuration parameters:

```python
from google import genai
from google.genai import types

client = genai.Client()
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=EmailExtraction,
    temperature=0.1  # Low temperature for factual extraction
)

response = client.models.generate_content(
    model='gemini-3.1-flash-lite',  # Default recommended model
    contents=email_text,
    config=config
)
```

## 3. Robust Error Handling and Fallbacks
- Wrap all Gemini API calls in `try/except` blocks.
- If JSON parsing fails or the API raises an exception, catch the error, write a log message, and retry (up to 3 times) with exponential backoff or use a fallback mechanism.
- For e-mail drafting (`draft_email.py`), if the Gemini API is completely unavailable, fall back to a local string-template formatting script (e.g. `f-string` filling).
