"""
Narration Chain - LLM-based narration generation for slides.
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMConnectionError, LLMGenerationError

logger = get_logger(__name__)


def create_narration_llm() -> OllamaLLM:
    """Create the Ollama LLM instance for narration."""
    return OllamaLLM(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.narration_temperature,
        num_predict=1024,
    )


NARRATION_PROMPT = PromptTemplate(
    input_variables=["slide_text", "language"],
    template="""You are an experienced teacher explaining content to students.

TASK:
Create a natural spoken narration for the following slide content.

IMPORTANT RULES:
- Generate narration ONLY (spoken explanation)
- Do NOT ask questions or generate quizzes
- Do NOT generate JSON or structured data
- Do NOT mention "questions", "MCQs", or "quiz"
- Generate the narration in: {language}
- Use a natural, engaging teaching tone
- Explain concepts clearly without repeating text verbatim
- Keep it concise but informative (2-4 paragraphs)

Slide content:
{slide_text}

Narration:"""
)


# Create the chain
llm = create_narration_llm()
narration_chain = NARRATION_PROMPT | llm


async def generate_narration_async(slide_text: str, language: str) -> str:
    """
    Generate narration asynchronously.
    
    Args:
        slide_text: The slide content to narrate
        language: Target language code (en, fr, hi)
    
    Returns:
        Generated narration text
    
    Raises:
        LLMConnectionError: If cannot connect to Ollama
        LLMGenerationError: If generation fails
    """
    logger.debug(f"Generating narration for slide (lang={language})")
    
    try:
        result = await narration_chain.ainvoke({
            "slide_text": slide_text,
            "language": language
        })
        
        narration = str(result).strip()
        logger.debug(f"Generated narration: {len(narration)} chars")
        return narration
        
    except ConnectionError as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        raise LLMConnectionError("Ollama") from e
    except Exception as e:
        logger.error(f"Narration generation failed: {e}")
        raise LLMGenerationError("narration") from e


def generate_narration_sync(slide_text: str, language: str) -> str:
    """
    Generate narration synchronously.
    
    Args:
        slide_text: The slide content to narrate
        language: Target language code (en, fr, hi)
    
    Returns:
        Generated narration text
    """
    logger.debug(f"Generating narration for slide (lang={language})")
    
    try:
        result = narration_chain.invoke({
            "slide_text": slide_text,
            "language": language
        })
        
        narration = str(result).strip()
        logger.debug(f"Generated narration: {len(narration)} chars")
        return narration
        
    except ConnectionError as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        raise LLMConnectionError("Ollama") from e
    except Exception as e:
        logger.error(f"Narration generation failed: {e}")
        raise LLMGenerationError("narration") from e