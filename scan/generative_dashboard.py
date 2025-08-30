"""
generative_dashboard.py
Generates an HTML/JavaScript dashboard with a heatmap from complexity_report.md using generative AI for summary and visualization code.
"""

import os
import openai
import json

REPORT_PATH = os.path.join(os.getcwd(), "complexity_report.md")
OUTPUT_PATH = os.path.join(os.getcwd(), "dashboard_generated.html")
OPENAI_MODEL = "gpt-4o"

# Load OpenAI API key from keys.json
KEYS_PATH = os.path.join(os.getcwd(), "keys.json")
with open(KEYS_PATH, encoding="utf-8") as kf:
    keys = json.load(kf)
OPENAI_API_KEY = keys.get("openai_api_key")

# --- Read the complexity report ---
def read_report(report_path):
    with open(report_path, encoding="utf-8") as f:
        return f.read()

# --- Generate summary and HTML using OpenAI ---
def generate_dashboard_with_openai(report_content):
    prompt = f"""
You are an expert data parser. Given the following repository analysis report, extract and return a JSON array containing ALL records, one for each function in the report, in the following format:
{{ "file": "GameEngine.java", "function": "startGame", "cyclomatic_complexity": 12, "churn_score": 0, "knowledge_score": "85% (Greg Jeffers)", "file_health_score": 75.5 }}

Return a JSON array (not just one record, but an array of all records), for example:
[
  {{ "file": "GameEngine.java", "function": "startGame", "cyclomatic_complexity": 12, "churn_score": 0, "knowledge_score": "85% (Greg Jeffers)", "file_health_score": 75.5 }},
  {{ "file": "Parser.java", "function": "parse", "cyclomatic_complexity": 27, "churn_score": 5, "knowledge_score": "100% (Greg Jeffers)", "file_health_score": 45.0 }}
  // ...more records...
]

Each record should represent a function from the report, with the following fields:
- file: the file name (no path, just the file)
- function: the function name
- cyclomatic_complexity: integer, from the function-level metrics table
- churn_score: integer, from the file-level table
- knowledge_score: string, combining the percentage and developer from the file-level table (e.g., "85% (Greg Jeffers)")
- file_health_score: float, from the file-level table

Return ONLY the JSON array, no explanation or extra text. Parse the report content below:
{report_content}
"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.2
    )
    # Parse the JSON array from the response
    import json as _json
    content = response.choices[0].message.content.strip()
    try:
        records = _json.loads(content)
    except Exception:
        # Try to extract JSON array if extra text is present
        import re as _re
        match = _re.search(r'(\[.*\])', content, _re.DOTALL)
        if match:
            records = _json.loads(match.group(1))
        else:
            raise ValueError("Could not parse JSON from OpenAI response")
    return records

