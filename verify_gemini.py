import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings

# Load env vars
load_dotenv()

async def verify_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment.")
        return

    print(f"✅ GOOGLE_API_KEY found: {api_key[:5]}...")

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0
        )
        print("Attempting to invoke Gemini...")
        response = await llm.ainvoke("Hello, simply say 'Gemini is working'")
        print(f"✅ Gemini Response: {response.content}")
    except Exception as e:
        print(f"❌ Failed to invoke Gemini: {e}")

if __name__ == "__main__":
    asyncio.run(verify_gemini())
