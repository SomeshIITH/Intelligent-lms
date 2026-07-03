from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """
    Unified standard API response envelope across the Intelligent LMS ecosystem.
    Guarantees consistent payload parsing interfaces for the React frontend client.
    """
    success: bool = Field(
        ..., 
        description="Flag indicating if the executed operation was completely successful"
    )
    message: str = Field(
        ..., 
        description="Human-readable informational summary message outlining operation results"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Standard UTC timestamp indicating exactly when the server response packet was finalized"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Optional unstructured context dictionary storing operational diagnostic metrics"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Operation completed successfully.",
                "timestamp": "2026-07-03T20:45:00.000Z",
                "metadata": {"processing_time_ms": 142}
            }
        }
    }