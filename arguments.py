import argparse

def parse_args():
    """
    Parse the command line arguments.
    Returns:
        Namespace: contains the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Analyze cyclomatic complexity of a repository using AI.")
    parser.add_argument("--github-username", required=False, help="GitHub username (optional for public repos)")
    parser.add_argument("--github-token", required=False, help="GitHub personal access token (optional for public repos)")
    parser.add_argument("--repo-url", required=True, help="Repository URL (HTTPS only)")
    parser.add_argument("--output", default="complexity_report.md", help="Output report file")
    return parser.parse_args()
