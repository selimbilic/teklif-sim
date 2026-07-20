from typing import Dict, List, Any
from src.extract import EmailExtraction

def generate_proposal_summary(
    facts: EmailExtraction, 
    gaps: List[str], 
    quote: Dict[str, float] = None,
    email_draft: str = ""
) -> str:
    """
    Generates a clean one-page proposal summary markdown report.
    """
    status = "⚠️ PENDING INFORMATION (EXSIK BILGI TALEBI)" if gaps else "✅ READY FOR REVIEW (TEKLİF HAZIR)"
    
    summary = f"""# PROPOSAL SUMMARY / TEKLİF ÖZETİ
**Status / Durum:** {status}

---

## 1. Customer & Request Facts / Müşteri ve Talep Bilgileri
- **Customer Airline / Havayolu:** {facts.customer_name or "Not Specified / Belirtilmemiş"}
- **Customer Class / Sınıfı:** {facts.customer_class or "Not Specified / Belirtilmemiş"}
- **Aircraft Type / Uçak Modeli:** {facts.aircraft_type or "Not Specified / Belirtilmemiş"}
- **Fleet Size / Uçak Sayısı:** {facts.fleet_size if facts.fleet_size is not None else "Not Specified / Belirtilmemiş"}
- **Modification Type / Türü:** {facts.modification_type or "Not Specified / Belirtilmemiş"}
- **Scope / Kapsam:** {facts.scope or "Not Specified / Belirtilmemiş"}

---
"""

    if gaps:
        summary += "\n## 2. Missing Information Checklist / Eksik Bilgiler\n"
        for gap in gaps:
            from src.gaps import get_field_description
            summary += f"- [ ] **{gap}** ({get_field_description(gap)})\n"
            
        if email_draft:
            summary += f"\n## 3. Draft Clarification Email / Eksik Bilgi Talep E-postası\n```text\n{email_draft}\n```\n"
    else:
        summary += "\n## 2. Itemized Cost Breakdown / Detaylı Fiyatlandırma\n"
        summary += "| Item / Kalem | Details / Açıklama | Cost / Ücret |\n"
        summary += "| --- | --- | --- |\n"
        summary += f"| **Base Labor Cost / Temel İşçilik** | Engineering manhours | ${quote['base_labor_cost']:,.2f} |\n"
        summary += f"| **Customer Margin / Kâr Marjı** | {quote['margin_applied']*100:.1f}% applied | ${quote['margin_amount']:,.2f} |\n"
        summary += f"| **Contingency / Beklenmedik Durum Payı** | 5.0% base labor | ${quote['contingency']:,.2f} |\n"
        summary += f"| **Testing & Certification / Sertifikasyon** | Fixed certification fee | ${quote['testing_fee']:,.2f} |\n"
        summary += f"| **Material Allowance / Malzeme Payı** | Max(1, Fleet) × $500 | ${quote['material_allowance']:,.2f} |\n"
        summary += "| --- | --- | --- |\n"
        summary += f"| **TOTAL QUOTE / TOPLAM TEKLİF** | **Net Price** | **${quote['total_cost']:,.2f}** |\n"
        
    summary += "\n---\n*Report generated automatically by TEKLİF-Sim Proposal Assistant.*"
    return summary
