import pandas as pd, joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Source a defect dataset with McCabe/Halstead-style metrics, e.g.
# search "NASA PROMISE defect dataset" (PC1/KC1/CM1) or Kaggle "software defect prediction"
df = pd.read_csv("defect_dataset.csv")
FEATURES = ["loc", "avg_complexity", "max_complexity", "maintainability_index", "comment_ratio"]
# rename dataset columns to match FEATURES first

X, y = df[FEATURES], df["defects"].astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

model = GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.05)
model.fit(X_train, y_train)
print(classification_report(y_test, model.predict(X_test)))
joblib.dump(model, "bug_risk_model.pkl")