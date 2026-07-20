import os
from typing import List
from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.gaps import get_field_description

load_dotenv()

# Fallback templates in case the LLM is unavailable
FALLBACK_TEMPLATES = {
    "en": """Dear Customer,

Thank you for contacting AeroDesign with your modification request. In order for us to begin the engineering assessment and prepare a detailed proposal, we kindly require the following missing information:

{bullet_points}

Please provide these details at your earliest convenience so that we can proceed with your quote.

Kind regards,

AeroDesign Proposal Engineering Team""",
    
    "tr": """Sayın Yetkili,

Tarafımıza iletmiş olduğunuz modifikasyon teklif talebi için teşekkür ederiz. Projeniz üzerinde çalışmaya başlayabilmemiz ve sağlıklı bir teklif sunabilmemiz için aşağıdaki eksik bilgilere ihtiyaç duymaktayız:

{bullet_points}

Lütfen bu detayları bizimle paylaşırsanız, en kısa sürede fiyat ve zaman çizelgemizi hazırlayıp ileteceğiz.

Saygılarımızla,

AeroDesign Proposal Engineering Team"""
}

def get_fallback_email(missing_fields: List[str], language: str) -> str:
    """
    Generates a polite clarification request using a local template.
    """
    lang = language.lower() if language else "en"
    if lang not in FALLBACK_TEMPLATES:
        lang = "en"
        
    # Format the missing fields descriptions
    bullet_points = ""
    for field in missing_fields:
        desc = get_field_description(field)
        if lang == "tr":
            # Simple TR translation of descriptions if needed, otherwise use description
            tr_desc = {
                "aircraft_type": "Uçak Modeli (örn. A320, B737)",
                "fleet_size": "Filo Büyüklüğü (uçak sayısı)",
                "modification_type": "Modifikasyon Türü (kabin, yapısal, aviyonik)",
                "customer_name": "Havayolu Müşteri Adı",
                "manhours": "Tahmini Mühendislik Adam-Saat Dağılımı"
            }.get(field, desc)
            bullet_points += f"  • {tr_desc}\n"
        else:
            bullet_points += f"  • {desc}\n"
            
    return FALLBACK_TEMPLATES[lang].format(bullet_points=bullet_points.rstrip())

def draft_clarification_email(original_email: str, missing_fields: List[str], language: str) -> str:
    """
    Drafts a polite email requesting the missing fields from the customer.
    Uses the Gemini API if available, falls back to a template if not.
    """
    if not missing_fields:
        return ""

    lang = language.lower() if language else "en"
    if lang not in ["tr", "en"]:
        lang = "en"

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] No GEMINI_API_KEY found. Using fallback template.")
        return get_fallback_email(missing_fields, lang)

    # Convert field keys to descriptions
    missing_descriptions = [f"{f} ({get_field_description(f)})" for f in missing_fields]
    
    system_instruction = """
    You are a professional proposal engineer at AeroDesign (an aircraft design organisation).
    You need to write a polite reply to a customer request email to ask for missing fields.

    Guidelines:
    1. Write the email in the requested language.
    2. Be professional, polite, and clear.
    3. List the missing fields as bullet points so they are easy to read.
    4. If the language is Turkish, use formal Turkish business greetings and sign-offs (e.g., "Sayın Yetkili", "Saygılarımızla").
    5. Do not include any placeholder text like "[Your Name]". Sign off as "AeroDesign Proposal Engineering Team".
    """

    prompt = f"""
    Original Customer Email:
    ---
    {original_email}
    ---
    
    Missing Fields to Ask For:
    {', '.join(missing_descriptions)}
    
    Requested Language: {lang.upper()}
    """

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"[!] Gemini drafting failed: {e}. Using fallback template.")
        return get_fallback_email(missing_fields, lang)
