from typing import List, Union, Dict
from src.extract import EmailExtraction

REQUIRED_FIELDS = {
    "aircraft_type": "Aircraft Model (e.g., A320, B737)",
    "fleet_size": "Fleet Size (number of aircraft)",
    "modification_type": "Modification Type (cabin, structural, avionics)",
    "customer_name": "Customer Airline Name",
    "scope": "Modification Scope Details"
}

def check_gaps(facts: Union[EmailExtraction, dict]) -> List[str]:
    """
    Checks the extracted facts for missing fields required to generate a proposal.
    Note: Customer-provided manhours is NO LONGER a required field, as AeroDesign
    DOA Estimation Engine automatically estimates man-hours from scope parameters.
    Returns a list of missing field keys.
    """
    missing_fields = []
    
    # Standardize facts to dictionary if it is a Pydantic model
    if isinstance(facts, EmailExtraction):
        facts_dict = facts.model_dump()
    else:
        facts_dict = facts

    # Check each required field
    for field in REQUIRED_FIELDS:
        val = facts_dict.get(field)
        
        # Field is missing if it is None or empty
        if val is None:
            missing_fields.append(field)
        elif isinstance(val, str) and not val.strip():
            missing_fields.append(field)
        elif field == "fleet_size" and isinstance(val, (int, float)) and val <= 0:
            missing_fields.append(field)
        elif field == "scope" and isinstance(val, str):
            # Flag vague scope statements
            vague_keywords = ["vague", "some modification", "need price", "general check", "unspecified"]
            if any(k in val.lower() for k in vague_keywords):
                missing_fields.append(field)
            
    return missing_fields

def get_field_description(field_key: str) -> str:
    """
    Returns the user-friendly description of a missing field.
    """
    return REQUIRED_FIELDS.get(field_key, field_key)
