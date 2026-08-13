import subprocess, json, tempfile, os
from state import SecurityIssue

def run_semgrep_on_file(file_path, content):
    issues = []
    ext = os.path.splitext(file_path)[1] or ".txt"
    with tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ["semgrep", "--config=p/security-audit", "--json", "--quiet", tmp_path],
            capture_output=True, text=True, timeout=25
        )
        data = json.loads(result.stdout or "{}")
        for r in data.get("results", []):
            issues.append(SecurityIssue(
                file_path=file_path,
                line=r["start"]["line"],
                severity=r["extra"]["severity"],
                issue=r["extra"]["message"],
                recommendation=r["check_id"],
                source="semgrep"
            ))
    except Exception:
        pass
    finally:
        os.unlink(tmp_path)
    return issues