import os
import re
import ast
import subprocess
from src.pricing import calculate_quote

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_pricing_determinism():
    """
    Ensure the pricing engine is 100% deterministic (same inputs yield the exact same outputs).
    Runs the engine 50 times in a loop and compares results.
    """
    manhours = {
        "cabin_design_engineer": 100,
        "structural_engineer": 50,
        "avionics_design_engineer": 25,
        "certification_engineer": 15,
        "project_manager": 10
    }
    
    first_result = calculate_quote(manhours, "partner", "competitive", fleet_size=3)
    
    for _ in range(49):
        result = calculate_quote(manhours, "partner", "competitive", fleet_size=3)
        assert result == first_result

def test_pricing_no_forbidden_imports():
    """
    Analyze the Abstract Syntax Tree (AST) of src/pricing.py to guarantee no LLM,
    randomization, or networking libraries are imported.
    """
    pricing_path = os.path.join(PROJECT_ROOT, "src", "pricing.py")
    assert os.path.exists(pricing_path), "src/pricing.py must exist"
    
    with open(pricing_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=pricing_path)

    forbidden_imports = {
        "google", "google.generativeai", "google.genai", "genai", 
        "random", "requests", "httpx", "urllib", "uuid"
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                assert root_module not in forbidden_imports, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            root_module = node.module.split(".")[0] if node.module else ""
            assert root_module not in forbidden_imports, f"Forbidden import found: from {node.module} import ..."

def test_gitignore_covers_env():
    """
    Ensure that .env and .venv are ignored in the .gitignore file.
    """
    gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
    assert os.path.exists(gitignore_path), ".gitignore must exist"
    
    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert ".env" in content, ".env must be ignored in gitignore"
    assert ".venv" in content, ".venv must be ignored in gitignore"

def test_clean_room_blacklist():
    """
    Runs the automated scan_compliance.py script to ensure no proprietary terms
    are hardcoded or leaked in the codebase.
    """
    compliance_script = os.path.join(
        PROJECT_ROOT, ".agents", "skills", "clean-room-compliance", "scripts", "scan_compliance.py"
    )
    assert os.path.exists(compliance_script), "scan_compliance.py script must exist"
    
    # Run python script and assert exit code is 0 (Success)
    python_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"  # Fallback
        
    result = subprocess.run(
        [python_exe, compliance_script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    
    assert result.returncode == 0, f"Clean-room compliance scan failed:\n{result.stdout}\n{result.stderr}"
