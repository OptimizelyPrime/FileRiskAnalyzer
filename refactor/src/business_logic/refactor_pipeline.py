from typing import List
import shutil
from common.utils.repo_utils import clone_repo
from datetime import datetime
import os
from .file_extraction import extract_code_from_files
from .llm_utils import refactor_with_llm
from .git_utils import commit_and_push_changes

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

        refactored_code = refactor_with_llm(extracted_code)

        for file_path, code in refactored_code.items():
            full_path = os.path.join(temp_dir, file_path)
            with open(full_path, 'w') as f:
                f.write(code)

        commit_message = "AI refactoring"
        commit_and_push_changes(repo, new_branch_name, commit_message)

    finally:
        if temp_dir and shutil.os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory {temp_dir}")
