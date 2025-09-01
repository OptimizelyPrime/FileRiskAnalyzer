from common.utils.file_health_utils import calculate_file_health_score
from common.utils.complexity_utils import parse_complexity_report
import os
import json
import time
import re

TEMPLATE_PATH = os.path.join(os.getcwd(), "dashboard_template.html")
REPORT_PATH = os.path.join(os.getcwd(), "complexity_report.md")

def add_risk_to_data(records):
    for record in records:
        func_metrics_dict = {
            f['function']: {
                'maintainability_index': f.get('maintainability_index'),
                'lines_of_code': f.get('length')
            } for f in record.get('functions', [])
        }

        raw_churn = record.get('churn', 0)

        try:
            raw_kc_pct = float(record.get('knowledge_score', '0%').replace('%',''))
        except (ValueError, AttributeError):
            raw_kc_pct = 0.0

        record['file_health'] = calculate_file_health_score(func_metrics_dict, raw_churn, raw_kc_pct)

        record['lines_of_code'] = sum(f.get('length', 0) for f in record.get('functions', []))

    return records

def generate_dashboard(repo_url=None):
    with open(REPORT_PATH, encoding="utf-8") as f:
        report_content = f.read()

    records = parse_complexity_report(report_content)
    records_with_risk = add_risk_to_data(records)

    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()

    js_records = ",\n            ".join([
        json.dumps(rec, ensure_ascii=False) for rec in records_with_risk
    ])

    html_out = template.replace("||DATA||", js_records)
    if repo_url:
        html_out = html_out.replace("||REPO_URL||", repo_url)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(os.getcwd(), f"generated_dashboard_{ts}.html")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Dashboard written to: {out_path}")

if __name__ == "__main__":
    generate_dashboard()
