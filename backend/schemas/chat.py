from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.common import BaseResponse


class ChatMessageRequest(BaseModel):
    """
    Validation schema for incoming conversation requests sent by the client.
    Captures the primary query alongside historical context for conversational continuity.
    """
    message: str = Field(
        ..., 
        min_length=1,
        description="The natural language question or instruction directed to the RAG AI Tutor."
    )
    history: Optional[List[str]] = Field(
        default_factory=list,
        description="Sequential list of previous alternating strings modeling conversation history."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "What are the core axioms discussed in chapter 2?",
                "history": [
                    "Hello, I am your AI tutor.",
                    "Hi, can you explain the main focus of this document?",
                    "This document focuses heavily on standard quantum computational foundations."
                ]
            }
        }
    }


class ChatCitation(BaseModel):
    """Represents a specific structural citation source extracted from the document to justify an answer."""
    page: int = Field(..., description="The physical page number within the uploaded source PDF (1-indexed).")
    content: str = Field(..., description="The raw textual snippet pulled out from this chunk boundary.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "page": 14,
                "content": "The secondary axiom dictates that state vectors must remain normalized within the Hilbert space."
            }
        }
    }


class ChatDataPayload(BaseModel):
    """The structured data container holding the complete textual answer and supporting facts."""
    answer: str = Field(..., description="The highly contextual Markdown-formatted text compiled by Gemini 2.5 Flash.")
    citations: List[ChatCitation] = Field(
        default_factory=list,
        description="Clean list of document chunks references leveraged to establish grounding truth."
    )


class ChatResponse(BaseResponse):
    """The fully enveloped server response layout matching conversational outputs."""
    data: ChatDataPayload = Field(..., description="The actual generated response data package.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "AI Tutor answer compiled successfully.",
                "timestamp": "2026-07-03T20:46:00.000Z",
                "data": {
                    "answer": "According to Chapter 2, the primary axioms rely heavily on state normalization...",
                    "citations": [
                        {
                            "page": 14,
                            "content": "The secondary axiom dictates that state vectors must remain normalized..."
                        }
                    ]
                },
                "metadata": {"tokens_processed": 435, "model": "gemini-2.5-flash"}
            }
        }
    }