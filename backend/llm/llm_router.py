import os
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings
from utils.exceptions import LLMException


class LLMRouter:
    """
    Central router for managing LLM instances within the Intelligent LMS.
    Ensures safe initialization, global verification of the Gemini API configuration,
    and exposes a uniform factory interface for returning production-ready model instances.
    """

    def __init__(self) -> None:
        logger.info("[LLM_ROUTER] Initializing LLMRouter service subsystem.")
        self._verify_api_key()

    def _verify_api_key(self) -> None:
        """
        Validates the existence of the Gemini API key.
        Explicitly injects it into the environment descriptor maps if required.
        """
        key = settings.GEMINI_API_KEY
        if not key or key == "your_gemini_api_key_here":
            logger.critical("[LLM_ROUTER] [CONFIGURATION ERROR] GEMINI_API_KEY is unset or set to placeholder value.")
            raise LLMException(
                message="Gemini API Key missing or invalid in configuration.",
                details={"config_state": "placeholder_or_empty"}
            )
        
        # Sync to environment variable explicitly to ensure LangChain native client handles pickup
        os.environ["GOOGLE_API_KEY"] = key
        logger.debug("[LLM_ROUTER] Gemini API key confirmed and mapped to environment variables.")

    def get_tutor_model(self, temperature: float = 0.3) -> ChatGoogleGenerativeAI:
        """
        Returns a configured instance of Gemini 2.5 Flash tailored for reasoning, 
        interactive conversations, and document tutoring workflows.
        """
        logger.info(f"[LLM_ROUTER] Initializing ChatGoogleGenerativeAI instance with temperature={temperature}")
        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=temperature,
                max_retries=3,
                timeout=30.0
            )
            logger.debug("[LLM_ROUTER] ChatGoogleGenerativeAI instance built successfully.")
            return model
        except Exception as e:
            logger.exception("[LLM_ROUTER] Failed to construct ChatGoogleGenerativeAI instance.")
            raise LLMException(
                message="Failed to initialize Google Generative AI model context.",
                details={"error": str(e)}
            )

    def get_structured_model(self, temperature: float = 0.1) -> ChatGoogleGenerativeAI:
        """
        Returns an instance optimized for extraction and structured JSON object compilation.
        Uses a lower temperature setting to maximize consistency and structural accuracy.
        """
        logger.info(f"[LLM_ROUTER] Initializing Structured ChatGoogleGenerativeAI instance with temperature={temperature}")
        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=temperature,
                max_retries=5, # Higher retry rate for strict data payloads
                timeout=45.0
            )
            logger.debug("[LLM_ROUTER] Structured ChatGoogleGenerativeAI instance built successfully.")
            return model
        except Exception as e:
            logger.exception("[LLM_ROUTER] Failed to construct Structured ChatGoogleGenerativeAI instance.")
            raise LLMException(
                message="Failed to initialize Structured Google Generative AI model context.",
                details={"error": str(e)}
            )


# Instantiate router globally for unified runtime access across layers
llm_router = LLMRouter()