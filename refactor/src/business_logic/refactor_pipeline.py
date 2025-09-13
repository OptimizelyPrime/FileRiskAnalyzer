from typing import List, Dict
import shutil
import os
from datetime import datetime
import requests

from common.utils.repo_utils import clone_repo
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


def create_pull_request(repo_url: str, head: str, base: str):
    """Create a pull request on GitHub for the refactored branch.

    Args:
        repo_url: URL of the repository on GitHub.
        head: Name of the branch containing the changes.
        base: Name of the branch to merge into.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set; skipping pull request creation.")
        return

    try:
        path = repo_url.rstrip("/").replace(".git", "").split("github.com/")[-1]
        owner, repo = path.split("/", 1)
    except ValueError:
        print(f"Unable to parse owner and repo from URL: {repo_url}")
        return

    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"token {token}"}
    data = {
        "title": "AI-powered refactoring",
        "head": head,
        "base": base,
        "body": "Automated refactoring via Gemini",
    }
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        if response.status_code in (200, 201):
            pr_url = response.json().get("html_url")
            print(f"Created pull request: {pr_url}")
        else:
            print(f"Failed to create pull request: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error while creating pull request: {e}")

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

        print("Committing and pushing changes...")
        try:
            repo.git.add(all=True)
            repo.index.commit("AI-powered refactoring")
            origin = repo.remote(name='origin')
            origin.push(new_branch_name)
            print(f"Pushed changes to branch {new_branch_name}")
            create_pull_request(repo_url, new_branch_name, branch)
        except Exception as e:
            print(f"Error committing or pushing changes: {e}")
    finally:
        if temp_dir and shutil.os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory {temp_dir}")
