from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
import joblib, numpy as np, os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "bug_risk_model.pkl")
_model = None

def _load_model():
    global _model
    if _model is None and os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
    return _model

def extract_metrics(file_path, content):
    try:
        raw = analyze(content)
        complexities = cc_visit(content)
        avg_cc = sum(c.complexity for c in complexities) / len(complexities) if complexities else 0
        max_cc = max((c.complexity for c in complexities), default=0)
        mi = mi_visit(content, True)
        return {
            "loc": raw.loc,
            "avg_complexity": avg_cc,
            "max_complexity": max_cc,
            "maintainability_index": mi,
            "comment_ratio": raw.comments / raw.loc if raw.loc else 0,
        }
    except Exception:
        return None

def predict_bug_risk(m):
    model = _load_model()
    if model:
        X = np.array([[m["loc"], m["avg_complexity"], m["max_complexity"], m["maintainability_index"], m["comment_ratio"]]])
        return float(model.predict_proba(X)[0][1])
    # heuristic fallback — used until a trained model exists
    score = 0.0
    if m["max_complexity"] > 10: score += 0.3
    if m["maintainability_index"] < 65: score += 0.3
    if m["comment_ratio"] < 0.05: score += 0.2
    if m["loc"] > 300: score += 0.2
    return min(score, 1.0)

def risk_label(score):
    return "high" if score >= 0.66 else "medium" if score >= 0.33 else "low"