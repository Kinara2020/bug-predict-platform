import os
from github import Github, Auth
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

FIX_PROMPT = """You are a code repair agent. Fix the described issue in this file.
Return ONLY the corrected full file content. No explanation, no markdown fences.

Issue: {issue}
File: {file_path}
Current code:
{code}
"""

def generate_fix(file_path, content, issue_description):
    if not content:
        return ""
    prompt = FIX_PROMPT.format(
        issue=issue_description or "",
        file_path=file_path or "",
        code=content[:6000]
    )
    try:
        resp = model.generate_content(prompt)
        if not resp or not resp.text:
            return content
        fixed = resp.text.strip()
    except Exception:
        return content

    if fixed.startswith("```"):
        lines = fixed.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        fixed = "\n".join(lines)
    return fixed.strip()

def create_fix_branch_and_commit(owner, repo_name, base_branch, files_to_fix):
    """files_to_fix: list of {file_path, content, issue}. Returns new branch name."""
    if not files_to_fix:
        return None

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")

    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(f"{owner}/{repo_name}")

    base_ref = repo.get_git_ref(f"heads/{base_branch}")
    base_sha = base_ref.object.sha

    branch_name = f"AI_FIX-{os.urandom(4).hex()}"
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)

    for f in files_to_fix:
        file_path = f.get("file_path")
        content = f.get("content", "")
        issue = f.get("issue", "")
        if not file_path:
            continue

        fixed_code = generate_fix(file_path, content, issue)
        try:
            existing = repo.get_contents(file_path, ref=branch_name)
            sha = existing.sha if hasattr(existing, "sha") else (existing[0].sha if isinstance(existing, list) else None)
            if sha:
                repo.update_file(
                    path=file_path,
                    message=f"fix: resolve issue in {file_path}",
                    content=fixed_code,
                    sha=sha,
                    branch=branch_name,
                )
            else:
                repo.create_file(
                    path=file_path,
                    message=f"fix: resolve issue in {file_path}",
                    content=fixed_code,
                    branch=branch_name,
                )
        except Exception:
            repo.create_file(
                path=file_path,
                message=f"fix: resolve issue in {file_path}",
                content=fixed_code,
                branch=branch_name,
            )
    return branch_name