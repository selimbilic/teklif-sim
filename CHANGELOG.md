# Changelog

All notable changes to the **TEKLİF-Sim** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-08-05

### Added & Enhanced (%100 Free Enterprise Release)
- **Multimodal Document Upload & Parsing (`src/parser.py`):** Added UI drag-and-drop file ingestion supporting PDF, Excel, Word, and Text documents via `pdfplumber`, `pypdf`, `python-docx`, and `openpyxl`.
- **Local PII & Privacy Anonymization (`src/privacy.py`):** Integrated Microsoft Presidio and regex sanitization layer to scrub personal and airline sensitive data locally on CPU before sending payloads to Gemini Pro.
- **Gemini Pro Multimodal Engine (`src/extract.py`):** Enhanced extraction with Gemini Pro model support and 1M-2M token context ingestion.
- **Free FX Currency Engine (`src/forex.py`):** Integrated official European Central Bank (ECB) and TCMB public XML feeds supporting live USD, EUR, GBP, and TRY conversion with zero API fees.
- **Relational Persistence Layer (`src/database.py`):** Built SQLAlchemy ORM database layer (SQLite / PostgreSQL) to automatically save proposals and enable CRM history search.
- **FastAPI Enterprise REST API (`src/api.py`):** Exposed `/health`, `/api/v1/extract`, `/api/v1/quote`, `/api/v1/simulate`, `/api/v1/export/pdf`, `/api/v1/export/docx`, and `/api/v1/proposals` endpoints for SAP/ERP & CRM integration.
- **Monte-Carlo Risk Simulation Engine (`src/simulation.py`):** Implemented 1,000-run Monte-Carlo simulation calculating P10 (Optimistic), P50 (Expected), and P90 (Conservative) confidence intervals.
- **Corporate PDF & Word Exporter (`src/export.py`):** Built ReportLab PDF and python-docx Word proposal document generator in official EASA Part 21 format.
- **Expanded Test Suite (`tests/test_v300_*.py`):** Added 16 new unit and integration tests bringing test suite to **68/68 passing**.

---

## [2.1.0] - 2026-08-03

### Added & Enhanced
- **YAML Configuration Loader (`config/settings.yaml` & `src/config.py`):** Externalized baseline pricing rules, rate cards, and complexity weights into YAML config.
- **GitHub Actions CI/CD Pipeline (`.github/workflows/ci.yml`):** Automated test workflow testing Python 3.10 through 3.13.
- **Dependency Locking (`requirements-lock.txt`):** Pinned production dependency versions for repeatable deployment.
- **Centralized Structured Logging (`src/logger.py`):** Added logging to console and `logs/teklif_sim.log` file.
- **Prompt Injection & Semantic Bounds Protection (`src/extract.py`):** Added regex marker filtering against prompt overrides and semantic caps on fleet size (500 max) and role manhours (10,000h max).
- **Sliding Window API Rate Limiter (`src/rate_limiter.py`):** Implemented token bucket rate limiter preventing Gemini API 429 quota exhaustion.
- **Parametric EWIS Aircraft Complexity Model (`src/estimation.py`):** Scaled EWIS wiring hours by aircraft body category (Widebody=1.4x, Narrowbody=1.0x, Regional=0.7x).
- **Expanded Test Suite (`tests/test_v210_features.py`):** Added 6 unit tests bringing total test count to **52/52 passing**.

---

## [2.0.1] - 2026-07-28

### Fixed & Security
- **HTML Injection / XSS Protection (`src/app.py`):** Added `html.escape()` sanitization (`safe_html`) for all LLM-extracted metadata rendered inside Streamlit `unsafe_allow_html=True` blocks.
- **Privacy & Data Security Disclaimer (`README.md` & `src/app.py`):** Added explicit privacy warning banners regarding the use of public LLM APIs (Gemini 3.1 Flash Lite) prohibiting real customer data or PII/GDPR sensitive inputs.
- **Unknown Engineering Role Validation (`src/pricing.py`):** Replaced silent `$0.00` pricing fallback (`rates.get(role, 0.0)`) with an explicit `ValueError` when an unrecognised role is passed in customer manhours.
- **Competitive Margin Clamping (`src/pricing.py`):** Clamped competitive strategy margin (`default_margin - 0.02`) to `min_margin` and enforced `[min_margin, max_margin]` band boundaries to prevent margin underflow.
- **Expanded Test Suite (`tests/test_pricing.py`):** Added unit tests covering unknown role validation errors and competitive margin clamping.

---

## [2.0.0] - 2026-07-28

### Breaking Changes
- **5-Tier DAL Multiplier System (`src/estimation.py`):** Replaced 2-tier DAL mapping (A/B=2.2, C/D=1.3) with DO-178C Annex A objective-proportional 5-tier system: DAL A=2.4x (71 obj, MC/DC+OCV), B=2.0x (69 obj), C=1.5x (62 obj), D=1.15x (26 obj), E=1.0x (0 obj). This changes all quote calculations involving DAL levels.
- **NRE/Recurring Fleet Scaling with Wright 80% Learning Curve (`src/estimation.py`):** Replaced linear fleet scaling (`1 + (n-1)*0.10`) with NRE/Recurring split model using Wright learning curve. NRE ratio varies by mod type (cabin=70%, cargo=55%). Large fleets now correctly reflect economies of scale.
- **CS-23 All-Role Reduction (`src/estimation.py`):** Expanded CS-23 discount from certification-only (0.85x) to all engineering roles with discipline-specific factors (cabin=0.55x, structural=0.60x, avionics=0.65x, certification=0.50x, PM=0.70x).
- **Mod-Type-Aware Testing Fees (`src/pricing.py`):** Replaced flat $1,500 testing fee with mod-type × complexity lookup table ranging from $800 (cabin minor) to $40,000 (cargo major).
- **Mod-Type-Aware Material Allowance (`src/pricing.py`):** Replaced flat $500/aircraft with mod-type × complexity per-aircraft table ranging from $200 (ELAMS minor) to $80,000 (cargo major).
- **Risk-Based Contingency (`src/pricing.py`):** Replaced fixed 5% contingency with risk-based rates: 4% (minor, no STC) to 15% (major STC), derived from AACE cost estimation standards.

### Added
- **Structural Engineer DAL Impact (`src/estimation.py`):** Structural engineering hours now receive 50% of the DAL multiplier effect, reflecting ARP4761 SSA impact on CS-25.571 damage tolerance analysis.
- **Mod-Type-Sensitive CVE Hours (`src/estimation.py`):** Part 21.A.239(d) CVE hours now scale by modification type (e.g., minor cabin=4h vs STC cargo=65h) instead of flat 6/15/25h.
- **ICA Preparation Hours (`src/estimation.py`):** Added CS-25.1529 / Appendix H ICA (Instructions for Continued Airworthiness) hours as separate certification line item, scaled by mod type and Part 21 classification.
- **EWIS Compliance Hours (`src/estimation.py`):** Added CS 25.1707-1733 / AMC 20-21 EWIS hours for avionics-intensive modifications (IFC, IFE, ISPS, ELAMS, cargo).
- **Expanded Scope Keywords (`src/estimation.py`):** Major scope keywords expanded from 11 to 28 entries; Minor keywords expanded from 6 to 17 entries (per EASA FAQ table of design change classification).
- **AOG/Rush Urgency Surcharge (`src/pricing.py`):** Added urgency multiplier on base labor: rush=1.25x, AOG=1.50x, independent of margin band.
- **Volume Discount (`src/pricing.py`):** Fleet 20+ gets 5% discount, Fleet 50+ gets 10% discount on subtotal.
- **Enhanced Dashboard (`src/app.py`):** Pricing tab now shows urgency surcharge, risk-based contingency with STC indicator, mod-type-specific fees, volume discount, and EWIS/ICA line items.
- **Enhanced Proposal Summary (`src/summarize.py`):** Proposal document reflects all new cost line items including urgency, volume discount, EWIS reference, and ICA hours.

---

## [1.3.0] - 2026-07-27

### Added & Fixed
- **ARP4761 DAL Safety Multiplier Pipeline Wiring (`src/pricing.py` & `src/app.py`):** Forwarded `dal_level` and `aircraft_type` parameters into `calculate_quote` and `estimate_manhours`, ensuring ARP4761 safety multipliers (DAL A/B: 2.2x, DAL C/D: 1.3x) directly adjust avionics and certification hours in quotes.
- **Flexible DAL Level String Parsing (`src/estimation.py`):** Enhanced `get_dal_multiplier` to support flexible string formats (`"C"`, `"Level B"`, `"DAL-A"`, `"A"`, `"D"`).
- **CS-23 vs CS-25 Certification Manhour Adjustment (`src/estimation.py`):** Applied a 0.85x certification factor for `CS-23` general aviation aeroplanes to reflect streamlined compliance documentation.
- **Data Integrity & Gap Rules (`src/gaps.py` & `src/draft_email.py`):** Flagged `fleet_size <= 0` as a missing information gap in `check_gaps`. Added Turkish translation for `"scope"` field in fallback clarification email template.
- **Expanded Unit Test Suite (`tests/`):** Expanded test suite to 30/30 passing tests covering flexible DAL parsing, CS-23 certification factors, zero fleet gap checks, and DAL quote pricing inclusion.

---

## [1.2.0] - 2026-07-27

### Added
- **Streamlit Action Button Execution Guard (`src/app.py`):** Explicitly wired `analyze_click` (`st.button`) to `st.session_state`. Gemini LLM fact extraction now triggers ONLY on explicit button action or sample email selection, preventing redundant LLM calls on widget interaction.
- **LLM Extraction Caching (`src/extract.py`):** Added `@st.cache_data` caching to `extract_facts_cached` to avoid duplicate Gemini API calls for identical email texts (0 cost, 0ms latency).
- **AST Unused Button Compliance Guard (`tests/test_compliance.py`):** Added `test_no_unused_streamlit_buttons()` AST test to ensure all `st.button` variables in `src/app.py` are properly checked in conditional statements.
- **Streamlit Headless AppTest Suite (`tests/test_ui.py`):** Added Streamlit AppTest integration suite verifying UI rendering and button trigger flow without browser automation.
- **Streamlit Skill Event Guarding Guidelines (`.agents/skills/developing-with-streamlit/SKILL.md`):** Documented explicit action button event guarding and LLM cost protection patterns.

---

## [1.1.0] - 2026-07-24

### Added
- **Fixed-Wing Certification Basis Engine (`CS-25` / `CS-23`):** Automatic classification of commercial transport aeroplanes (`CS-25`) vs small/general aviation aeroplanes (`CS-23`). Helicopters/rotorcraft excluded.
- **EASA Part 21.A.91 Change Classification Engine:** Automated classification into `Minor Change` vs `Major Change / STC` with mandatory independent CVE verification hours (`21.A.239(d)(2)`).
- **ARP4754A / ARP4761 / DO-178C Safety Assessment Multipliers:** Integrated DAL level (DAL A to E) safety multipliers for avionics and certification engineering hours.
- **Specialized Aviation Project Categories:** Added baseline man-hour estimation models for `IFE` (In-Flight Entertainment), `IFC` (Wi-Fi Connectivity), `ISPS` (In-Seat Power Supply), `ELAMS` (Electrical Load Analysis), `GAIN` (Galley Ovens/Heaters), `cabin_lopa`, and `structural_repair`.
- **DOA Deliverables Package Checklist (`src/summarize.py`):** Automatically appends EASA Part 21 certification document suite (CP, MoC, SB/MI, ICA, ELA, FHA/PSSA/SSA, CVE Statement) to generated proposal reports.
- **Streamlit Corporate UI Badge Update (`src/app.py`):** Displays `v1.1.0` header badge along with regulatory metadata, Part 21 classification status, and CVE verification hours.

---

## [1.0.0] - 2026-07-23

### Added
- **Deterministic Pricing Engine (`src/pricing.py`):** 100% Pure Python implementation for aircraft modification proposals (Base Labor + Margin + Contingency + Testing/Cert Fees + Fleet Material Allowances).
- **Gemini LLM Fact Extraction (`src/extract.py`):** Powered by `gemini-3.1-flash-lite` with structured `EmailExtraction` Pydantic models.
- **DOA Man-Hour Estimation Engine (`src/estimation.py`):** Baseline hours per discipline for Cabin, Structural, Avionics, and Cargo modifications with fleet scaling.
- **Clarification Draft Email Generator (`src/draft_email.py`):** Generates polite, structured emails requesting missing proposal details.
- **Proposal Summary Generator (`src/summarize.py`):** Executive markdown proposal output with detailed cost breakdowns.
- **Corporate Light Streamlit Dashboard (`src/app.py`):** Executive web interface with interactive email selection, manual overrides, and downloadable quotes.
- **Compliance & AST Test Suite (`tests/`):** 20/20 unit and AST compliance tests ensuring engine isolation, 50x determinism, clean-room compliance, and git hygiene.
- **Synthetic Data & Test Cases:** 20 synthetic email test cases, custom rate cards, and margin bands.
