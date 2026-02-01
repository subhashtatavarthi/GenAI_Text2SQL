from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings
import logging

logger = logging.getLogger(__name__)

def get_llm(provider: str, model_name: str = None):
    """
    Returns the ChatModel based on the provider string.
    Supported: 'openai', 'gemini'
    """
    if provider.lower() == "gemini":
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in configuration.")
        
        model = model_name or "gemini-2.5-flash"
        logger.info(f"Using Google Gemini LLM: {model}")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
            convert_system_message_to_human=True # Often needed for some Gemini versions
        )
    elif provider.lower() == "openai":
        model = model_name or "gpt-3.5-turbo"
        logger.info(f"Using OpenAI LLM: {model}")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            model=model,
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
