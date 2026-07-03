from typing import List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from schemas.common import BaseResponse


class TopicMastery(BaseModel):
    """Captures quantified evaluation metrics regarding a user's performance on a specific sub-topic."""
    topic_name: str = Field(..., description="The explicit name of the core module or chapter topic evaluated.")
    score_percentage: float = Field(..., description="Calculated proficiency rating mapped from 0.0 to 100.0.")
    question_count: int = Field(..., description="Total number of assessment vectors processed under this topic label.")

    @field_validator("score_percentage")
    @classmethod
    def validate_percentage_bounds(cls, v: float) -> float:
        """Validates that a mastery rating score exists within acceptable percentage thresholds."""
        if v < 0.0 or v > 100.0:
            raise ValueError(f"Score percentage must exist strictly between 0.0 and 100.0. Found: {v}")
        return v


class AnalyticsDataPayload(BaseModel):
    """The structured data container holding global metrics, topical trends, and actionable intervention insights."""
    overall_score: float = Field(..., description="The micro-aggregated average score achieved across all quiz instances.")
    quizzes_taken: int = Field(..., description="Total cumulative evaluation runs completed by the active student entity.")
    topic_breakdown: List[TopicMastery] = Field(
        default_factory=list, 
        description="Granular array containing individual module structural mastery vectors."
    )
    strengths: List[str] = Field(
        default_factory=list, 
        description="High-proficiency topics identified where the user demonstrated advanced retention."
    )
    weaknesses: List[str] = Field(
        default_factory=list, 
        description="Critical core gaps or performance vulnerabilities flagged for urgent textbook review."
    )
    remediation_plan: str = Field(
        ..., 
        description="Detailed Markdown narrative mapping tailored learning interventions back to explicit document source pages."
    )

    @field_validator("overall_score")
    @classmethod
    def validate_global_percentage_bounds(cls, v: float) -> float:
        """Validates that the overall score metric maps legally on a standard 100% scale."""
        if v < 0.0 or v > 100.0:
            raise ValueError(f"Overall score must map strictly between 0.0 and 100.0. Found: {v}")
        return v


class AnalyticsResponse(BaseResponse):
    """The fully enveloped server response layout matching calculated analytics pipelines."""
    data: AnalyticsDataPayload = Field(..., description="The actual compiled telemetry analytics payload package.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Student learning analytics profiling engine executed successfully.",
                "timestamp": "2026-07-03T20:49:00.000Z",
                "data": {
                    "overall_score": 74.5,
                    "quizzes_taken": 4,
                    "topic_breakdown": [
                        {
                            "topic_name": "State Normalization Axioms",
                            "score_percentage": 90.0,
                            "question_count": 10
                        },
                        {
                            "topic_name": "Hilbert Space Operators",
                            "score_percentage": 59.0,
                            "question_count": 10
                        }
                    ],
                    "strengths": ["State Normalization Axioms", "Bra-Ket Basic Notation"],
                    "weaknesses": ["Hilbert Space Operators"],
                    "remediation_plan": "The student shows excellent recall on basic notation, but struggles significantly with linear operators. **Action Item:** Re-read Chapter 2, specifically focusing on the mathematical proofs detailed on pages 14 through 19."
                },
                "metadata": {"analytics_engine_version": "2.1.0"}
            }
        }
    }