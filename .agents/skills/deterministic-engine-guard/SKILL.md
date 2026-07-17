---
name: deterministic-engine-guard
description: Enforces strict coding discipline on the pricing engine. Crucial to guarantee no LLM calls, random numbers, or network operations are included in src/pricing.py.
---

# Deterministic Engine Guard

This skill ensures that the pricing engine (`src/pricing.py`) is written as a deterministic, pure-Python module that is easily testable and contains no fuzzy logic.

## Strict Restrictions for `src/pricing.py`

### 1. Prohibited Imports
Do NOT import any of the following libraries or modules inside the pricing code:
- `google.generativeai` or `google-genai` (No LLM calls)
- `random` (No random pricing, margins, or fees)
- `datetime` (specifically `datetime.now()`, which makes outputs time-dependent)
- `uuid` (No dynamic ID generation that changes per execution)
- `requests`, `urllib`, `httpx` (No network calls)

### 2. File-Based Configuration
- The rates must be loaded from `data/rate_card.csv`.
- The customer classes and margin bands must be loaded from `data/customer_classes.json`.
- The strategy must be mapped using keyword-matching logic from a string input.

### 3. Test-Driven Development (TDD)
- The specification (`docs/pricing_spec.md`) and the unit tests (`tests/test_pricing.py`) MUST be written and reviewed BEFORE modifying the core pricing implementation.
- All pricing engine changes must be verified to keep the test suite completely green.
- Given the same inputs (manhours, customer class, strategy string), the pricing engine must always return the exact same output.
