import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

async def test_raw():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("No API Key")
        return

    print(f"Key: {api_key[:5]}...")
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', contents='Unicorn'
        )
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_raw())
