from fastapi import APIRouter, status, Body
from loguru import logger
from schemas.chat import ChatMessageRequest, ChatResponse
from schemas.quiz import QuizResponse
from schemas.roadmap import RoadmapResponse
from schemas.analytics import AnalyticsResponse
from agents.orchestrator import agent_orchestrator
from services.quiz_service import quiz_service
from services.analytics_service import analytics_service

router = APIRouter(tags=["Intelligent LMS Agent Operations"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit query to RAG AI Tutor",
    description="Queries the vector knowledge base using the multi-agent conversational tutoring layout.",
)
async def chat_with_tutor(
    request: ChatMessageRequest = Body(..., description="The student query and trailing chat history array")
) -> ChatResponse:
    """
    Passes conversational dialogue requests down into the multi-agent orchestrator.
    """
    logger.info(f"[CHAT_API] Intercepted tutoring transaction query: '{request.message[:40]}...'")
    response: ChatResponse = await agent_orchestrator.route_chat_query(request)
    return response


@router.get(
    "/quiz",
    response_model=QuizResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate 5-MCQ evaluation quiz",
    description="Triggers the Assessor Agent to scan the document matrix and compile exactly 5 conceptual multiple choice items.",
)
async def generate_quiz() -> QuizResponse:
    """
    Triggers automated quiz generation pipelines through the orchestrator.
    """
    logger.info("[CHAT_API] Intercepted trigger request for conceptual assessment quiz synthesis.")
    response: QuizResponse = await quiz_service.generate_new_quiz()
    return response


@router.post(
    "/quiz/score",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Record completed quiz performance telemetry",
    description="Logs the score metrics onto disk tracks to calibrate personalized analytics remediation models.",
)
async def score_quiz_submission(
    score: float = Body(..., embed=True, description="Total correct choices answered"),
    total: int = Body(..., embed=True, description="Total question count evaluation ceiling"),
    topic_context: str = Body(..., embed=True, description="The conceptual topic area summary evaluated"),
) -> None:
    """
    Commits transactional student score metrics to historical data trackers.
    """
    logger.info(f"[CHAT_API] Intercepted performance payload logging: {score}/{total} for '{topic_context}'")
    quiz_service.record_quiz_score_telemetry(score=score, total=total, topic_context=topic_context)


@router.get(
    "/roadmap",
    response_model=RoadmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate study milestone roadmap",
    description="Triggers the Curriculum Agent to build a sequential learning path mapping back to source pages.",
)
async def generate_roadmap() -> RoadmapResponse:
    """
    Triggers automated milestone path planning through the orchestrator.
    """
    logger.info("[CHAT_API] Intercepted trigger request for learning path roadmap layout.")
    response: RoadmapResponse = await agent_orchestrator.route_roadmap_generation()
    return response


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Compile student profiling analytics",
    description="Processes recorded score history arrays through the Analytics Agent to output custom remediation paths.",
)
async def get_student_analytics() -> AnalyticsResponse:
    """
    Gathers quiz history metrics and evaluates custom remediation paths.
    """
    logger.info("[CHAT_API] Intercepted profiling request for student telemetry analysis.")
    response: AnalyticsResponse = await analytics_service.compile_student_analytics()
    return response