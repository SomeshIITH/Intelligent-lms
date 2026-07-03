from typing import List, Dict, Any
from loguru import logger
from agents.orchestrator import agent_orchestrator
from services.quiz_service import quiz_service
from schemas.analytics import AnalyticsResponse, AnalyticsDataPayload


class AnalyticsService:
    """
    Coordinates student performance analysis workflows within the service tier.
    Extracts raw historical telemetry trails from storage and processes them through
    the multi-agent framework to build a contextual student profile.
    """

    def __init__(self) -> None:
        logger.info("[ANALYTICS_SERVICE] Initializing central learning analytics aggregator.")

    async def compile_student_analytics(self) -> AnalyticsResponse:
        """
        Retrieves quiz history logs and triggers the agent framework to calculate
        mastery profiles, highlight weak areas, and generate remediation strategies.
        """
        logger.info("[ANALYTICS_SERVICE] Request received to build student analytics profile.")

        # 1. Extract raw transactional quiz history directly from the service layer
        raw_history: List[Dict[str, Any]] = quiz_service._load_raw_history()
        logger.debug(f"[ANALYTICS_SERVICE] Retrieved {len(raw_history)} historical evaluation logs.")

        # 2. Return a clean initialization payload if no quizzes have been taken yet
        if not raw_history:
            logger.info("[ANALYTICS_SERVICE] History log is empty. Returning baseline analytics payload.")
            return AnalyticsResponse(
                success=True,
                message="No evaluation tracking data available yet. Please complete a quiz to populate metrics.",
                data=AnalyticsDataPayload(
                    overall_score=0.0,
                    quizzes_taken=0,
                    topic_breakdown=[],
                    strengths=[],
                    weaknesses=[],
                    remediation_plan="Your knowledge profile will update here once you complete your first quiz."
                ),
                metadata={"analytics_execution": "empty_baseline"}
            )

        # 3. Route history logs down to the multi-agent layers for analysis
        logger.info("[ANALYTICS_SERVICE] Dispatching history data to the multi-agent orchestrator.")
        analytics_response: AnalyticsResponse = await agent_orchestrator.route_analytics_calculation(raw_history)
        
        logger.info("[ANALYTICS_SERVICE] Student profiling complete. Analytics metrics returned.")
        return analytics_response


# Instantiate service singleton for unified api exposure
analytics_service = AnalyticsService()