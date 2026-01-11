"""
QA Chain - LLM-based MCQ generation for slides.
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMConnectionError, LLMGenerationError

logger = get_logger(__name__)


def create_qa_llm() -> OllamaLLM:
    """Create the Ollama LLM instance for QA generation."""
    return OllamaLLM(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.qa_temperature,
        num_predict=2048,
    )


QA_PROMPT = PromptTemplate(
    input_variables=["slide_text", "language"],
    template="""You are an assessment generator creating quiz questions.

TASK:
Generate 1-2 valid MCQ questions based on the slide content.

STRICT RULES (MANDATORY):
- The "answer" MUST be exactly one of the provided options
- ALL questions and options MUST be in {language}
- Generate ALL text strictly in {language}
- If {language} is not "en", DO NOT use English words at all
- Output ONLY valid JSON
- Output MUST start with '{{' and end with '}}'
- Do NOT include any text before or after the JSON
- Do NOT include explanations, comments, or introductions

Return a JSON object with exactly one key: "questions"

Each question MUST include:
- "question": string (the question text)
- "options": list of exactly 4 strings
- "answer": must EXACTLY match one option
- "difficulty": "easy" or "medium"

Slide content:
{slide_text}

JSON Output:"""
)


# Create the chain
llm = create_qa_llm()
qa_chain = QA_PROMPT | llm


async def generate_mcqs_async(slide_text: str, language: str) -> str:
    """
    Generate MCQs asynchronously.
    
    Args:
        slide_text: The slide content to generate questions from
        language: Target language code (en, fr, hi)
    
    Returns:
        Raw JSON string with generated MCQs
    
    Raises:
        LLMConnectionError: If cannot connect to Ollama
        LLMGenerationError: If generation fails
    """
    logger.debug(f"Generating MCQs for slide (lang={language})")
    
    try:
        result = await qa_chain.ainvoke({
            "slide_text": slide_text,
            "language": language
        })
        
        raw_output = str(result).strip()
        logger.debug(f"Generated MCQs: {len(raw_output)} chars")
        return raw_output
        
    except ConnectionError as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        raise LLMConnectionError("Ollama") from e
    except Exception as e:
        logger.error(f"MCQ generation failed: {e}")
        raise LLMGenerationError("MCQs") from e


def generate_mcqs_sync(slide_text: str, language: str) -> str:
    """
    Generate MCQs synchronously.
    
    Args:
        slide_text: The slide content to generate questions from
        language: Target language code (en, fr, hi)
    
    Returns:
        Raw JSON string with generated MCQs
    """
    logger.debug(f"Generating MCQs for slide (lang={language})")
    
    try:
        result = qa_chain.invoke({
            "slide_text": slide_text,
            "language": language
        })
        
        raw_output = str(result).strip()
        logger.debug(f"Generated MCQs: {len(raw_output)} chars")
        return raw_output
        
    except ConnectionError as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        raise LLMConnectionError("Ollama") from e
    except Exception as e:
        logger.error(f"MCQ generation failed: {e}")
        raise LLMGenerationError("MCQs") from e

