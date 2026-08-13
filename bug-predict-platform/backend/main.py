from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import workflow
from state import ScanState

app = FastAPI(title="AI Code Quality Platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ScanRequest(BaseModel):
    owner: str
    repo: str
    branch: str = "main"

@app.post("/scan")
def scan_repo(req: ScanRequest):
    return workflow.invoke(ScanState(owner=req.owner, repo=req.repo, branch=req.branch))

@app.get("/health")
def health():
    return {"status": "ok"}