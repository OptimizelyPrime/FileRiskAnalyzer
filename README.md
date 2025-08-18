# Repository Risk Analysis Dashboard

This project is a tool for analyzing Git repositories to identify potential risks related to code complexity, maintainability, and knowledge concentration. It generates an interactive HTML dashboard to visualize these risks.

## Features

*   **Code Complexity Analysis:** Calculates cyclomatic complexity and other metrics for Python files.
*   **Git History Analysis:** Analyzes commit history to measure churn and identify key contributors.
*   **Authorship and Knowledge Concentration:** Identifies the primary authors of files and functions to highlight knowledge silos.
*   **Interactive Dashboard:** Generates a single-file HTML dashboard to visualize the analysis results.
*   **AI-Powered Analysis:** (Optional) Uses OpenAI's GPT models to provide deeper insights into code complexity.

## How it Works

The tool operates in two main stages:

1.  **Analysis (`main.py`):**
    *   Clones the target Git repository.
    *   Analyzes the source files to calculate complexity, churn, and authorship metrics.
    *   Generates a `complexity_report.md` file with the raw analysis data.

2.  **Dashboard Generation (`generate_dashboard_with_data.py`):**
    *   Parses the `complexity_report.md` file.
    *   Calculates a "file health score" based on the analysis data.
    *   Injects the data into an HTML template (`dashboard_template.html`).
    *   Creates a final, self-contained HTML dashboard file (e.g., `generated_dashboard_20231027_120000.html`).

## Installation

1.  **Clone this repository:**
    ```bash
    git clone <this_repository_url>
    cd <this_repository_directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Optional) Set up OpenAI API Key:**
    If you want to use the AI-powered analysis features, you need to provide an OpenAI API key. You can do this by creating a `.env` file in the project root and adding your key:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```

## Usage

1.  **Run the analysis:**
    ```bash
    python main.py --repo-url <target_repo_url> --output complexity_report.md
    ```
    *   Replace `<target_repo_url>` with the URL of the Git repository you want to analyze.
    *   You can also specify a different output file for the report using the `--output` argument.

2.  **Generate the dashboard:**
    ```bash
    python generate_dashboard_with_data.py
    ```
    This script will look for `complexity_report.md` in the project root and generate the HTML dashboard in the same directory. The output file will be named with a timestamp (e.g., `generated_dashboard_20231027_120000.html`).

## Dependencies

*   [GitPython](https://gitpython.readthedocs.io/): For interacting with Git repositories.
*   [Radon](https://radon.readthedocs.io/): For code complexity metrics.
*   [Pandas](https://pandas.pydata.org/): For data manipulation.
*   [OpenAI](https://github.com/openai/openai-python): For AI-powered code analysis.
*   [LangChain](https://github.com/langchain-ai/langchain): To orchestrate interactions with the OpenAI API.
*   [Pydantic](https://docs.pydantic.dev/): For data validation.
