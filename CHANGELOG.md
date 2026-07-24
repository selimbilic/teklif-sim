# Changelog

All notable changes to the **TEKLİF-Sim** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
