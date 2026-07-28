from typing import Dict, List, Any
from src.extract import EmailExtraction
from src.estimation import resolve_cert_basis, classify_part21_change

def generate_proposal_summary(
    facts: EmailExtraction, 
    gaps: List[str], 
    quote: Dict[str, float] = None,
    email_draft: str = ""
) -> str:
    """
    Generates a clean one-page proposal summary markdown report with
    EASA Part 21 certification details and v2.0.0 itemized cost breakdown.
    """
    status = "⚠️ PENDING INFORMATION (EKSİK BİLGİ TALEBİ)" if gaps else "✅ READY FOR REVIEW (TEKLİF HAZIR)"
    cert_basis = getattr(facts, "cert_basis", None) or resolve_cert_basis(facts.aircraft_type)
    part21_info = classify_part21_change(facts.scope, facts.modification_type or "", facts.complexity or "standard")
    dal = getattr(facts, "dal_level", None) or "DAL D"

    summary = f"""# PROPOSAL SUMMARY / TEKLİF ÖZETİ
**Status / Durum:** {status}

---

## 1. Customer & Request Facts / Müşteri ve Talep Bilgileri
- **Customer Airline / Havayolu:** {facts.customer_name or "Not Specified / Belirtilmemiş"}
- **Customer Class / Sınıfı:** {facts.customer_class or "Not Specified / Belirtilmemiş"}
- **Aircraft Type / Uçak Modeli:** {facts.aircraft_type or "Not Specified / Belirtilmemiş"} (`{cert_basis}` Fixed-Wing Basis)
- **Fleet Size / Uçak Sayısı:** {facts.fleet_size if facts.fleet_size is not None else "Not Specified / Belirtilmemiş"}
- **Modification Type / Türü:** {facts.modification_type or "Not Specified / Belirtilmemiş"}
- **Design Assurance Level (ARP4761):** `{dal}`
- **Scope / Kapsam:** {facts.scope or "Not Specified / Belirtilmemiş"}

---

## 2. EASA Part 21 & Certification Package / Sertifikasyon Esası
- **Certification Specification:** `{cert_basis}` (Fixed-Wing Aeroplanes)
- **EASA Part 21.A.91 Classification:** **{part21_info['clause']}**
- **Independent CVE Verification (21.A.239):** `{part21_info['cve_hours']} hours` allocated
- **ICA Preparation (CS-25.1529):** `{part21_info.get('ica_hours', 0)} hours` allocated
- **DOA Mandatory Document Package Deliverables:**
  - [x] Certification Programme (CP) & Means of Compliance (MoC)
  - [x] Service Bulletin (SB) / Modification Instruction (MI)
  - [x] Structural / Electrical Substantiation Reports
  - [x] Safety Assessment Report (FHA / PSSA / SSA per ARP4761)
  - [x] Instructions for Continued Airworthiness (ICA) / AMM Supplement
  - [x] EWIS Compliance Assessment (CS 25.1707 / AMC 20-21)
  - [x] Independent Compliance Verification (CVE Statement)

---
"""

    if gaps:
        summary += "\n## 3. Missing Information Checklist / Eksik Bilgiler\n"
        for gap in gaps:
            from src.gaps import get_field_description
            summary += f"- [ ] **{gap}** ({get_field_description(gap)})\n"
            
        if email_draft:
            summary += f"\n## 4. Draft Clarification Email / Eksik Bilgi Talep E-postası\n```text\n{email_draft}\n```\n"
    else:
        summary += "\n## 3. Itemized Cost Breakdown / Detaylı Fiyatlandırma\n"
        summary += "| Item / Kalem | Details / Açıklama | Cost / Ücret |\n"
        summary += "| --- | --- | --- |\n"
        
        base_labor = quote.get('base_labor_cost', 0)
        urgency_mult = quote.get('urgency_multiplier', 1.0)
        base_labor_adj = quote.get('base_labor_cost_adjusted', base_labor)
        
        summary += f"| **Base Labor Cost / Temel İşçilik** | Engineering manhours (incl. CVE, ICA & EWIS) | ${base_labor:,.2f} |\n"
        
        if urgency_mult > 1.0:
            urgency_cost = round(base_labor_adj - base_labor, 2)
            summary += f"| **Urgency Surcharge / Acil Durum Payı** | AOG/Rush {urgency_mult:.0%} surcharge | ${urgency_cost:,.2f} |\n"
        
        summary += f"| **Customer Margin / Kâr Marjı** | {quote['margin_applied']*100:.1f}% applied | ${quote['margin_amount']:,.2f} |\n"
        
        contingency_rate = quote.get('contingency_rate', 0.05)
        summary += f"| **Contingency / Beklenmedik Durum Payı** | {contingency_rate*100:.0f}% risk-based | ${quote['contingency']:,.2f} |\n"
        summary += f"| **Testing & Certification / Sertifikasyon** | Mod-type specific fee | ${quote['testing_fee']:,.2f} |\n"
        summary += f"| **Material Allowance / Malzeme Payı** | Per-aircraft kit allowance | ${quote['material_allowance']:,.2f} |\n"
        
        vol_disc = quote.get('volume_discount', 0)
        if vol_disc > 0:
            vol_rate = quote.get('volume_discount_rate', 0)
            summary += f"| **Volume Discount / Filo İndirimi** | {vol_rate*100:.0f}% fleet discount | -${vol_disc:,.2f} |\n"
        
        summary += "| --- | --- | --- |\n"
        summary += f"| **TOTAL QUOTE / TOPLAM TEKLİF** | **Net Price** | **${quote['total_cost']:,.2f}** |\n"
        
    summary += "\n---\n*Report generated automatically by TEKLİF-Sim Proposal Assistant (v2.0.0).* "
    return summary
