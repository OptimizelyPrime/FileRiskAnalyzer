from typing import List, Dict, Any

def get_function_line_map(file_paths: List[str]) -> Dict[str, Dict[str, List[int]]]:
    """
    Given a list of file paths, returns a mapping of file_path -> function_name -> list of line numbers for that function.

    Args:
        file_paths (List[str]): List of file paths to analyze.

    Returns:
        Dict[str, Dict[str, List[int]]]: Mapping of file_path to function_name to list of line numbers.
    """
    from maintainability_score_analyzer import analyze
    import os
    function_line_map = {}
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            metrics = analyze(source_code, filepath=file_path)
            file_func_lines = {}
            # If metrics is a dict of function names to metrics dicts
            if isinstance(metrics, dict) and all(isinstance(v, dict) for v in metrics.values()):
                for func_name, func_metrics in metrics.items():
                    start = func_metrics.get('start_line', None)
                    end = func_metrics.get('end_line', None)
                    if start is not None and end is not None:
                        file_func_lines[func_name] = {
                            'start_line': start,
                            'end_line': end,
                            'lines': list(range(start, end + 1))
                        }
                    else:
                        file_func_lines[func_name] = {
                            'start_line': None,
                            'end_line': None,
                            'lines': []
                        }
            elif 'functions' in metrics:
                for func in metrics['functions']:
                    func_name = func.get('name', 'unknown')
                    start = func.get('start_line', None)
                    end = func.get('end_line', None)
                    if start is not None and end is not None:
                        file_func_lines[func_name] = {
                            'start_line': start,
                            'end_line': end,
                            'lines': list(range(start, end + 1))
                        }
                    else:
                        file_func_lines[func_name] = {
                            'start_line': None,
                            'end_line': None,
                            'lines': []
                        }
            else:
                file_func_lines['unknown'] = {
                    'start_line': None,
                    'end_line': None,
                    'lines': []
                }
            file_name = os.path.basename(file_path)
            function_line_map[file_name] = file_func_lines
        except Exception:
            file_name = os.path.basename(file_path)
            function_line_map[file_name] = {}
    return function_line_map
"""
complexity_utils.py
Utility functions for calculating cyclomatic complexity using the lizard library.
"""

from typing import List, Dict, Any


def analyze_file_complexity(file_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Analyze the cyclomatic complexity and maintainability of a file, returning function-level metrics.

    Args:
        file_path (str): Path to the file to analyze.

    Returns:
        Dict[str, Dict[str, Any]]: Dict mapping function name to metrics dict.
    """
    from maintainability_score_analyzer import analyze
    complexity_data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    metrics = analyze(source_code, filepath=file_path)
    # If the analyzer returns a dict of function names to metrics, use it directly
    if isinstance(metrics, dict) and all(isinstance(v, dict) for v in metrics.values()):
        # This is already a function-metrics dict
        complexity_data = metrics
    elif 'functions' in metrics:
        for func in metrics['functions']:
            func_name = func.get('name', 'unknown')
            # Include all keys/metrics for this function
            complexity_data[func_name] = dict(func)
    else:
        # Fallback: just use whatever top-level metrics are available
        complexity_data['unknown'] = dict(metrics)
    return complexity_data


def analyze_directory_complexity(directory_path: str, extensions: List[str] = ["py"]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Analyze all files in a directory, returning a dict mapping file path to function-metrics dict.

    Args:
        directory_path (str): Path to the directory to analyze.
        extensions (List[str], optional): List of file extensions to include. Defaults to ["py"].

    Returns:
        Dict[str, Dict[str, Dict[str, Any]]]: Dict mapping file path to function-metrics dict.
    """
    from maintainability_score_analyzer import analyze
    import os
    complexity_data = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            if any(file.endswith(f'.{ext}') for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    metrics = analyze(source_code, filepath=file_path)
                    file_func_metrics = {}
                    if 'functions' in metrics:
                        for func in metrics['functions']:
                            func_name = func.get('name', 'unknown')
                            file_func_metrics[func_name] = {
                                'cyclomatic_complexity': func.get('cyclomatic_complexity'),
                                'lines_of_code': func.get('length'),
                                'parameters': func.get('parameters'),
                                'maintenance_score': func.get('maintainability_index', metrics.get('maintainability_index')),
                            }
                    else:
                        file_func_metrics['unknown'] = {
                            'cyclomatic_complexity': metrics.get('cyclomatic_complexity'),
                            'lines_of_code': metrics.get('length'),
                            'parameters': metrics.get('parameters'),
                            'maintenance_score': metrics.get('maintainability_index'),
                        }
                    complexity_data[file_path] = file_func_metrics
                except Exception:
                    continue
    return complexity_data

def parse_complexity_report(report_content: str) -> List[Dict[str, Any]]:
    """
    Parses the content of a complexity report markdown file and returns a list of file metrics.

    Args:
        report_content (str): The content of the complexity report markdown file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a file
                               and its complexity metrics.
    """
    import re
    files_data = []

    # Regex to split the report by file sections
    file_sections = re.split(r'\n## ', report_content)
    for i, section in enumerate(file_sections):
        if i == 0 and section.strip().startswith("# Repository Complexity and Maintainability Report"):
            continue

        if not section.strip():
            continue

        section = '## ' + section

        file_match = re.search(r'## (.*)', section)
        if not file_match:
            continue

        file_name = file_match.group(1).strip()

        # Extract churn, knowledge score, and developer
        churn_table_match = re.search(r'\| Churn \| Knowledge Score \| Developer \| File Health Score \|\n\|-+\|-+\|-+\|-+\|\n\| (.*?) \| (.*?)% \| (.*?) \| (.*?) \|', section)
        if not churn_table_match:
            continue

        churn = churn_table_match.group(1).strip()
        knowledge_score = churn_table_match.group(2).strip()
        developer = churn_table_match.group(3).strip()
        file_health = churn_table_match.group(4).strip()

        # Find all function/unknown sections
        function_sections = re.findall(r'\*\*(.*?)\*\*: Maintainability Index = ([\d.]+)\n\| Lines Of Code \| Halstead Volume \| Cyclomatic Complexity \|\n\|-+\|--+\|--+\|\n\| (.*?) \| (.*?) \| (.*?) \|', section)

        functions_list = []
        for func_match in function_sections:
            func_name = func_match[0]
            maintainability_index = float(func_match[1])
            loc = int(func_match[2].strip())
            halstead_volume = float(func_match[3].strip())
            cyclomatic_complexity = int(float(func_match[4].strip()))

            functions_list.append({
                "function": func_name,
                "maintainability_index": maintainability_index,
                "length": loc,
                "halstead_volume": halstead_volume,
                "cyclomatic_complexity": cyclomatic_complexity
            })

        files_data.append({
            "file": file_name,
            "churn": int(churn),
            "knowledge_score": knowledge_score,
            "developer": developer,
            "file_health": float(file_health),
            "functions": functions_list
        })

    return files_data
