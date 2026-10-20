# Day 2 Labs: Predict, Discover, Compare

Yesterday you cleaned the Fund's data. Today you put it to work on two kinds of question:

- **"What is likely to happen?"** Which newly lodged claims are most likely to turn out irregular, so the
  review team can check them before money goes out? (supervised learning)
- **"What groups exist?"** What kinds of members and employers does the Fund actually serve, and would
  they benefit from different treatment? (unsupervised learning)

Then you'll write one function that tests every model the same way, so you can compare them fairly, and you'll see how a model can look
excellent and still be useless.

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. Claims risk scoring | `Lab1_Claims_Risk_Scoring.ipynb` | about 75 min |
| 2. Member and employer segmentation | `Lab2_Member_Employer_Segmentation.ipynb` | about 60 min |
| 3. Comparing models fairly, and checking we can trust the winner | `Lab3_Comparing_and_Checking_Models.ipynb` | about 75 min |

Lab 3 builds on the models from Lab 1, but it retrains them itself, so it runs on its own too.

## Files in this folder

| File | What it is |
|---|---|
| `claims_review_history.csv` | About 7,800 paid claims from 2019-2025 that went through the post-payment audit, with the audit result (`irregular` = 1 means the audit found a problem: overpayment, ineligible claim, false documents or fraud) |
| `member_profile.csv` | 15,000 active members with contribution and service-contact behaviour over the last 24 months |
| `employer_profile.csv` | About 1,300 active employers with payment behaviour over the last 24 months |
| `requirements.txt` | Libraries used today, on top of Day 1 |

Two columns in `claims_review_history.csv` need a warning now, before you see them in the notebook:
`investigation_opened` and `amount_recovered_tzs`. Both are only filled in *after* the audit. Keep that in
mind. Lab 3 is about exactly this.

## Setup

Open `Lab1_Claims_Risk_Scoring.ipynb` and run its first code cell. It finds the course environment you built on Day 1,
installs today's libraries into it, and tells you if the notebook needs switching to the
**Python (fund-ai)** kernel. If it asks you to switch, do that and run the cell once more. You can run it as
often as you like; it only installs what's missing.

On macOS, if `import xgboost` fails, run `brew install libomp`.

## A note on language

In this data, `irregular = 1` means the audit found *something* wrong. Most of those cases are errors,
not crimes. Keep that in mind when you talk about the model. It produces a **risk score to prioritise
review**. It never decides that a member is a fraudster. A person looks at the claim and decides.
