from langgraph.graph import StateGraph, END
from state import ScanState, FileMetrics
from github_utils import get_repo_files
from analysis.static_analysis import run_bandit_on_file
from analysis.ml_bug_predictor import extract_metrics, predict_bug_risk, risk_label
from analysis.llm_review import review_file
from analysis.quality_score import compute_overall_score

def fetch_files_node(state: ScanState):
    state.file_contents = get_repo_files(state.owner, state.repo, state.branch)
    return state

def analyze_code_node(state: ScanState):
    metrics, sec_issues = [], []
    for path, content in state.file_contents.items():
        m = extract_metrics(path, content)
        if not m:
            continue
        score = predict_bug_risk(m)
        metrics.append(FileMetrics(
            file_path=path, loc=m["loc"], cyclomatic_complexity=m["avg_complexity"],
            maintainability_index=m["maintainability_index"],
            bug_risk_score=score, bug_risk_label=risk_label(score)
        ))
        if path.endswith(".py"):
            sec_issues += run_bandit_on_file(path, content)
    state.file_metrics = metrics
    state.security_issues = sec_issues
    return state

def llm_review_node(state: ScanState):
    risky = sorted(state.file_metrics, key=lambda f: -f.bug_risk_score)[:5]
    state.llm_review_notes = [review_file(f.file_path, state.file_contents[f.file_path]) for f in risky]
    return state

def score_node(state: ScanState):
    state.overall_quality_score = compute_overall_score(state.file_metrics, state.security_issues, state.llm_review_notes)
    return state

builder = StateGraph(ScanState)
builder.add_node("fetch_files", fetch_files_node)
builder.add_node("analyze_code", analyze_code_node)
builder.add_node("llm_review", llm_review_node)
builder.add_node("score", score_node)
builder.set_entry_point("fetch_files")
builder.add_edge("fetch_files", "analyze_code")
builder.add_edge("analyze_code", "llm_review")
builder.add_edge("llm_review", "score")
builder.add_edge("score", END)

workflow = builder.compile()