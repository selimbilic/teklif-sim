"""
Unit and Integration Tests for v3.0.0 Phase 1:
- Document Parsing (PDF, Excel, Word, Text)
- PII & Privacy Anonymization
- Gemini Pro Multimodal Integration
"""

import pytest
import io
import pandas as pd
from src.parser import parse_uploaded_file, parse_pdf, parse_excel, parse_word
from src.privacy import anonymize_text


def test_parse_text_file():
    content = b"Aircraft: B737-800\nFleet Size: 5\nScope: IFC Wi-Fi Installation"
    result = parse_uploaded_file("request.txt", content)
    assert "B737-800" in result
    assert "IFC Wi-Fi" in result


def test_parse_excel_file():
    df = pd.DataFrame({
        "Aircraft": ["A320-200", "B777-300ER"],
        "Quantity": [10, 4],
        "Scope": ["Cabin LOPA", "Cargo Conversion"]
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Fleet_Manifest")
    
    excel_bytes = buffer.getvalue()
    result = parse_uploaded_file("fleet_manifest.xlsx", excel_bytes)
    assert "A320-200" in result
    assert "B777-300ER" in result
    assert "Sheet: Fleet_Manifest" in result


def test_parse_word_file():
    docx = pytest.importorskip("docx")
    doc = docx.Document()
    doc.add_heading("Customer Specification", level=1)
    doc.add_paragraph("Airline: Flagship Air. Fleet size: 12 aircraft. Scope: Glass Cockpit Avionics.")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    word_bytes = buffer.getvalue()
    
    result = parse_uploaded_file("specification.docx", word_bytes)
    assert "Flagship Air" in result
    assert "Glass Cockpit Avionics" in result


def test_privacy_anonymization_emails_phones():
    raw_text = "Contact Manager john.doe@airline-corp.com or call +1 555-019-2834 for A320 quote."
    clean_text = anonymize_text(raw_text)
    assert "john.doe@airline-corp.com" not in clean_text
    assert "+1 555-019-2834" not in clean_text
    assert "A320" in clean_text


def test_unsupported_file_format():
    result = parse_uploaded_file("archive.zip", b"binarydata")
    assert "Unsupported file type" in result
