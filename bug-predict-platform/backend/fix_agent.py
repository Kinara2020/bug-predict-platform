import os
from github import Github, Auth
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

FIX_PROMPT = """You are a code repair agent. Fix the described issue in this file.
Return ONLY the corrected full file content. No explanation, no markdown fences.

Issue: {issue}
File: {file_path}
Current code:
{code}
"""

def generate_fix(file_path, content, issue_description):
    prompt = FIX_PROMPT.format(issue=issue_description, file_path=file_path, code=content[:6000])
    resp = model.generate_content(prompt)
    fixed = resp.text.strip()
    if fixed.startswith("```"):
        parts = fixed.split("```")
        fixed = parts[1]
        first_line, _, rest = fixed.partition("\n")
        if first_line.strip().lower() in ("python", "javascript", "js", "java"):
            fixed = rest
    return fixed.strip()

def create_fix_branch_and_commit(owner, repo_name, base_branch, files_to_fix):
    """files_to_fix: list of {file_path, content, issue}. Returns new branch name."""
    token = os.getenv("GITHUB_TOKEN")
    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(f"{owner}/{repo_name}")

    base_ref = repo.get_git_ref(f"heads/{base_branch}")
    base_sha = base_ref.object.sha

    branch_name = f"AI_FIX-{os.urandom(4).hex()}"
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)

    for f in files_to_fix:
        fixed_code = generate_fix(f["file_path"], f["content"], f["issue"])
        existing = repo.get_contents(f["file_path"], ref=branch_name)
        repo.update_file(
            path=f["file_path"],
            message=f"fix: resolve issue in {f['file_path']}",
            content=fixed_code,
            sha=existing.sha,
            branch=branch_name,
        )
    return branch_name