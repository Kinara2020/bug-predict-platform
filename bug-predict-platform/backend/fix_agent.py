import os
from github import Github, Auth
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")

FIX_PROMPT = """You are a precise code repair agent. Fix ONLY the described issue — do not rewrite unrelated code, do not change function signatures unless required, and preserve existing logic wherever possible.

Return ONLY the corrected full file content. No explanation, no markdown fences, no commentary.

Issue: {issue}
File: {file_path}
Current code:
{code}
"""

VERIFY_PROMPT = """You are a code reviewer. Compare the ORIGINAL and FIXED versions of this file.
Answer with exactly one word: SAFE or UNSAFE.
SAFE means: the fix addresses the issue without breaking unrelated functionality or introducing new syntax errors.
UNSAFE means: the fix looks incomplete, removes unrelated code, or introduces obvious syntax problems.

ORIGINAL:
{original}

FIXED:
{fixed}
"""

def generate_fix(file_path, content, issue_description):
    prompt = FIX_PROMPT.format(issue=issue_description, file_path=file_path, code=content[:6000])
    resp = model.generate_content(prompt)
    fixed = resp.text.strip()
    if fixed.startswith("```"):
        parts = fixed.split("```")
        fixed = parts[1]
        first_line, _, rest = fixed.partition("\n")
        if first_line.strip().lower() in ("python", "javascript", "js", "java", "jsx"):
            fixed = rest
    return fixed.strip()

def verify_fix(original, fixed):
    prompt = VERIFY_PROMPT.format(original=original[:3000], fixed=fixed[:3000])
    resp = model.generate_content(prompt)
    verdict = resp.text.strip().upper()
    return "SAFE" in verdict

def create_fix_branch_and_commit(owner, repo_name, base_branch, files_to_fix):
    token = os.getenv("GITHUB_TOKEN")
    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(f"{owner}/{repo_name}")

    base_ref = repo.get_git_ref(f"heads/{base_branch}")
    base_sha = base_ref.object.sha

    branch_name = f"AI_FIX-{os.urandom(4).hex()}"
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)

    diffs = []
    skipped = []

    for f in files_to_fix:
        original = f["content"]
        fixed_code = generate_fix(f["file_path"], original, f["issue"])

        if not verify_fix(original, fixed_code):
            skipped.append({"file_path": f["file_path"], "reason": "Fix failed self-verification, skipped for safety"})
            continue

        existing = repo.get_contents(f["file_path"], ref=branch_name)
        repo.update_file(
            path=f["file_path"],
            message=f"fix: resolve issue in {f['file_path']}",
            content=fixed_code,
            sha=existing.sha,
            branch=branch_name,
        )
        diffs.append({
            "file_path": f["file_path"],
            "original": original[:2000],
            "fixed": fixed_code[:2000],
        })

    return branch_name, diffs, skipped