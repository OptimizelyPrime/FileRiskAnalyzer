from utils.file_risk_utils import calculate_overall_risk
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

    # Extract file commit histories
    file_histories = get_repo_files_commit_history(repo_path)

    # Calculate churn scores (file-level)
    churn_scores = calculate_repo_churn_scores(file_histories)

    # Extract authorship data for each file (file-level)
    # authorship_data: Dict[file_path][func_name] = List[Dict[str, str]]
    authorship_data = get_repo_authorship(repo_path, source_files)

    # Calculate knowledge concentration scores (file-level)
    knowledge_concentration_scores = calculate_repo_knowledge_concentration(authorship_data)

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
            file_kc_pct = file_kc.get('top_author_pct', 'N/A')
            # Calculate file risk score
            # AMS: average maintainability index for the file
            # Weighted AMS: each function's maintainability index weighted by its LOC proportion
            ams_vals = []
            total_loc = 0
            for m in func_metrics.values():
                loc = m.get('lines_of_code')
                if m.get('maintainability_index') not in (None, 'N/A') and loc not in (None, 'N/A'):
                    ams_vals.append((m['maintainability_index'], loc))
                    total_loc += loc
            if ams_vals and total_loc > 0:
                print(f"[DEBUG] {file_name} AMS values (score, loc): {ams_vals}")
                print(f"[DEBUG] {file_name} total LOC: {total_loc}")
                ams_score = sum(idx * (loc / total_loc) for idx, loc in ams_vals)
                print(f"[DEBUG] {file_name} weighted AMS score: {ams_score}")
                risk_weights = None  # use default
            elif ams_vals:
                print(f"[DEBUG] {file_name} AMS values (score, loc): {ams_vals}")
                ams_score = sum(idx for idx, _ in ams_vals) / len(ams_vals)
                print(f"[DEBUG] {file_name} unweighted AMS score: {ams_score}")
                risk_weights = None  # use default
            else:
                ams_score = 0
                print(f"[DEBUG] {file_name} has no functions, AMS score set to 0")
                # If no functions, set quality weight to 0, distribute rest proportionally
                risk_weights = {'quality': 0.0, 'churn': 0.5, 'kc': 0.5}
            # Churn normalization (demo: divide by 10, cap at 1.0)
            try:
                churn_norm = min(1.0, float(file_churn) / 10.0) if file_churn not in ('N/A', None) else 0.0
            except Exception:
                churn_norm = 0.0
            # Knowledge concentration normalization (1 - top_author_pct/100)
            try:
                kc_norm = 1.0 - float(file_kc_pct) / 100.0 if file_kc_pct not in ('N/A', None) else 0.0
            except Exception:
                kc_norm = 0.0
            file_risk = calculate_overall_risk(ams_score, churn_norm, kc_norm, weights=risk_weights)
            outfile.write(f"## {file_name}\n\n")
            outfile.write("| Churn | Knowledge Score | Developer | File Risk |\n")
            outfile.write("|-------|-----------------|-----------|-----------|\n")
            outfile.write(f"| {file_churn} | {file_kc_pct}% | {file_dev} | {file_risk} |\n\n")

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
