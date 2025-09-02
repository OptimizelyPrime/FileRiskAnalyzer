from git import Repo

def commit_and_push_changes(repo: Repo, new_branch_name: str, commit_message: str):
    """
    Commits and pushes changes to a new branch.

    Args:
        repo: The git.Repo object.
        new_branch_name: The name of the new branch.
        commit_message: The commit message.
    """
    repo.git.add(A=True)
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push(new_branch_name)
    print(f"Pushed changes to branch {new_branch_name}")
