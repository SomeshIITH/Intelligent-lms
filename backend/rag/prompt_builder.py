from typing import List
from loguru import logger
from langchain_core.documents import Document


class PromptBuilder:
    """
    Constructs high-context, production-grade prompt templates for the multi-agent system.
    Injects contextual document snippets into structured instructions to prevent hallucinations.
    """

    @staticmethod
    def format_context_segments(documents: List[Document]) -> str:
        """
        Flattens an array of LangChain Document objects into a clean, readable context string
        with explicit page markers for precise citation mapping.
        """
        logger.info(f"[PROMPT_BUILDER] Formatting {len(documents)} context chunks for prompt injection.")
        formatted_segments = []
        
        for idx, doc in enumerate(documents):
            page_num = doc.metadata.get("page", "Unknown")
            content = doc.page_content.strip()
            segment_str = f"--- CONTEXT BLOCK #{idx + 1} (Source Page: {page_num}) ---\n{content}"
            formatted_segments.append(segment_str)
            
        return "\n\n".join(formatted_segments)

    @staticmethod
    def build_tutor_prompt(query: str, formatted_context: str, history_str: str) -> str:
        """
        Compiles the primary prompt for the interactive RAG AI Tutor agent.
        """
        logger.debug(f"[PROMPT_BUILDER] Assembling RAG Tutor prompt template for query: '{query[:40]}...'")
        
        return f"""You are a Senior Academic AI Tutor inside an Intelligent LMS. Your goal is to help students master concepts using only the provided document text.

CRITICAL OPERATIONAL RULES:
1. Rely ONLY on the provided Context Blocks to formulate your answer. If the answer cannot be found or reasonably inferred from the context, state clearly that you cannot find it in the source document.
2. Use professional, encouraging, clear language adapted to the user's apparent vocabulary level.
3. Use Markdown formatting (bolding, headers, tables, bullet points) to ensure high readability. Avoid wall-of-text responses.
4. When citing information, explicitly state which source page it came from (e.g., "[Page 12]").

CONVERSATION HISTORY:
{history_str}

DOCUMENT KNOWLEDGE BASE CONTEXT:
{formatted_context}

STUDENT QUESTION:
{query}

YOUR Grounded, Helpful, and Structured Markdown Answer:"""

    @staticmethod
    def build_quiz_prompt(formatted_context: str) -> str:
        """
        Compiles the prompt that instructs the assessor agent to return a strict JSON structure
        containing exactly 5 Multiple Choice Questions.
        """
        logger.debug("[PROMPT_BUILDER] Assembling Quiz Assessor prompt template.")
        
        return f"""You are an Expert Academic Assessor Agent. Your task is to generate exactly 5 multiple choice questions (MCQs) designed to evaluate a student's deep conceptual understanding of the provided document text.

CRITICAL INSTRUCTIONS:
1. Generate EXACTLY 5 questions based on the provided context. No more, no less.
2. Each question must have exactly 4 options.
3. The questions must test conceptual mastery and understanding, not superficial keyword matching.
4. You MUST respond with a single, valid JSON object that fits the specified schema. Do not include markdown code block backticks (```json) or any conversational text around the JSON.

DOCUMENT KNOWLEDGE BASE CONTEXT:
{formatted_context}

REQUIRED JSON OUTPUT STRUCTURE (Provide raw JSON only):
{{
  "questions": [
    {{
      "id": 1,
      "question": "Clear, objective question stem text based on context...",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_option_index": 1,
      "explanation": "Detailed pedagogical reasoning explaining why the option at index 1 is correct and why the others are wrong."
    }},
    ...
  ]
}}"""

    @staticmethod
    def build_roadmap_prompt(formatted_context: str) -> str:
        """
        Compiles the prompt that instructs the curriculum agent to return a sequential
        learning timeline as a strict JSON payload.
        """
        logger.debug("[PROMPT_BUILDER] Assembling Curriculum Roadmap prompt template.")
        
        return f"""You are a Principal Curriculum Specialist Agent. Your task is to analyze the provided document text and synthesize a highly optimized, chronological study roadmap for a student.

CRITICAL INSTRUCTIONS:
1. Break down the entire material logically into progressive, structured milestones.
2. Provide a macro title for the roadmap and identify the inferred target audience profile.
3. For each milestone, provide an estimated number of hours required and map it to the exact source pages from the context.
4. You MUST respond with a single, valid JSON object that fits the specified schema. Do not include markdown code block backticks (```json) or any conversational text around the JSON.

DOCUMENT KNOWLEDGE BASE CONTEXT:
{formatted_context}

REQUIRED JSON OUTPUT STRUCTURE (Provide raw JSON only):
{{
  "title": "Comprehensive Title for the Learning Path",
  "target_audience": "Inferred proficiency level or student tier",
  "milestones": [
    {{
      "id": 1,
      "title": "Name of Phase 1",
      "description": "High-level summary of what this phase covers.",
      "key_concepts": ["Concept Alpha", "Concept Beta"],
      "estimated_hours": 3.5,
      "source_pages": [1, 2, 3]
    }}
  ]
}}"""

    @staticmethod
    def build_analytics_prompt(quiz_history_summary: str, formatted_context: str) -> str:
        """
        Compiles the prompt that instructs the analytics agent to evaluate past scores and generate
        remediation plans mapped directly back to source documents.
        """
        logger.debug("[PROMPT_BUILDER] Assembling Analytics Evaluator prompt template.")
        
        return f"""You are a Principal Student Telemetry and Analytics Agent. Your task is to process a student's quiz performance history, identify conceptual strengths/weaknesses, and compile an actionable remediation plan based on the source document context.

CRITICAL INSTRUCTIONS:
1. Analyze the raw score performance trends provided.
2. Identify which overall concepts are mastered and which need urgent attention.
3. Formulate a comprehensive Markdown-formatted remediation plan that tells the student exactly what to read, citing specific source pages from the document text.
4. You MUST respond with a single, valid JSON object that fits the specified schema. Do not include markdown code block backticks (```json) or any conversational text around the JSON.

STUDENT PERFORMANCE DATA SUMMARY:
{quiz_history_summary}

DOCUMENT KNOWLEDGE BASE CONTEXT:
{formatted_context}

REQUIRED JSON OUTPUT STRUCTURE (Provide raw JSON only):
{{
  "overall_score": 75.0,
  "quizzes_taken": 2,
  "topic_breakdown": [
    {{
      "topic_name": "Name of Topic Area",
      "score_percentage": 60.0,
      "question_count": 5
    }}
  ],
  "strengths": ["List of mastered topics"],
  "weaknesses": ["List of weak topics needing review"],
  "remediation_plan": "Extensive Markdown formatted step-by-step review strategy mentioning exact source pages."
}}"""