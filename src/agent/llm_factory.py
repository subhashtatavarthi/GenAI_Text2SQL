from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings
import logging

logger = logging.getLogger(__name__)

def get_llm(provider: str):
    """
    Returns the ChatModel based on the provider string.
    Supported: 'openai', 'gemini'
    """
    if provider.lower() == "gemini":
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in configuration.")
        logger.info("Using Google Gemini LLM")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", # Validated available model
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
            convert_system_message_to_human=True # Often needed for some Gemini versions
        )
    elif provider.lower() == "openai":
        logger.info("Using OpenAI GPT-3.5 LLM")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            model="gpt-3.5-turbo",
            temperature=0
        )
    else:
        # Default fallback or error
        logger.warning(f"Unknown provider '{provider}', falling back to OpenAI.")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            model="gpt-3.5-turbo",
            temperature=0
        )
