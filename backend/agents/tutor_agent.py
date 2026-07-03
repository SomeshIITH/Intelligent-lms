import json
from typing import List, Optional
from loguru import logger
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from llm.llm_router import llm_router
from rag.retriever import knowledge_retriever
from rag.prompt_builder import PromptBuilder
from schemas.chat import ChatMessageRequest, ChatResponse, ChatDataPayload, ChatCitation
from utils.exceptions import LLMException


class TutorAgent:
    """
    Agent responsible for conducting interactive, context-grounded tutoring sessions.
    Queries the vector store for grounding documents, structures chat histories, 
    and handles conversational reasoning via Gemini 2.5 Flash.
    """

    def __init__(self) -> None:
        logger.info("[TUTOR_AGENT] Initializing RAG Tutor Agent workflow instance.")
        self._llm = llm_router.get_tutor_model(temperature=0.3)

    def _format_history(self, history: List[str]) -> str:
        """Flattens incoming alternating conversation pairs into a single string context."""
        if not history:
            return "No prior conversation history recorded."
            
        formatted_history_lines = []
        for index, msg_content in enumerate(history):
            # Alternates between Student and Tutor labels sequentially
            speaker = "Student" if index % 2 == 0 else "Tutor"
            formatted_history_lines.append(f"{speaker}: {msg_content.strip()}")
            
        return "\n".join(formatted_history_lines)

    async def execute(self, payload: ChatMessageRequest) -> ChatResponse:
        """
        Processes a student query by fetching relevant context documents and running
        a conversational reasoning loop through Gemini 2.5 Flash.
        """
        query = payload.message
        logger.info(f"[TUTOR_AGENT] Received conversational tutoring query: '{query[:50]}...'")

        try:
            # 1. Fetch relevant context documents from the vector database
            context_documents: List[Document] = knowledge_retriever.retrieve_relevant_chunks(query)
            
            # 2. Extract page numbers and content segments to build structured citations
            citations: List[ChatCitation] = []
            for doc in context_documents:
                citations.append(
                    ChatCitation(
                        page=int(doc.metadata.get("page", 1)),
                        content=doc.page_content.strip()
                    )
                )

            # 3. Format the chat history and context segments for prompt injection
            history_str = self._format_history(payload.history or [])
            formatted_context = PromptBuilder.format_context_segments(context_documents)
            
            # 4. Assemble the finalized prompt template
            final_prompt = PromptBuilder.build_tutor_prompt(
                query=query,
                formatted_context=formatted_context,
                history_str=history_str
            )
            
            logger.debug("[TUTOR_AGENT] Dispatching prompt matrix to Gemini 2.5 Flash framework.")
            
            # 5. Execute the generation loop via LangChain
            response = await self._llm.ainvoke([HumanMessage(content=final_prompt)])
            raw_answer = str(response.content).strip()
            
            logger.info(f"[TUTOR_AGENT] Successfully received generation payload (Length: {len(raw_answer)} chars)")
            
            # 6. Package the result into the standard response envelope
            return ChatResponse(
                success=True,
                message="AI Tutor answer compiled successfully.",
                data=ChatDataPayload(
                    answer=raw_answer,
                    citations=citations
                ),
                metadata={
                    "model": "gemini-2.5-flash",
                    "citation_count": len(citations)
                }
            )

        except Exception as e:
            logger.exception(f"[TUTOR_AGENT] Failure encountered inside processing loops for query '{query[:30]}'")
            if "DatabaseEmptyException" in type(e).__name__:
                raise e
            raise LLMException(
                message="The AI Tutor agent encountered a failure while generating a response.",
                details={"error_message": str(e)}
            )


# Instantiate agent singleton for unified application routing
tutor_agent = TutorAgent()