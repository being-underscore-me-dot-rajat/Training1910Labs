"""Stage 2: aggregate member postings to one row per employer per month."""
from pathlib import Path

import pandas as pd

from common import load_params

params = load_params()["transform"]

df = pd.read_parquet("data/interim/valid.parquet")

# Total contribution = employee share + employer share.
df["total_tzs"] = df["employee_share_tzs"] + df["employer_share_tzs"]

# Drop postings below the minimum set in params.yaml.
rows_before = len(df)
df = df[df["total_tzs"] >= params["min_contribution_tzs"]]
print("min_contribution_tzs =", params["min_contribution_tzs"], "removed", rows_before - len(df), "postings")

# 1 for an arrears posting, 0 otherwise.
df["is_arrears"] = (df["entry_type"] == "ARREARS").astype(int)

# One row per employer per month.
employer_month = df.groupby(["employer_no", "period"], as_index=False).agg(
    members_posted=("member_no", "count"),
    wages_tzs=("gross_wage_tzs", "sum"),
    contributions_tzs=("total_tzs", "sum"),
    arrears_share=("is_arrears", "mean"),
)

Path("data/processed").mkdir(parents=True, exist_ok=True)
employer_month.to_parquet("data/processed/employer_month.parquet", index=False)
print("wrote", len(employer_month), "employer-months")
