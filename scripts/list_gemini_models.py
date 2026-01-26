import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

import google.generativeai as genai
from src.config import settings

def list_models():
    print("--- Listing Available Gemini Models ---")
    key = settings.GOOGLE_API_KEY
    if not key:
        print("❌ GOOGLE_API_KEY is missing.")
        return

    try:
        genai.configure(api_key=key)
        print(f"Key configured: {key[:5]}...")
        
        print("Fetching models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
    except Exception as e:
        print(f"❌ Error Listing Models: {e}")

if __name__ == "__main__":
    list_models()
