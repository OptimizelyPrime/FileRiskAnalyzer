from typing import List
import shutil
from common.utils.repo_utils import clone_repo
from datetime import datetime
from .file_extraction import extract_code_from_files

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
        print("Extracted code:")
        print(extracted_code)

        # In the future, this will:
        # 1. Analyze the specified files
        # 2. Perform refactoring
        # 3. Push the changes back to the repository
    finally:
        if temp_dir and shutil.os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory {temp_dir}")
