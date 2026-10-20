# Day 1 Labs: Getting Your Footing

Today you set up the workspace you'll use for the rest of the course, get to know the Fund's data, and
build your first repeatable pipeline. Everything you do in the next nine days sits on top of this.

## The ten days, briefly

Over the course you'll play the part of a new member of the Fund's Data & AI team. Each day adds a piece:

| Day | What you build | Uses what you built on |
|---|---|---|
| 1 | A clean, profiled copy of the Fund's core data | - |
| 2 | A claims risk score and member/employer segments | Day 1's clean data |
| 3 | A neural network, a large-scale feature job, a versioned pipeline | Day 2's claims data |
| 4 | Forecasts of contribution inflows and benefit payouts | Day 1's contributions |
| 5 | A fraud and anomaly review queue for benefit payments | Day 2's ideas on thresholds and capacity |
| 6 | Sentiment, complaint routing and entity extraction on member feedback | - |
| 7 | A shortlist of open-source LLMs you'd trust with Fund data | Day 6's feedback |
| 8 | An LLM fine-tuned on the member handbook | Day 7's shortlist |
| 9 | A handbook assistant (RAG) behind an internal API | Days 7 and 8 |
| 10 | One of the above, deployed, monitored and governed | Everything |

Every folder has its own copy of the data it needs, so if you miss a day you can still pick up the next one.

All the data is synthetic. It was generated to look and behave like a social security fund's records (the
Tanzanian mainland, TZS, 20% contributions, the usual benefit types), but no real member, employer or
payment is in it. You'll still treat it as if it were real, because that's the habit you want on real data.

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. Environment, Git and a shared workspace | `Lab1_Setup_Guide.md` | about 75 min |
| 2. Exploring the Fund's data | `Lab2_Exploring_the_Fund_Data.ipynb` | about 90 min |
| 3. Your first end-to-end pipeline | `Lab3_First_Pipeline.ipynb` | about 75 min |

Do them in order. Lab 1 gives you the environment the notebooks run in.

## Files in this folder

| File | What it is |
|---|---|
| `employers.csv` | About 1,400 registered employers: sector, region, registration and closure dates |
| `members.csv` | About 61,000 members who were on the books at some point from 2017 to 2025 |
| `contributions_monthly.csv` | One row per employer per month (about 128,000): members reported, wages, amount due, amount paid, dates |
| `claims.csv` | About 13,800 benefit claims lodged from 2017 to January 2026 |
| `requirements.txt`, `environment.yml` | Reference environment files. You'll build your own in Lab 1 and compare. |

The extract was taken on 31 January 2026. It's a raw extract, which means it has the problems raw extracts
usually have. Finding them is part of Lab 2.

## If you get stuck

- Read the error message from the bottom up. The last line usually says what went wrong.
- Check that the notebook is using the right kernel (top right in VS Code or Jupyter).
- Before asking the facilitator, write down in one sentence what you expected and what happened instead.
  Putting a problem into words fixes it surprisingly often.
