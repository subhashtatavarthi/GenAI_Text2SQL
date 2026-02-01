from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") 
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API Key found in .env")
    exit(1)

try:
    print("Connecting to OpenAI...")
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    response = llm.invoke("Hello, are you working?")
    print("\n✅ Success! Response from OpenAI:")
    print(response.content)
except Exception as e:
    print(f"\n❌ Error: {e}")
