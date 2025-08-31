import tempfile
from git import Repo
import os

def clone_repo(repo_url, branch, username=None, token=None):
    """
    Clones a repository from a HTTPS URL to a temporary directory.
    If username/token are provided, uses them for authentication. Otherwise, attempts to clone as a public repo.
    Returns:
        tuple: A tuple containing the git.Repo object and the path to the temporary directory.
    """
    temp_dir = tempfile.mkdtemp()
    if repo_url.startswith("https://"):
        if username and token:
            url_with_auth = repo_url.replace("https://", f"https://{username}:{token}@")
        else:
            url_with_auth = repo_url  # Assume public repo
    else:
        raise ValueError("Only HTTPS URLs are supported.")
    print(f"Cloning {repo_url} into {temp_dir}...")
    repo = Repo.clone_from(url_with_auth, temp_dir, branch=branch)
    return repo, temp_dir

def find_source_files(repo_path):
    """
    Recursively finds all files in the repository path.
    Returns:
        list: A list of file paths.
    """
    all_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.__contains__('.git'):
                continue
            all_files.append(file_path)
    return all_files