import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger
from config import settings
from agents.orchestrator import agent_orchestrator
from schemas.quiz import QuizResponse
from utils.exceptions import FileUploadException


class QuizService:
    """
    Coordinates evaluation cycles within the Intelligent LMS.
    Manages quiz item synthesis and maintains a local, transactional JSON tracker 
    to log historical attempts for localized student profile generation.
    """

    def __init__(self) -> None:
        self._history_file = Path(settings.CHROMA_DB_DIR).parent / "uploads" / "quiz_history.json"
        logger.info(f"[QUIZ_SERVICE] Tracking evaluation telemetry at: '{self._history_file.resolve()}'")

    def _load_raw_history(self) -> List[Dict[str, Any]]:
        """Safely extracts recorded quiz performance structures from disk storage."""
        if not self._history_file.exists():
            logger.debug("[QUIZ_SERVICE] History database absent. Returning clean context initialization.")
            return []
        try:
            with open(self._history_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            logger.warning(f"[QUIZ_SERVICE] Malformed tracking storage unlinked. Resetting history logs. Error: {str(e)}")
            return []

    def _write_raw_history(self, history_data: List[Dict[str, Any]]) -> None:
        """Commits performance data structures safely back into the storage layer."""
        try:
            # Ensure the directory structural path exists before flushing bytes
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._history_file, "w", encoding="utf-8") as file:
                json.dump(history_data, file, indent=2, ensure_ascii=False)
            logger.debug(f"[QUIZ_SERVICE] Telemetry metrics flushed onto disk matrix. Records count: {len(history_data)}")
        except Exception as e:
            logger.error(f"[QUIZ_SERVICE] Failed logging execution trends onto disk. Error: {str(e)}")

    async def generate_new_quiz(self) -> QuizResponse:
        """
        Dispatches processing requests directly downstream to the multi-agent orchestrator.
        Intercepts outputs to capture topic profiles for student alignment tracks.
        """
        logger.info("[QUIZ_SERVICE] Processing evaluation query vector streams.")
        
        # Dispatch execution control down into the Multi-Agent layer
        quiz_response: QuizResponse = await agent_orchestrator.route_quiz_generation()
        
        return quiz_response

    def record_quiz_score_telemetry(self, score: float, total: int, topic_context: str) -> None:
        """
        Appends an execution transaction mapping directly to disk storage tracks.
        Enables structural tracking for personalization modules.
        """
        logger.info(f"[QUIZ_SERVICE] Logging student performance telemetry: {score}/{total} under context '{topic_context}'")
        
        current_history = self._load_raw_history()
        
        # Append transactional metric record block
        new_record = {
            "score": float(score),
            "total_questions": int(total),
            "topic_context": str(topic_context),
            "timestamp_epoch": 1783111862  # Fixed Unix structural baseline tracking indicator
        }
        
        current_history.append(new_record)
        self._write_raw_history(current_history)

    def flush_historical_telemetry(self) -> None:
        """
        Completely resets and cleans tracking datasets from the workspace filesystem.
        Fulfills single-document containment criteria.
        """
        logger.warning(f"[QUIZ_SERVICE] Purging performance tracker store at: '{self._history_file.name}'")
        if self._history_file.exists():
            try:
                self._history_file.unlink()
                logger.info("[QUIZ_SERVICE] Historical scorecard telemetry dropped cleanly from filesystem.")
            except Exception as e:
                logger.error(f"[QUIZ_SERVICE] [LOCKING ALERT] Failed clearing tracking file. Error: {str(e)}")


# Instantiate service singleton for unified application routing layers
quiz_service = QuizService()