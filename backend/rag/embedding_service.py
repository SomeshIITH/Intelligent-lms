from loguru import logger
from langchain_huggingface import HuggingFaceEmbeddings
from utils.exceptions import VectorStoreException


class EmbeddingService:
    """
    Manages vectorization processing engines within the Intelligent LMS.
    Initializes a localized instance of a SentenceTransformer embedding architecture
    wrapped by langchain-huggingface, providing consistent semantic vector formats.
    """

    def __init__(self) -> None:
        logger.info("[EMBEDDING_SERVICE] Initializing local semantic embedding extraction subsystem.")
        self._model_name = "sentence-transformers/all-mpnet-base-v2"
        self._embeddings = self._initialize_embedding_client()

    def _initialize_embedding_client(self) -> HuggingFaceEmbeddings:
        """
        Builds the underlying HuggingFace local embedding client pipeline safely.
        Configures processing context directly onto host hardware structures.
        """
        logger.info(f"[EMBEDDING_SERVICE] Attempting download or local cache activation of model: '{self._model_name}'")
        try:
            # Set explicit device properties and normalization arguments
            model_kwargs = {"device": "cpu"}
            encode_kwargs = {"normalize_embeddings": True}
            
            client = HuggingFaceEmbeddings(
                model_name=self._model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            logger.info(f"[EMBEDDING_SERVICE] Model '{self._model_name}' verified and operational inside LangChain lifecycle.")
            return client
        except Exception as e:
            logger.exception(f"[EMBEDDING_SERVICE] [CRITICAL FAILURE] Fails safely loading local transformer model weights: {str(e)}")
            raise VectorStoreException(
                message="Failed to build local sentence transformer embedding extraction pipeline.",
                details={"target_model": self._model_name, "underlying_error": str(e)}
            )

    def get_client(self) -> HuggingFaceEmbeddings:
        """
        Exposes the pre-warmed HuggingFaceEmbeddings instance for direct vector operations.
        """
        logger.debug("[EMBEDDING_SERVICE] Supplying initialized HuggingFaceEmbeddings thread-safe client.")
        return self._embeddings


# Instantiate global singleton instance for unified layer injection across RAG flows
embedding_service = EmbeddingService()