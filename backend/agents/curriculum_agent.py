import json
import re
from typing import List
from loguru import logger
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from llm.llm_router import llm_router
from rag.retriever import knowledge_retriever
from rag.prompt_builder import PromptBuilder
from schemas.roadmap import RoadmapResponse, RoadmapDataPayload
from utils.exceptions import AgentExecutionException


class CurriculumAgent:
    """
    Agent responsible for analyzing the operational knowledge base context
    and parsing it into a structured, chronological study roadmap milestone track.
    Ensures absolute structural compliance using regex extraction and Pydantic validation.
    """

    def __init__(self) -> None:
        logger.info("[CURRICULUM_AGENT] Initializing Curriculum Specialist Agent instance.")
        self._llm = llm_router.get_structured_model(temperature=0.1)

    def _clean_json_response(self, raw_text: str) -> str:
        """Strips markdown encapsulation blocks to expose the raw underlying JSON block."""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    async def execute_generation(self) -> RoadmapResponse:
        """
        Gathers high-level document sections from the vector database, prompts Gemini 
        to synthesize a curriculum track, and enforces Pydantic structural validation.
        """
        logger.info("[CURRICULUM_AGENT] Commencing chronological roadmap layout planning.")

        try:
            # 1. Fetch historical structural chunks across the active database index
            context_query = "table of contents, index, chapters, overview, introductions, summary of material"
            context_documents: List[Document] = knowledge_retriever.retrieve_relevant_chunks(context_query)
            
            # 2. Convert matches into uniform context segments
            formatted_context = PromptBuilder.format_context_segments(context_documents)
            
            # 3. Assemble the explicit milestone template prompt
            roadmap_prompt = PromptBuilder.build_roadmap_prompt(formatted_context)
            
            logger.debug("[CURRICULUM_AGENT] Shipping structured prompt layout to model.")
            
            # 4. Trigger asynchronous generation call
            response = await self._llm.ainvoke([HumanMessage(content=roadmap_prompt)])
            raw_content = str(response.content).strip()
            
            # 5. Clean backtick artifacts
            json_text = self._clean_json_response(raw_content)
            
            # 6. Parse into standard dictionary structures
            try:
                parsed_data = json.loads(json_text)
            except json.JSONDecodeError as jde:
                logger.error(f"[CURRICULUM_AGENT] Failed decoding returned JSON package. Raw trace: {raw_content}")
                raise AgentExecutionException(
                    message="Curriculum model returned invalid JSON markup that could not be parsed.",
                    details={"json_error": str(jde), "raw_text": raw_content}
                )

            # 7. Validate and enforce Pydantic data schemas
            try:
                validated_payload = RoadmapDataPayload.model_validate(parsed_data)
            except Exception as ve:
                logger.error(f"[CURRICULUM_AGENT] Structural compliance validation mismatch: {str(ve)}")
                raise AgentExecutionException(
                    message="Generated timeline data failed to map to strict roadmap specifications.",
                    details={"validation_error": str(ve), "parsed_data": parsed_data}
                )

            logger.info(f"[CURRICULUM_AGENT] Pathing generation complete. Compiled '{validated_payload.title}' path.")
            
            return RoadmapResponse(
                success=True,
                message="Chronological study roadmap synthesized successfully from document context.",
                data=validated_payload,
                metadata={
                    "milestone_count": len(validated_payload.milestones),
                    "model_allocation": "gemini-2.5-flash"
                }
            )

        except Exception as e:
            logger.exception("[CURRICULUM_AGENT] Exception intercepted within structural generation loops.")
            if "DatabaseEmptyException" in type(e).__name__ or "AgentExecutionException" in type(e).__name__:
                raise e
            raise AgentExecutionException(
                message="The Curriculum agent failed during structured learning path planning.",
                details={"error_message": str(e)}
            )


# Instantiate singleton for shared service routing layers
curriculum_agent = CurriculumAgent()