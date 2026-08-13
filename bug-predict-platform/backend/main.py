from dotenv import load_dotenv
load_dotenv()

import os, hmac, hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from graph import workflow
from state import ScanState
from fix_agent import create_fix_branch_and_commit

app = FastAPI(title="AI Code Quality Platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SCAN_STORE: Dict[str, dict] = {}
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

class ScanRequest(BaseModel):
    owner: str
    repo: str
    branch: str = "main"

@app.post("/scan")
def scan_repo(req: ScanRequest):
    result = workflow.invoke(ScanState(owner=req.owner, repo=req.repo, branch=req.branch))
    SCAN_STORE[f"{req.owner}/{req.repo}"] = result
    return result

@app.get("/latest")
def get_latest(owner: str, repo: str):
    key = f"{owner}/{repo}"
    if key not in SCAN_STORE:
        raise HTTPException(status_code=404, detail="No scan yet — run /scan first")
    return SCAN_STORE[key]

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not WEBHOOK_SECRET:
        return True  # skip verification if no secret configured (dev only)
    if not signature_header:
        return False
    digest = hmac.new(WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest("sha256=" + digest, signature_header)

def run_scan_and_store(owner, repo, branch):
    result = workflow.invoke(ScanState(owner=owner, repo=repo, branch=branch))
    SCAN_STORE[f"{owner}/{repo}"] = result

@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Hub-Signature-256", "")):
        raise HTTPException(status_code=401, detail="Invalid signature")
    if request.headers.get("X-GitHub-Event") != "push":
        return {"status": "ignored"}
    payload = await request.json()
    owner = payload["repository"]["owner"].get("login") or payload["repository"]["owner"].get("name")
    repo = payload["repository"]["name"]
    branch = payload["ref"].split("/")[-1]
    background_tasks.add_task(run_scan_and_store, owner, repo, branch)
    return {"status": "scan queued", "owner": owner, "repo": repo, "branch": branch}

class FixFile(BaseModel):
    file_path: str
    issue: str

class DecisionRequest(BaseModel):
    owner: str
    repo: str
    branch: str = "main"
    decision: str  # "approve" | "reject" | "suggest_fix"
    files_to_fix: List[FixFile] = []

@app.post("/decision")
def make_decision(req: DecisionRequest):
    key = f"{req.owner}/{req.repo}"
    scan = SCAN_STORE.get(key)
    if not scan:
        raise HTTPException(status_code=404, detail="Run /scan first")

    if req.decision == "approve":
        scan["decision"] = "approved"
    elif req.decision == "reject":
        scan["decision"] = "rejected"
    elif req.decision == "suggest_fix":
        payload = [
            {"file_path": f.file_path, "content": scan["file_contents"].get(f.file_path, ""), "issue": f.issue}
            for f in req.files_to_fix
        ]
        branch = create_fix_branch_and_commit(req.owner, req.repo, req.branch, payload)
        scan["decision"] = "fix_suggested"
        scan["fix_branch"] = branch
    else:
        raise HTTPException(status_code=400, detail="invalid decision")

    SCAN_STORE[key] = scan
    return scan

@app.get("/health")
def health():
    return {"status": "ok"}