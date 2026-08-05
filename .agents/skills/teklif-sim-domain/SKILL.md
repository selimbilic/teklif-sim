---
name: teklif-sim-domain
description: Provides core domain knowledge about aircraft design modifications (DOA, cabins, structures, avionics, certification), manhour estimations, and proposal generation workflows. Use this skill when dealing with aircraft modification types, customer requests, or proposal drafting.
---

# Aircraft Modification Proposal Domain Guide

This skill provides domain context and instructions for analyzing modification requests and preparing engineering quotes as an EASA/FAA Design Organisation (DOA).

## 1. Domain Terminology

- **DOA (Design Organisation Approval):** The approval granted by the aviation authority (like EASA or FAA) allowing a company to design modifications and repairs on aircraft.
- **Modification Types:**
  - **Cabin Interior:** Refitting seats, carpets, galleys, lavatories, or emergency equipment.
  - **Structural:** Modifying the fuselage (e.g., cargo door cut, Wi-Fi antenna mount reinforcement) or repairing structural damage (e.g., tail strike).
  - **Avionics:** Upgrading flight deck displays, communication systems (Wi-Fi), or navigation systems (ADS-B Out).
- **Engineering Disciplines (Roles):**
  - `cabin_design_engineer`: Designs LOPA (Layout of Passenger Accommodations), seat layouts, emergency equipment.
  - `structural_engineer`: Performs load analysis, fuselage modifications, stress verification.
  - `avionics_design_engineer`: Works on electrical routing, avionics integration, antennas.
  - `certification_engineer`: Drafts Service Bulletins (SB), works with authority approvals, prepares compliance documents.
  - `project_manager`: Coordinates tasks, schedule, and client contact.

## 2. Proposal Engineering Workflow

When a client email arrives:
1. **Analyze Facts:** Identify the aircraft model, fleet size, scope of work, customer, and any estimated manhours.
2. **Gap Detection:** Determine what is missing. A valid quote requires:
   - Aircraft type (e.g., A320, B737-800)
   - Fleet size / quantity of aircraft
   - Specific modification scope
   - Estimated engineering hours per role (or enough detail to estimate them)
3. **Clarification:** If any required fields are missing, generate a polite clarification draft.
4. **Fiyatlandırma (Pricing):** Cost the labor using the rate card, apply the customer class margin band, and add fixed fees.

## 3. Think Before Coding Principle

When acting within this domain:
- **Never guess or assume client details:** If the aircraft fleet size or model is vague (e.g. "our fleet"), flag it as a gap.
- **Push back on ambiguity:** If a request is completely irrelevant (e.g., catering), label it invalid instead of forcing a proposal.

## 4. Scope & Certification Constraints

- **Supported Certification Standards:** Fixed-wing aircraft certifications ONLY (`CS-25` Large Aeroplanes and `CS-23` Normal/Utility Aeroplanes).
- **Excluded Scope:** Helikopter / Rotorcraft certifications (`CS-27` / `CS-29`) are explicitly **EXCLUDED** from the project roadmap and estimation scope. We operate strictly with current fixed-wing CS standards.
