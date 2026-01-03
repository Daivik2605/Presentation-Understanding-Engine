from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

llm = OllamaLLM(model="llama3:8b", temperature=0.3)

prompt = PromptTemplate(
    input_variables=["slide_text"],
    template="""
You are an education expert.

From the slide content below, generate exactly 3 multiple-choice questions.

Each question MUST include:
- "question": string
- "options": list of 4 strings
- "answer": the correct option text (must match one option exactly)
- "difficulty": "easy" or "medium"

IMPORTANT RULES:
- Output ONLY valid JSON
- Return a JSON object with a single key "questions"
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include extra text
- Do NOT number questions outside JSON

Slide content:
{slide_text}
"""
)

qa_chain = prompt | llm

