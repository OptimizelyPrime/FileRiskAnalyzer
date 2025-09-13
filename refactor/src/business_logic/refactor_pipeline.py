from typing import List, Dict
import shutil
import os
from common.utils.repo_utils import clone_repo
from datetime import datetime
from .file_extraction import extract_code_from_files
from .gemini_refactor import refactor_code_using_gemini

def save_refactored_code(repo_path: str, refactored_code: Dict[str, str]):
    """
    Saves the refactored code back to the specified files.

    Args:
        repo_path: The absolute path to the cloned repository.
        refactored_code: A dictionary where keys are the file paths and values are their new content.
    """
    for file_path, code in refactored_code.items():
        full_path = os.path.join(repo_path, file_path)
        try:
            with open(full_path, 'w') as f:
                f.write(code)
            print(f"Successfully saved refactored code to {full_path}")
        except Exception as e:
            print(f"Error saving file {full_path}: {e}")

def run(repo_url: str, branch: str, files: List[str]):
    """
    This function will contain the core business logic for the refactoring pipeline.
    """
    repo, temp_dir = None, None
    try:
        print(f"Refactoring process initiated for repo: {repo_url}, branch: {branch}, files: {files}")
        repo, temp_dir = clone_repo(repo_url, branch)
        print(f"Cloned repo to {temp_dir}")

        date_stamp = datetime.now().strftime("%Y%m%d")
        new_branch_name = f"ai-refactor-{date_stamp}"
        new_branch = repo.create_head(new_branch_name)
        new_branch.checkout()

        print(f"Created and checked out new branch: {new_branch_name}")

        extracted_code = extract_code_from_files(temp_dir, files)

        refactored_code = {}
        for file_path, code in extracted_code.items():
            print(f"Refactoring file: {file_path}")
            refactored_code[file_path] = refactor_code_using_gemini(code)

        save_refactored_code(temp_dir, refactored_code)

        # In the future, this will:
        # 1. Analyze the specified files
        # 2. Perform refactoring
        # 3. Push the changes back to the repository
    finally:
        if temp_dir and shutil.os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory {temp_dir}")
