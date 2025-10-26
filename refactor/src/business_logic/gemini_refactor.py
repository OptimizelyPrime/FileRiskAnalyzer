import os
import json
from typing import Dict

def _load_gemini_api_key() -> str:
    """Load Gemini API key from refactor/keys.json, fallback to env var.

    Looks for keys.json two directories up from this file (refactor/keys.json).
    """
    keys_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "keys.json"))
    api_key = None
    try:
        if os.path.exists(keys_path):
            with open(keys_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Support either key name
                api_key = data.get("gemini_api_key") or data.get("GOOGLE_API_KEY")
    except Exception as e:
        raise RuntimeError(f"Failed to read API keys from {keys_path}: {e}")

    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key not found. Add it to refactor/keys.json under 'gemini_api_key' "
            "or set the GOOGLE_API_KEY environment variable."
        )
    return api_key


def refactor_code_using_gemini(code: str) -> str:
    """
    Uses Gemini to refactor the given code to minimize cyclomatic complexity and Halstead volume.

    Args:
        code: The code to be refactored.

    Returns:
        The refactored code.
    """
    api_key = _load_gemini_api_key()

    try:
        # Lazy import to avoid crashing API startup on incompatible Python/versions
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.prompts import ChatPromptTemplate
        from langchain.schema.output_parser import StrOutputParser
    except Exception as e:
        raise RuntimeError(
            "Gemini refactoring dependencies are unavailable or incompatible. "
            "Ensure a compatible Python version (e.g., 3.11–3.13) and install matching langchain packages. "
            f"Underlying import error: {e!r}"
        )

    # Use a supported Gemini model name (v1). 'gemini-1.5-pro' is widely available.
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=api_key)

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
