import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings

def test_gemini():
    print("--- Testing Gemini Connection ---")
    key = settings.GOOGLE_API_KEY
    if not key:
        print("❌ GOOGLE_API_KEY is missing via settings.")
        # Try raw env
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("GOOGLE_API_KEY")
        print(f"Raw env check: {key[:5]}..." if key else "Missing in .env too")
    else:
        print(f"Key found: {key[:5]}...")

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=key,
            temperature=0
        )
        print("Invoking model...")
        result = llm.invoke("Hello, are you working?")
        print(f"✅ Response: {result.content}")
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")

if __name__ == "__main__":
    test_gemini()
