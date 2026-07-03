from typing import List
from pydantic import BaseModel, Field, field_validator
from schemas.common import BaseResponse


class RoadmapMilestone(BaseModel):
    """
    Represents a specific chronological learning milestone within the study roadmap.
    Maps out discrete concepts, concrete objectives, and references to pages in the PDF.
    """
    id: int = Field(..., description="Unique incremental step identifier for the milestone (starting at 1).")
    title: str = Field(..., description="The definitive, conceptual name of this milestone phase.")
    description: str = Field(..., description="High-level description of what this phase covers and why it matters.")
    key_concepts: List[str] = Field(..., description="Explicit bullet list of core academic topics covered in this node.")
    estimated_hours: float = Field(..., description="The recommended time investment required to absorb this material.")
    source_pages: List[int] = Field(
        ..., 
        description="The physical, 1-indexed page references from the source PDF covering these specific concepts."
    )

    @field_validator("estimated_hours")
    @classmethod
    def validate_positive_hours(cls, v: float) -> float:
        """Ensures that the time estimate is always a realistic, non-negative value."""
        if v <= 0:
            raise ValueError(f"Estimated hours must be strictly greater than zero. Found: {v}")
        return v


class RoadmapDataPayload(BaseModel):
    """Holds the complete array of structured milestones forming the study roadmap."""
    title: str = Field(..., description="The overarching macro-title of the learning path.")
    target_audience: str = Field(..., description="Identified proficiency tier or audience scope inferred from the document.")
    milestones: List[RoadmapMilestone] = Field(..., description="The ordered chronological array of learning nodes.")

    @field_validator("milestones")
    @classmethod
    def validate_milestones_not_empty(cls, v: List[RoadmapMilestone]) -> List[RoadmapMilestone]:
        """Guarantees that a generated study path contains a valid sequence of actionable milestones."""
        if not v:
            raise ValueError("The generated study roadmap must contain at least one step milestone.")
        return v


class RoadmapResponse(BaseResponse):
    """Unified response envelope wrapping the completed, structured study roadmap."""
    data: RoadmapDataPayload = Field(..., description="The actual core roadmap architecture package.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Chronological study roadmap synthesized successfully from document context.",
                "timestamp": "2026-07-03T20:48:00.000Z",
                "data": {
                    "title": "Mastering Quantum Foundations",
                    "target_audience": "Intermediate Undergraduate Physics Student",
                    "milestones": [
                        {
                            "id": 1,
                            "title": "Introduction to State Vectors",
                            "description": "Establish foundational math layers regarding Hilbert spaces and bracket notations.",
                            "key_concepts": ["Hilbert Spaces", "Bra-Ket Notation", "State Normalization"],
                            "estimated_hours": 3.5,
                            "source_pages": [1, 2, 3, 4]
                        }
                    ]
                },
                "metadata": {"total_estimated_hours": 18.5}
            }
        }
    }