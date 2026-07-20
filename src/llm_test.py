import os
import sys
from google import genai
from dotenv import load_dotenv

def test_connection():
    # Load .env file
    load_dotenv()
    
    # Check if API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY is not set in the environment or .env file.")
        return False
        
    print(f"[+] Found GEMINI_API_KEY (Length: {len(api_key)})")
    
    try:
        # Initialize Client. It will auto-detect GEMINI_API_KEY from environment variables
        client = genai.Client()
        
        print("[*] Sending request to Gemini (gemini-3.1-flash-lite)...")
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents='Respond in one short sentence to confirm your connection is successful.',
        )
        print(f"[+] Response from LLM: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
