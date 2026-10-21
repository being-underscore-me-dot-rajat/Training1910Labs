"""Stage 1: validate raw member contributions and keep only valid rows."""
from pathlib import Path

import pandas as pd

from common import load_params, write_json

params = load_params()["validate"]

# Read every year of raw postings.
raw = pd.read_parquet("data/raw/member_contributions")
print("read", len(raw), "raw rows")

# Each rule is a True/False column: True means the row breaks the rule.
wage_not_positive = raw["gross_wage_tzs"] <= 0
wage_above_max = raw["gross_wage_tzs"] > params["max_wage_tzs"]
missing_employer = raw["employer_no"].isna()
missing_posted_date = raw["posted_date"].isna()

# A row is bad if it breaks any rule (| means "or").
bad = wage_not_positive | wage_above_max | missing_employer | missing_posted_date

# Keep the good rows, then drop exact duplicates.
good = raw[~bad]
valid = good.drop_duplicates()

# Save the valid rows.
Path("data/interim").mkdir(parents=True, exist_ok=True)
valid.to_parquet("data/interim/valid.parquet", index=False)

# A small report of what was removed, for DVC to track as a metric.
report = {
    "raw_rows": len(raw),
    "valid_rows": len(valid),
    "duplicates_removed": len(good) - len(valid),
    "wage_not_positive": int(wage_not_positive.sum()),
    "wage_above_max": int(wage_above_max.sum()),
    "missing_employer": int(missing_employer.sum()),
    "missing_posted_date": int(missing_posted_date.sum()),
}
write_json(report, "reports/validation.json")
print("kept", len(valid), "valid rows;", report)
