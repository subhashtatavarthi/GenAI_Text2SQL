import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# Load env vars
load_dotenv()

class TestSchema(BaseModel):
    reasoning: str = Field(description="Why you chose this answer")
    answer: str = Field(description="The actual answer")

async def verify_structured_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found.")
        return

    try:
        print("Initializing Gemini...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0
        )
        
        print("Testing .with_structured_output()...")
        structured_llm = llm.with_structured_output(TestSchema)
        
        result = await structured_llm.ainvoke("Why is the sky blue?")
        print(f"✅ Structured Result: {result}")
        
    except Exception as e:
        print(f"❌ Failed structured output: {e}")

if __name__ == "__main__":
    asyncio.run(verify_structured_gemini())
