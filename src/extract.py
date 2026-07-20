import os
import sys
import json
import time
from typing import Dict, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        description="Must be exactly one of: 'cabin', 'structural', or 'avionics'."
    )
    scope: Optional[str] = Field(
        None, 
        description="A short summary of the modification scope of work."
    )
    fleet_size: Optional[int] = Field(
        None, 
        description="Number of uçağı/aircraft to be modified. Must be a positive integer. Set to None if missing."
    )
    manhours: Optional[ManhourBreakdown] = Field(
        None, 
        description="Engineering manhours breakdown per role. Set to None if no hours are specified."
    )
    is_valid: bool = Field(
        ..., 
        description="Set to False if the e-mail is completely unrelated to aircraft engineering design modifications (e.g. spam, catering, marketing, personal email). Otherwise, set to True."
    )

def extract_facts(email_text: str, max_retries: int = 3) -> EmailExtraction:
    """
    Extracts structured facts from email text using the Gemini API and Pydantic validation.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] Warning: GEMINI_API_KEY is not set in extract.py. Returning default model.")
        return EmailExtraction(is_valid=False)

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
    4. Determine the modification type: 'cabin' (interiors, seats, galleys, carpets), 'structural' (repairs, mounts, fuselage penetrations), or 'avionics' (displays, Wi-Fi, wiring, ADS-B).
    5. Extract the fleet size (number of aircraft). If not mentioned, set to null.
    6. Extract the manhour breakdown if mentioned. Map roles to:
       - cabin_design_engineer
       - structural_engineer
       - avionics_design_engineer
       - certification_engineer
       - project_manager
       Note: Map the text descriptions to these precise database role keys.
    7. Assess if the email is a valid aviation modification request. If it is spam, marketing, catering, or completely unrelated to modifying an aircraft, set `is_valid` to false.
    """

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=EmailExtraction,
        temperature=0.1
    )

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=email_text,
                config=config
            )
            # Response is automatically parsed into the Pydantic schema because we specified response_schema
            if response.parsed:
                return response.parsed
            else:
                # Fallback parse in case response.parsed is None (rare in new SDK when response_schema is set)
                data = json.loads(response.text)
                return EmailExtraction(**data)
        except Exception as e:
            print(f"[!] Extraction attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                sleep_time = 20 if "429" in str(e) else (2 ** attempt)
                print(f"[!] Sleeping for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
            else:
                print("[!] All extraction attempts failed.")
                raise e

    return EmailExtraction(is_valid=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/extract.py <path_to_email_txt>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        email_content = f.read()

    try:
        facts = extract_facts(email_content)
        print(facts.model_dump_json(indent=2))
    except Exception as err:
        print(f"Error during extraction: {err}")
        sys.exit(1)
