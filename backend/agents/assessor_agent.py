import json
import re
from typing import List
from loguru import logger
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from llm.llm_router import llm_router
from rag.retriever import knowledge_retriever
from rag.prompt_builder import PromptBuilder
from schemas.quiz import QuizResponse, QuizDataPayload, MCQQuestion
from utils.exceptions import AgentExecutionException


class AssessorAgent:
    """
    Agent responsible for analyzing the active knowledge base context
    and synthesizing a strict, production-grade 5-question conceptual quiz.
    Ensures structural integrity through explicit regex cleaning and Pydantic validation.
    """

    def __init__(self) -> None:
        logger.info("[ASSESSOR_AGENT] Initializing Quiz Assessor Agent workflow instance.")
        self._llm = llm_router.get_structured_model(temperature=0.1)

    def _clean_json_response(self, raw_text: str) -> str:
        """
        Strips markdown code fences (```json) and leading/trailing whitespace
        to isolate the raw JSON block before parsing.
        """
        cleaned = raw_text.strip()
        # Remove leading markdown ticks if present
        cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.IGNORECASE)
        # Remove trailing markdown ticks if present
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    async def execute_generation(self) -> QuizResponse:
        """
        Queries the vector base for broad core concepts, instructs Gemini to formulate
        exactly 5 MCQs, parses the text stream, and validates the output against the Pydantic model.
        """
        logger.info("[ASSESSOR_AGENT] Initializing automated 5-MCQ quiz generation pipeline.")

        try:
            # 1. Gather rich document context from the vector index
            # Passing a broad conceptual query to retrieve top structural chunks
            context_query = "core concepts, main subjects, definitions, principles, and chapters"
            context_documents: List[Document] = knowledge_retriever.retrieve_relevant_chunks(context_query)
            
            # 2. Flatten extracted documents into a clean context block
            formatted_context = PromptBuilder.format_context_segments(context_documents)
            
            # 3. Build the specialized evaluation prompt
            quiz_prompt = PromptBuilder.build_quiz_prompt(formatted_context)
            
            logger.debug("[ASSESSOR_AGENT] Dispatching structured quiz generation prompt to Gemini.")
            
            # 4. Invoke the LLM asynchronously
            response = await self._llm.ainvoke([HumanMessage(content=quiz_prompt)])
            raw_content = str(response.content).strip()
            
            # 5. Clean potential markdown wrapper leakage
            json_text = self._clean_json_response(raw_content)
            
            logger.debug(f"[ASSESSOR_AGENT] Isolated payload text for parsing: {json_text[:200]}...")
            
            # 6. Parse into dictionary structure
            try:
                parsed_data = json.loads(json_text)
            except json.JSONDecodeError as jde:
                logger.error(f"[ASSESSOR_AGENT] JSON Decode Failure. Raw payload was: {raw_content}")
                raise AgentExecutionException(
                    message="LLM returned an invalid JSON string structure that could not be parsed.",
                    details={"json_error": str(jde), "raw_output": raw_content}
                )

            # 7. Validate and bind parsed data structures using strict Pydantic rules
            try:
                validated_payload = QuizDataPayload.model_validate(parsed_data)
            except Exception as ve:
                logger.error(f"[ASSESSOR_AGENT] Pydantic validation structure mismatch: {str(ve)}")
                raise AgentExecutionException(
                    message="Generated quiz structure failed to conform to the strict production specifications.",
                    details={"validation_error": str(ve), "parsed_data": parsed_data}
                )

            logger.info(f"[ASSESSOR_AGENT] Quiz generation successful. Validated {len(validated_payload.questions)} MCQ items.")
            
            return QuizResponse(
                success=True,
                message="Production assessment quiz containing exactly 5 items compiled successfully.",
                data=validated_payload,
                metadata={
                    "model": "gemini-2.5-flash",
                    "extracted_chunks": len(context_documents)
                }
            )

        except Exception as e:
            logger.exception("[ASSESSOR_AGENT] Critical failure inside assessment quiz execution loop.")
            if "DatabaseEmptyException" in type(e).__name__ or "AgentExecutionException" in type(e).__name__:
                raise e
            raise AgentExecutionException(
                message="The Assessor agent encountered an unhandled error during quiz synthesis.",
                details={"error_message": str(e)}
            )


# Instantiate agent singleton for unified application routing
assessor_agent = AssessorAgent()