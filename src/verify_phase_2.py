import os
import sys
from src.extract import extract_facts
from src.gaps import check_gaps, get_field_description

def verify_all_emails():
    email_dir = "data/sample_emails"
    if not os.path.exists(email_dir):
        print(f"[-] Email directory {email_dir} does not exist.")
        return

    # List all email files
    files = sorted(os.listdir(email_dir))
    print(f"[*] Found {len(files)} sample emails. Starting verification...\n")

    for file_name in files:
        file_path = os.path.join(email_dir, file_name)
        print("="*60)
        print(f"[*] Processing: {file_name}")
        print("="*60)
        
        with open(file_path, "r", encoding="utf-8") as f:
            email_content = f.read()

        try:
            # 1. Extract facts
            facts = extract_facts(email_content)
            print(f"[+] Valid email: {facts.is_valid}")
            if not facts.is_valid:
                print("[-] This email was flagged as INVALID (spam or unrelated).")
                continue
                
            print(f"[+] Airline: {facts.customer_name} ({facts.customer_class})")
            print(f"[+] Aircraft: {facts.aircraft_type} (Fleet: {facts.fleet_size})")
            print(f"[+] Mod Type: {facts.modification_type}")
            print(f"[+] Scope: {facts.scope}")
            
            if facts.manhours:
                hours_dict = {k: v for k, v in facts.manhours.model_dump().items() if v is not None}
                print(f"[+] Manhours: {hours_dict}")
            else:
                print("[+] Manhours: None")

            # 2. Check gaps
            gaps = check_gaps(facts)
            if gaps:
                print(f"[!] GAPS DETECTED: {len(gaps)}")
                for gap in gaps:
                    print(f"    - {gap} ({get_field_description(gap)})")
            else:
                print("[+] No gaps detected! Ready to quote.")
                
        except Exception as e:
            print(f"[-] Failed to process {file_name}: {e}")
        
        print("\n")
        # Add 12-second sleep between requests to respect 5 RPM Gemini rate limit
        import time
        time.sleep(12)

if __name__ == "__main__":
    verify_all_emails()
