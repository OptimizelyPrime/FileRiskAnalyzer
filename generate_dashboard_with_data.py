from utils.file_risk_utils import calculate_overall_risk
import os
import json
import time
import re

TEMPLATE_PATH = os.path.join(os.getcwd(), "dashboard_template.html")
REPORT_PATH = os.path.join(os.getcwd(), "complexity_report.md")

def parse_complexity_report(report_path):
    with open(report_path, encoding="utf-8") as f:
        lines = f.readlines()

    files = []
    current_file = None
    current_functions = []
    churn = None
    knowledge_score = None
    developer = None
    i = 0
    # For demo, use dummy normalized churn/kc; in real use, compute from repo data
    def dummy_normalize(val, max_val=10):
        try:
            v = float(val)
            return min(1.0, max(0.0, v / max_val))
        except Exception:
            return 0.0

    while i < len(lines):
        line = lines[i].strip()
        # File section
        if line.startswith('## '):
            # Save previous file
            if current_file:
                # Calculate file-level metrics for risk
                ams_score = None
                if current_functions:
                    ams_vals = [f['maintainability_index'] for f in current_functions if f.get('maintainability_index') is not None]
                    if ams_vals:
                        ams_score = sum(ams_vals) / len(ams_vals)
                churn_norm = dummy_normalize(churn)
                # For demo, use 1 - knowledge_score as normalized knowledge concentration (if percent string)
                try:
                    kc_norm = 1.0 - float(knowledge_score.replace('%',''))/100.0 if knowledge_score and '%' in knowledge_score else 0.0
                except Exception:
                    kc_norm = 0.0
                file_risk = calculate_overall_risk(ams_score or 0, churn_norm, kc_norm)
                files.append({
                    'file': current_file,
                    'churn': churn,
                    'knowledge_score': knowledge_score,
                    'developer': developer,
                    'file_risk': file_risk,
                    'lines_of_code': file_loc,
                    'functions': current_functions
                })
            current_file = line[3:].strip()
            current_functions = []
            churn = None
            knowledge_score = None
            developer = None
            file_loc = None
            i += 1
            # Look for churn/knowledge/developer table
            while i < len(lines):
                if lines[i].strip().startswith('|') and 'Churn' in lines[i]:
                    # header row
                    i += 2 # skip header and separator
                    vals = [v.strip() for v in lines[i].strip().strip('|').split('|')]
                    churn = int(vals[0]) if vals[0].isdigit() else None
                    knowledge_score = vals[1]
                    developer = vals[2]
                    i += 1
                    break
                i += 1
            # Look for file-level LOC (first function or until next file or EOF)
            j = i
            while j < len(lines):
                l = lines[j].strip()
                if l.startswith('**') and 'Maintainability Index' in l:
                    # Next two lines: header, divider, then values
                    if j+3 < len(lines):
                        vals = [v.strip() for v in lines[j+3].strip().strip('|').split('|')]
                        try:
                            file_loc = int(vals[0]) if vals[0] else None
                        except Exception:
                            file_loc = None
                    break
                elif l.startswith('## ') or l == '':
                    break
                j += 1
        # Function section
        elif line.startswith('**') and 'Maintainability Index' in line:
            fn_match = re.match(r'\*\*(.+)\*\*: Maintainability Index = ([\d.]+)', line)
            if fn_match:
                fn_name = fn_match.group(1)
                maintainability_index = float(fn_match.group(2))
                # Next three lines: table header, divider, then values
                i += 3
                if i < len(lines):
                    vals = [v.strip() for v in lines[i].strip().strip('|').split('|')]
                    try:
                        loc = int(vals[0]) if vals[0] else None
                    except Exception:
                        loc = None
                    try:
                        halstead_volume = float(vals[1]) if len(vals) > 1 and vals[1] else None
                    except Exception:
                        halstead_volume = None
                    try:
                        cyclomatic_complexity = int(float(vals[2])) if len(vals) > 2 and vals[2] else None
                    except Exception:
                        cyclomatic_complexity = None
                else:
                    loc = None
                    halstead_volume = None
                    cyclomatic_complexity = None
                current_functions.append({
                    'function': fn_name,
                    'maintainability_index': maintainability_index,
                    'length': loc,
                    'halstead_volume': halstead_volume,
                    'cyclomatic_complexity': cyclomatic_complexity
                })
            i += 1
        else:
            i += 1
    # Save last file
    if current_file:
        ams_score = None
        if current_functions:
            ams_vals = [f['maintainability_index'] for f in current_functions if f.get('maintainability_index') is not None]
            if ams_vals:
                ams_score = sum(ams_vals) / len(ams_vals)
        churn_norm = dummy_normalize(churn)
        try:
            kc_norm = 1.0 - float(knowledge_score.replace('%',''))/100.0 if knowledge_score and '%' in knowledge_score else 0.0
        except Exception:
            kc_norm = 0.0
        file_risk = calculate_overall_risk(ams_score or 0, churn_norm, kc_norm)
        # Try to get file-level LOC for last file
        file_loc = None
        # Look for first function after this file header
        j = i
        while j < len(lines):
            l = lines[j].strip()
            if l.startswith('**') and 'Maintainability Index' in l:
                if j+3 < len(lines):
                    vals = [v.strip() for v in lines[j+3].strip().strip('|').split('|')]
                    try:
                        file_loc = int(vals[0]) if vals[0] else None
                    except Exception:
                        file_loc = None
                break
            elif l.startswith('## ') or l == '':
                break
            j += 1
        files.append({
            'file': current_file,
            'churn': churn,
            'knowledge_score': knowledge_score,
            'developer': developer,
            'file_risk': file_risk,
            'lines_of_code': file_loc,
            'functions': current_functions
        })
    return files

def main():
    records = parse_complexity_report(REPORT_PATH)
    # Patch the template so the file-level pill shows the file risk score on the right
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()
    # Replace the right-side label for file-level pills from 'File' to the file risk value
    def file_risk_right_side(match):
        return (f'{match.group(1)}' +
                '${fileObj.file_risk !== undefined ? fileObj.file_risk.toFixed(2) : "--"}' +
                match.group(2))
    import re as _re
    # Find the file-level pill right-side div
    template = _re.sub(
        r'(<div class="risk-score"[^>]*>)[Ff]ile(</div>)',
        file_risk_right_side,
        template
    )
    js_records = ",\n            ".join([
        json.dumps(rec, ensure_ascii=False) for rec in records
    ])
    html_out = template.replace("||DATA||", js_records)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(os.getcwd(), f"generated_dashboard_{ts}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Dashboard written to: {out_path}")

if __name__ == "__main__":
    main()
