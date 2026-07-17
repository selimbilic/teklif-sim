---
name: clean-room-compliance
description: Enforces clean-room engineering compliance. Crucial for detecting real-world company names, real rates, and API keys. Use this skill when modifying code, data files, or documentation.
---

# Clean-Room Engineering Compliance Guide

This skill ensures the project remains a clean-room codebase by keeping all data synthetic and excluding any real-world company details, credentials, or proprietary files.

## 1. Compliance Rules

### Blacklisted Names
Under no circumstances should the following names (or their variations) be stored in any text file, codebase, data file, or commit message:
- `Turkish Technic`
- `THY`
- `Türk Hava Yolları`
- Real Turkish Technic engineer/employee names
- Real hourly rate structures

### Whitelisted Synthetic Names
Always invent fake airline names for sample emails and customer classes, such as:
- `Anadolu Air`
- `Bosphorus Jet`
- `Gulf Alliance`
- `EuroLink`
- `Safari Air`

### API Key and Credentials Security
- The Gemini API Key must NEVER be hardcoded in any script or data file.
- The `.env` file containing the key must be listed in `.gitignore` and never committed.

## 2. Automated Compliance Checking

A helper script is provided at `C:\Users\mseli\teklif-sim\.agents\skills\clean-room-compliance\scripts\scan_compliance.py`.
Run this script to verify compliance across the workspace before creating any Git commit.
