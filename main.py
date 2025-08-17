from utils.file_risk_utils import calculate_file_health_score

import os
from arguments import parse_args
from utils.repo_utils import clone_repo, find_source_files
from utils.openai_utils import initialize_openai_api, analyze_file_with_ai
from utils.complexity_utils import analyze_file_complexity
from utils.file_history_utils import get_repo_files_commit_history
from utils.churn_utils import calculate_repo_churn_scores
from utils.authorship_utils import get_repo_authorship
from utils.knowledge_concentration_utils import calculate_repo_knowledge_concentration
from utils.debt_score_utils import calculate_debt_scores
from time import sleep

def main():
    args = parse_args()

    # Initialize OpenAI API
    if not initialize_openai_api():
        return

    repo_path = clone_repo(args.repo_url, args.github_username, args.github_token)
    source_files = find_source_files(repo_path)
    results = {}

    from datetime import datetime
    since_dt = datetime.fromtimestamp(args.since)

    # Extract file commit histories
    file_histories = get_repo_files_commit_history(repo_path, since=since_dt)

    # Calculate churn scores (file-level)
    churn_scores = calculate_repo_churn_scores(file_histories)

    # Extract authorship data for each file (file-level)
    # authorship_data: Dict[file_path][func_name] = List[Dict[str, str]]
    authorship_data = get_repo_authorship(repo_path, source_files)

    # Calculate knowledge concentration scores (file-level)
    knowledge_concentration_scores = calculate_repo_knowledge_concentration(authorship_data, since=since_dt)

    import os
    for file_path in source_files:
        try:
            # complexity_result = analyze_file_with_ai(file_path, code)
            complexity_result = analyze_file_complexity(file_path)
            file_name = os.path.basename(file_path)
            results[file_name] = complexity_result
        except Exception as e:
            print(f"[WARN] Skipping {file_path}: {e}")
            continue
        sleep(1)

    # Calculate unified Debt Scores
    #debt_scores_df = calculate_debt_scores(results, churn_scores, knowledge_concentration_scores)

    # Generate a report organized by file, then by function
    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write("# Repository Complexity and Maintainability Report\n\n")
        for file_name, func_metrics in results.items():
            # File-level metrics
            file_churn = churn_scores.get(file_name, 'N/A')
            file_kc = knowledge_concentration_scores.get(file_name, {})
            file_dev = file_kc.get('top_author', 'N/A')
            file_kc_pct = file_kc.get('top_author_pct', 0.0)
            # Convert churn to int, default to 0

            try:
                churn_val = int(file_churn) if file_churn not in ('N/A', None) else 0
            except (ValueError, TypeError):
                churn_val = 0
            # Convert kc_pct to float, default to 0.0
            try:
                kc_val = float(file_kc_pct) if file_kc_pct not in ('N/A', None) else 0.0
            except (ValueError, TypeError):
                kc_val = 0.0
            # Calculate file health score using the new function
            file_health = calculate_file_health_score(func_metrics, churn_val, kc_val)

            outfile.write(f"## {file_name}\n\n")
            outfile.write("| Churn | Knowledge Score | Developer | File Health Score |\n")
            outfile.write("|-------|-----------------|-----------|-------------------|\n")
            outfile.write(f"| {churn_val} | {kc_val}% | {file_dev} | {file_health} |\n\n")

            # Function-level metrics
            for func_name, metrics in func_metrics.items():
                maint_idx = metrics.get('maintainability_index', 'N/A')
                outfile.write(f"**{func_name}**: Maintainability Index = {maint_idx}\n")
                # Exclude 'maintainability_index', 'length', 'parameters' from the table, show all other metrics
                exclude_keys = {'maintainability_index', 'length', 'parameters'}
                metric_keys = [k for k in metrics.keys() if k not in exclude_keys]
                if metric_keys:
                    # Table header
                    outfile.write("| " + " | ".join([k.replace('_', ' ').title() for k in metric_keys]) + " |\n")
                    outfile.write("|" + "|".join(['-' * (len(k) + 2) for k in metric_keys]) + "|\n")
                    # Table row
                    outfile.write("| " + " | ".join(str(metrics.get(k, 'N/A')) for k in metric_keys) + " |\n\n")
                else:
                    outfile.write("No additional metrics available.\n\n")
        # outfile.write("\n# Final Debt Scores (Sorted)\n\n")
        # outfile.write(debt_scores_df.to_string(index=False))
        outfile.write("\n\n")

if __name__ == "__main__":
    main()
