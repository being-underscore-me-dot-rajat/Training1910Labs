"""Stage 3: build one row per employer with features up to the cutoff and a label for the next months.

Label: 1 if, in the `horizon_months` after the cutoff, the employer has any arrears postings or any month
with no postings at all. In plain words: "will this employer fall behind soon?"
"""
from pathlib import Path

import numpy as np
import pandas as pd

from common import load_params

params = load_params()["features"]

em = pd.read_parquet("data/processed/employer_month.parquet")

# Turn "2025-06" into a month number (year * 12 + month), so months can be added and subtracted.
em["month"] = em["period"].str[:4].astype(int) * 12 + em["period"].str[5:7].astype(int)

cutoff_text = params["cutoff_period"]
cutoff = int(cutoff_text[:4]) * 12 + int(cutoff_text[5:7])
history_start = cutoff - params["history_months"] + 1     # first month the features look at
horizon_end = cutoff + params["horizon_months"]           # last month the label looks at

# History = the months up to the cutoff; future = the months after it.
history = em[(em["month"] >= history_start) & (em["month"] <= cutoff)]
history = history.sort_values(["employer_no", "month"])
future = em[(em["month"] > cutoff) & (em["month"] <= horizon_end)]

# Only employers that posted in the cutoff month can be scored.
active_employers = history.loc[history["month"] == cutoff, "employer_no"].unique()
history = history[history["employer_no"].isin(active_employers)]

# ---- Features: one row per employer ----
by_employer = history.groupby("employer_no")
features = pd.DataFrame()
features["months_posted"] = by_employer["month"].nunique()
features["avg_members"] = by_employer["members_posted"].mean()
features["log_avg_contribution"] = np.log1p(by_employer["contributions_tzs"].mean())
features["contribution_per_member"] = by_employer["contributions_tzs"].sum() / by_employer["members_posted"].sum()
features["arrears_share"] = by_employer["arrears_share"].mean()

last_3_months = history[history["month"] > cutoff - 3]
features["arrears_share_last3"] = last_3_months.groupby("employer_no")["arrears_share"].mean()

# Change in headcount from the first month to the last month of the history (0.1 = +10%).
features["members_change"] = by_employer["members_posted"].last() / by_employer["members_posted"].first() - 1

features["months_missing"] = params["history_months"] - features["months_posted"]

# Optional feature, switched on in params.yaml for version 2 of the lab.
if params["add_growth_3m"]:
    previous_3_months = history[(history["month"] <= cutoff - 3) & (history["month"] > cutoff - 6)]
    last3_avg = last_3_months.groupby("employer_no")["contributions_tzs"].mean()
    prev3_avg = previous_3_months.groupby("employer_no")["contributions_tzs"].mean()
    features["growth_3m"] = (last3_avg / prev3_avg - 1).clip(-1, 5)
    print("added growth_3m feature")

# ---- Label: did the employer fall behind in the following months? ----
future = future[future["employer_no"].isin(active_employers)]
by_employer_future = future.groupby("employer_no")
had_arrears = by_employer_future["arrears_share"].max() > 0
missed_a_month = by_employer_future["month"].nunique() < params["horizon_months"]
fell_behind = had_arrears | missed_a_month

# Employers with no postings at all after the cutoff aren't in `fell_behind`; they fell behind too.
fell_behind = fell_behind.reindex(features.index, fill_value=True)
features["label_falls_behind"] = fell_behind.astype(int)

features = features.fillna(0).reset_index()

Path("data/processed").mkdir(parents=True, exist_ok=True)
features.to_parquet("data/processed/employer_features.parquet", index=False)
n_features = features.shape[1] - 2       # every column except employer_no and the label
label_rate = 100 * features["label_falls_behind"].mean()
print(f"wrote {len(features)} employers, {n_features} features, label rate {label_rate:.1f}%")
