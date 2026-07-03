import json
import re
from typing import List, Dict, Any
from loguru import logger
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from llm.llm_router import llm_router
from rag.retriever import knowledge_retriever
from rag.prompt_builder import PromptBuilder
from schemas.analytics import AnalyticsResponse, AnalyticsDataPayload
from utils.exceptions import AgentExecutionException


class AnalyticsAgent:
    """
    Agent responsible for processing student execution tracking history metrics.
    Aggregates performance telemetry data, queries the vector database for 
    remediation contexts, and returns a verified student analytics profile.
    """

    def __init__(self) -> None:
        logger.info("[ANALYTICS_AGENT] Initializing Student Telemetry Analytics Agent instance.")
        self._llm = llm_router.get_structured_model(temperature=0.1)

    def _clean_json_response(self, raw_text: str) -> str:
        """Strips markdown encapsulation blocks to isolate the clean JSON structure."""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    async def execute_analysis(self, raw_quiz_history: List[Dict[str, Any]]) -> AnalyticsResponse:
        """
        Processes history logs, extracts critical weakness vectors, queries ChromaDB
        for remediation content, and synthesizes a structured student analytics profile.
        """
        logger.info(f"[ANALYTICS_AGENT] Running analytics processing for {len(raw_quiz_history)} past attempts.")

        try:
            # 1. Compile historical quiz submissions into an explicit natural text overview
            history_summary_lines = []
            flagged_weaknesses = []

            for index, attempt in enumerate(raw_quiz_history):
                score = attempt.get("score", 0.0)
                total = attempt.get("total_questions", 5)
                topic = attempt.get("topic_context", "General Material")
                
                history_summary_lines.append(
                    f"Attempt #{index + 1}: Topic Area='{topic}', Achieved={score}/{total} correct answers."
                )
                
                # Flag topics falling below an 80% passing threshold for structural remediation
                if (score / total) < 0.8:
                    flagged_weaknesses.append(topic)

            history_summary_str = "\n".join(history_summary_lines)
            if not history_summary_str:
                history_summary_str = "No historical quiz submission traces found for this profile."

            # 2. Gather context chunks from ChromaDB targeting flagged weakness areas
            search_query = ", ".join(flagged_weaknesses) if flagged_weaknesses else "core curriculum subjects"
            logger.debug(f"[ANALYTICS_AGENT] Querying remediation context using vectors: '{search_query[:60]}...'")
            context_documents: List[Document] = knowledge_retriever.retrieve_relevant_chunks(search_query)
            
            # 3. Format matches into uniform context segments
            formatted_context = PromptBuilder.format_context_segments(context_documents)
            
            # 4. Assemble the dedicated analytics prompt template
            analytics_prompt = PromptBuilder.build_analytics_prompt(
                quiz_history_summary=history_summary_str,
                formatted_context=formatted_context
            )
            
            logger.debug("[ANALYTICS_AGENT] Shipping structured telemetry prompt layout to model.")
            
            # 5. Invoke the LLM asynchronously
            response = await self._llm.ainvoke([HumanMessage(content=analytics_prompt)])
            raw_content = str(response.content).strip()
            
            # 6. Clean code block backticks
            json_text = self._clean_json_response(raw_content)
            
            # 7. Parse the text stream into a dictionary structure
            try:
                parsed_data = json.loads(json_text)
            except json.JSONDecodeError as jde:
                logger.error(f"[ANALYTICS_AGENT] Failed decoding JSON telemetry payload. Trace: {raw_content}")
                raise AgentExecutionException(
                    message="Telemetry model returned an invalid JSON block structure that could not be parsed.",
                    details={"json_error": str(jde), "raw_text": raw_content}
                )

            # 8. Validate and enforce Pydantic data schemas
            try:
                # Override the summary variables with precise system metrics if missing
                if "quizzes_taken" not in parsed_data or parsed_data["quizzes_taken"] == 0:
                    parsed_data["quizzes_taken"] = len(raw_quiz_history)
                
                validated_payload = AnalyticsDataPayload.model_validate(parsed_data)
            except Exception as ve:
                logger.error(f"[ANALYTICS_AGENT] Telemetry validation mismatch: {str(ve)}")
                raise AgentExecutionException(
                    message="Generated telemetry metrics failed to map to strict analytics profile layouts.",
                    details={"validation_error": str(ve), "parsed_data": parsed_data}
                )

            logger.info("[ANALYTICS_AGENT] Profiling complete. Analytics data package finalized.")
            return AnalyticsResponse(
                success=True,
                message="Student learning analytics profiling engine executed successfully.",
                data=validated_payload,
                metadata={"history_records_parsed": len(raw_quiz_history)}
            )

        except Exception as e:
            logger.exception("[ANALYTICS_AGENT] Exception intercepted within profile analysis loops.")
            if "DatabaseEmptyException" in type(e).__name__ or "AgentExecutionException" in type(e).__name__:
                raise e
            raise AgentExecutionException(
                message="The Analytics agent failed during student profiling calculations.",
                details={"error_message": str(e)}
            )


# Instantiate agent singleton for unified application routing
analytics_agent = AnalyticsAgent()