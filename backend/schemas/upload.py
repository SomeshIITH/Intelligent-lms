from pydantic import BaseModel, Field
from schemas.common import BaseResponse


class UploadMetadata(BaseModel):
    """Encapsulates descriptive structured details regarding the successfully ingested PDF asset."""
    filename: str = Field(..., description="The original sanitized name of the uploaded PDF file.")
    file_size_bytes: int = Field(..., description="Total size footprint of the committed document in bytes.")
    chunk_count: int = Field(..., description="The total number of textual segments extracted and indexed into ChromaDB.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "quantum_mechanics_lecture_1.pdf",
                "file_size_bytes": 1048576,
                "chunk_count": 42
            }
        }
    }


class UploadResponse(BaseResponse):
    """Explicit response payload returned upon a successful knowledge-base replacement operation."""
    data: UploadMetadata = Field(..., description="The precise structural metadata of the single newly active knowledge source.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Knowledge base completely refreshed. Previous knowledge structures dropped cleanly.",
                "timestamp": "2026-07-03T20:45:00.000Z",
                "data": {
                    "filename": "quantum_mechanics_lecture_1.pdf",
                    "file_size_bytes": 1048576,
                    "chunk_count": 42
                },
                "metadata": {"execution_phase": "ingest_complete"}
            }
        }
    }