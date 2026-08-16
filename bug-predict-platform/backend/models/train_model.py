import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score, roc_auc_score
import joblib
import os
import json

np.random.seed(42)
N = 2000

loc = np.random.exponential(80, N).clip(5, 800)
avg_complexity = np.random.gamma(2, 2, N).clip(1, 30)
max_complexity = avg_complexity + np.random.gamma(2, 3, N)
maintainability_index = (100 - (avg_complexity * 1.5) - (loc / 50) + np.random.normal(0, 8, N)).clip(0, 100)
comment_ratio = np.random.beta(2, 8, N)

# Defect probability increases with complexity/size, decreases with maintainability/comments
risk_score = (
    0.35 * (max_complexity / 30)
    + 0.25 * (loc / 800)
    + 0.25 * (1 - maintainability_index / 100)
    + 0.15 * (1 - comment_ratio)
)
defect_prob = 1 / (1 + np.exp(-8 * (risk_score - 0.5)))
defects = (np.random.rand(N) < defect_prob).astype(int)

df = pd.DataFrame({
    "loc": loc,
    "avg_complexity": avg_complexity,
    "max_complexity": max_complexity,
    "maintainability_index": maintainability_index,
    "comment_ratio": comment_ratio,
    "defects": defects,
})

FEATURES = ["loc", "avg_complexity", "max_complexity", "maintainability_index", "comment_ratio"]
X = df[FEATURES]
y = df["defects"]

print(f"Training on {len(X)} samples, {y.sum()} defective, {len(y)-y.sum()} clean")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

model = GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.05, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

print("\n=== MODEL EVALUATION ===")
print(f"Accuracy: {acc:.3f}")
print(f"F1 Score: {f1:.3f}")
print(f"AUC-ROC:  {auc:.3f}")
print(classification_report(y_test, y_pred))

os.makedirs(os.path.dirname(__file__), exist_ok=True)
joblib.dump(model, os.path.join(os.path.dirname(__file__), "bug_risk_model.pkl"))

metrics = {
    "accuracy": round(acc, 3), "f1_score": round(f1, 3), "auc_roc": round(auc, 3),
    "n_samples": len(X), "data_source": "modeled dataset based on known complexity-defect correlations"
}
with open(os.path.join(os.path.dirname(__file__), "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

print("\nSaved model to bug_risk_model.pkl")
print("Saved metrics to metrics.json")