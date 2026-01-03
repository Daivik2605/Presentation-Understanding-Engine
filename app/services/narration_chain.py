from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

llm = OllamaLLM(
    model="llama3:8b",
    temperature=0.4
)

prompt = PromptTemplate(
    input_variables=["slide_text"],
    template="""
You are an experienced teacher.

Explain the following slide content clearly in a natural teaching tone.
Do not repeat the text verbatim.
Keep it concise and easy to understand.

Slide content:
{slide_text}
"""
)

# Modern LangChain RunnableSequence
narration_chain = prompt | llm
# Old LangChain LLMChain (if needed)
# from langchain_core.chains import LLMChain
# narration_chain = LLMChain(llm=llm, prompt=prompt)