#!/usr/bin/env python3
import os
import sys

# Define blacklisted terms (case-insensitive)
BLACKLIST = [
    "turkish technic",
    "turkish technıc",
    "thy",
    "türk hava yolları",
    "turk hava yollari"
]

# Paths to scan, relative to the project root (C:\Users\mseli\teklif-sim)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

# Directories/files to exclude from scanning
EXCLUDE_DIRS = [".git", ".venv", "__pycache__", "node_modules", ".agents"]
EXCLUDE_FILES = [".env"]

def scan_files():
    failures = 0
    print(f"Scanning directory: {PROJECT_ROOT} for clean-room compliance...")

    # Check gitignore presence
    gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
    if not os.path.exists(gitignore_path):
        print("[-] Missing .gitignore file!")
        failures += 1
    else:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
            if ".env" not in content:
                print("[-] .env file is not added to .gitignore!")
                failures += 1
            if ".venv" not in content:
                print("[-] .venv directory is not added to .gitignore!")
                failures += 1

    # Traverse directory
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file in EXCLUDE_FILES:
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        # 1. Check blacklist
                        line_lower = line.lower()
                        for term in BLACKLIST:
                            if term in line_lower:
                                # Ensure we don't flag the scan script itself or the skill document
                                if "scan_compliance.py" in file_path or "clean-room-compliance/SKILL.md" in file_path:
                                    continue
                                print(f"[-] Blacklist Violation in {file_path}:{line_num} -> Found '{term}'")
                                failures += 1

                        # 2. Check for hardcoded API keys
                        # Simple heuristics for Gemini API key (AIzaSy...)
                        if "aizasy" in line_lower:
                            print(f"[-] Potential Hardcoded API Key in {file_path}:{line_num}")
                            failures += 1
            except Exception as e:
                print(f"[!] Error reading {file_path}: {e}")

    if failures == 0:
        print("[+] Clean-room compliance check PASSED.")
        return True
    else:
        print(f"[-] Clean-room compliance check FAILED with {failures} violations.")
        return False

if __name__ == "__main__":
    success = scan_files()
    sys.exit(0 if success else 1)
