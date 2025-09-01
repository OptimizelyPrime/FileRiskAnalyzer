from typing import List, Dict
import os

def extract_code_from_files(repo_path: str, files: List[str]) -> Dict[str, str]:
    """
    Reads the content of specified files from a given repository path.

    Args:
        repo_path: The absolute path to the cloned repository.
        files: A list of file paths relative to the repository root.

    Returns:
        A dictionary where keys are the file paths and values are their content.
    """
    extracted_code = {}
    for file_path in files:
        full_path = os.path.join(repo_path, file_path)
        try:
            with open(full_path, 'r') as f:
                extracted_code[file_path] = f.read()
        except FileNotFoundError:
            print(f"Warning: File not found at {full_path}")
        except Exception as e:
            print(f"Error reading file {full_path}: {e}")
    return extracted_code
