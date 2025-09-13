import os
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

def refactor_code_using_gemini(code: str) -> str:
    """
    Uses Gemini to refactor the given code to minimize cyclomatic complexity and Halstead volume.

    Args:
        code: The code to be refactored.

    Returns:
        The refactored code.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")

    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)

    prompt_template = """
    You are an expert software engineer specializing in code refactoring.
    Your task is to refactor the following code to minimize its cyclomatic complexity and Halstead volume.
    Do not add any new functionality or change the existing functionality.
    Only return the refactored code, without any explanations or markdown formatting.

    Original code:
    {code}
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    refactored_code = chain.invoke({"code": code})
    return refactored_code
