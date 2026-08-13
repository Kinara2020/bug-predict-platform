def compute_overall_score(file_metrics, security_issues, llm_notes):
    if not file_metrics:
        return 0.0
    avg_risk = sum(f.bug_risk_score for f in file_metrics) / len(file_metrics)
    sec_penalty = min(len(security_issues) * 5, 40)
    score = 100 - (avg_risk * 40) - sec_penalty
    return round(max(score, 0), 1)