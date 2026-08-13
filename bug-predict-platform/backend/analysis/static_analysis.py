import subprocess, json, tempfile, os
from state import SecurityIssue

def run_bandit_on_file(file_path, content):
    issues = []
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = subprocess.run(["bandit", "-f", "json", tmp_path], capture_output=True, text=True)
        data = json.loads(result.stdout or "{}")
        for r in data.get("results", []):
            issues.append(SecurityIssue(
                file_path=file_path,
                line=r["line_number"],
                severity=r["issue_severity"],
                issue=r["issue_text"],
                recommendation=f"{r.get('test_id')} — confidence {r.get('issue_confidence')}",
                source="bandit"
            ))
    finally:
        os.unlink(tmp_path)
    return issues