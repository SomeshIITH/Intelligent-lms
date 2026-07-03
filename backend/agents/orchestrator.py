from typing import List, Dict, Any
from loguru import logger
from agents.tutor_agent import tutor_agent
from agents.assessor_agent import assessor_agent
from agents.curriculum_agent import curriculum_agent
from agents.analytics_agent import analytics_agent
from schemas.chat import ChatMessageRequest, ChatResponse
from schemas.quiz import QuizResponse
from schemas.roadmap import RoadmapResponse
from schemas.analytics import AnalyticsResponse


class AgentOrchestrator:
    """
    Central facade and orchestration gateway for the Intelligent LMS Agent Layer.
    Dispatches inbound application requests to their respective specialized execution agents,
    providing structured context verification, system metrics, and uniform tracing.
    """

    def __init__(self) -> None:
        logger.info("[ORCHESTRATOR] Initializing multi-agent intelligence routing workspace.")

    async def route_chat_query(self, request: ChatMessageRequest) -> ChatResponse:
        """
        Routes incoming conversation pipelines directly through the interactive RAG Tutor Agent.
        """
        logger.info(f"[ORCHESTRATOR] Intercepted chat request (History length: {len(request.history or [])})")
        try:
            response: ChatResponse = await tutor_agent.execute(request)
            logger.info("[ORCHESTRATOR] Conversational response packet safely returned from Tutor Agent.")
            return response
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Execution failure inside Tutor Agent branch: {str(e)}")
            raise e

    async def route_quiz_generation(self) -> QuizResponse:
        """
        Triggers the Assessor Agent to analyze current knowledge frames and build 5 MCQs.
        """
        logger.info("[ORCHESTRATOR] Intercepted request for automated evaluation quiz generation.")
        try:
            response: QuizResponse = await assessor_agent.execute_generation()
            logger.info("[ORCHESTRATOR] Structured quiz payload safely returned from Assessor Agent.")
            return response
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Generation failure inside Assessor Agent branch: {str(e)}")
            raise e

    async def route_roadmap_generation(self) -> RoadmapResponse:
        """
        Triggers the Curriculum Agent to formulate a chronological learning path timeline.
        """
        logger.info("[ORCHESTRATOR] Intercepted request for structured study roadmap synthesis.")
        try:
            response: RoadmapResponse = await curriculum_agent.execute_generation()
            logger.info("[ORCHESTRATOR] Chronological milestone track safely returned from Curriculum Agent.")
            return response
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Layout failure inside Curriculum Agent branch: {str(e)}")
            raise e

    async def route_analytics_calculation(self, raw_history: List[Dict[str, Any]]) -> AnalyticsResponse:
        """
        Passes structural score telemetry trends to the Analytics Agent for remediation planning.
        """
        logger.info(f"[ORCHESTRATOR] Intercepted request for profiling telemetry (Attempts: {len(raw_history)}).")
        try:
            response: AnalyticsResponse = await analytics_agent.execute_analysis(raw_history)
            logger.info("[ORCHESTRATOR] Student telemetry profile safely returned from Analytics Agent.")
            return response
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Analysis failure inside Analytics Agent branch: {str(e)}")
            raise e


# Instantiate orchestration hub globally for unified service consumption
agent_orchestrator = AgentOrchestrator()