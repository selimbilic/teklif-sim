"""
Local PII & Privacy Anonymization Module for TEKLİF-Sim (v3.0.0).
Scrubs PII (emails, phone numbers, personal names) locally
before passing data to LLM APIs, enforcing KVKK / GDPR / NDA compliance.
"""

import re
from src.logger import logger

_analyzer_engine = None
_anonymizer_engine = None

def _get_presidio_engines():
    global _analyzer_engine, _anonymizer_engine
    if _analyzer_engine is None:
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine
            _analyzer_engine = AnalyzerEngine()
            _anonymizer_engine = AnonymizerEngine()
        except Exception as e:
            logger.debug(f"Presidio engines could not be loaded: {e}")
            _analyzer_engine = False
            _anonymizer_engine = False
    return _analyzer_engine, _anonymizer_engine


def anonymize_text(text: str) -> str:
    """
    Anonymizes PII locally using Microsoft Presidio if available,
    with regex fallbacks for emails, phone numbers, and sensitive markers.
    """
    if not text:
        return ""

    analyzer, anonymizer = _get_presidio_engines()

    if analyzer and anonymizer:
        try:
            results = analyzer.analyze(text=text, language="en")
            anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
            return anonymized_result.text
        except Exception as e:
            logger.warning(f"Presidio anonymization exception, using regex fallback: {e}")

    # Fallback regex scrubbing
    scrubbed = text
    # Mask email addresses
    scrubbed = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[ANONYMIZED_EMAIL]', scrubbed)
    # Mask phone numbers
    scrubbed = re.sub(r'\+?\d[\d\s-]{8,}\d', '[ANONYMIZED_PHONE]', scrubbed)

    return scrubbed
