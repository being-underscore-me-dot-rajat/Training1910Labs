"""Stage 4: train a simple model that ranks employers by risk of falling behind, and record metrics."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from common import load_params, write_json

params = load_params()
train_params = params["train"]

df = pd.read_parquet("data/processed/employer_features.parquet")

# Every column except the ID and the label is a feature.
features = df.columns.drop(["employer_no", "label_falls_behind"]).tolist()
X = df[features]
y = df["label_falls_behind"]

# 70% to train, 30% to test, with the same share of "falls behind" in both.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=params["seed"], stratify=y
)

# Scale the features, then logistic regression.
model = Pipeline([
    ("scale", StandardScaler()),
    ("model", LogisticRegression(C=train_params["C"], max_iter=2000, class_weight="balanced")),
])
model.fit(X_train, y_train)
risk_scores = model.predict_proba(X_test)[:, 1]

# The compliance team can follow up the top `review_capacity` share of employers.
ranked = pd.DataFrame({"label": y_test.to_numpy(), "score": risk_scores})
ranked = ranked.sort_values("score", ascending=False)
n_review = max(1, round(train_params["review_capacity"] * len(ranked)))
reviewed = ranked.head(n_review)

metrics = {
    "n_features": len(features),
    "roc_auc": round(float(roc_auc_score(y_test, risk_scores)), 4),
    "pr_auc": round(float(average_precision_score(y_test, risk_scores)), 4),
    "precision_at_capacity": round(float(reviewed["label"].mean()), 4),
    "recall_at_capacity": round(float(reviewed["label"].sum() / ranked["label"].sum()), 4),
}

# Save the model together with its feature list, and the metrics for DVC.
Path("models").mkdir(exist_ok=True)
joblib.dump({"model": model, "features": features}, "models/arrears_model.joblib")
write_json(metrics, "reports/metrics.json")
print("metrics:", metrics)
