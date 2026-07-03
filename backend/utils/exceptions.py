from typing import Any, Dict, Optional


class AppBaseException(Exception):
    """
    Base exception class for all custom domain errors within the Intelligent LMS.
    Enables tracking of semantic error classifications and contextual details.
    """
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class FileUploadException(AppBaseException):
    """Raised when an error occurs during PDF parsing, validating, or filesystem storage."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class VectorStoreException(AppBaseException):
    """Raised when ChromaDB operations, embedding generation, or index purges fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)


class LLMException(AppBaseException):
    """Raised when the Gemini 2.5 Flash API encounters generation or authorization errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=502, details=details)


class AgentExecutionException(AppBaseException):
    """Raised when an orchestration agent fails to parse schema mappings or evaluate tools."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=422, details=details)


class DatabaseEmptyException(AppBaseException):
    """Raised when a user queries the system before any valid source document has been uploaded."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=404, details=details)