from typing import Dict

def refactor_with_llm(code_by_file: Dict[str, str]) -> Dict[str, str]:
    """
    Simulates refactoring code using an LLM.

    Args:
        code_by_file: A dictionary where keys are file paths and values are their content.

    Returns:
        A dictionary with the refactored code.
    """
    refactored_code = {}
    for file_path, code in code_by_file.items():
        refactored_code[file_path] = "# Refactored by AI\n" + code
    return refactored_code
