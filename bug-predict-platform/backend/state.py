from pydantic import BaseModel
from typing import List, Dict, Optional

class FileMetrics(BaseModel):
    file_path: str
    loc: int
    cyclomatic_complexity: float
    maintainability_index: float
    bug_risk_score: float
    bug_risk_label: str
    

class SecurityIssue(BaseModel):
    file_path: str
    line: int
    severity: str
    issue: str
    recommendation: str
    source: str = "bandit"  # "bandit" or "semgrep"

class ScanState(BaseModel):
    owner: str
    repo: str
    branch: str = "main"
    file_contents: Dict[str, str] = {}
    file_metrics: List[FileMetrics] = []
    security_issues: List[SecurityIssue] = []
    llm_review_notes: List[str] = []
    overall_quality_score: float = 0.0
    decision: str = "pending"          # pending | approved | rejected | fix_suggested
    fix_branch: Optional[str] = None
    fix_diffs: List[dict] = []
    skipped_files: List[dict] = []