# Lab 3: A Versioned Pipeline with DVC

**Time:** about 75 minutes
**You'll finish with:** a pipeline where every output can be traced to the exact data, code and settings
that produced it, and rebuilt on demand, on your machine or a colleague's.

---

## Why this matters

Six months after a model goes live, someone from internal audit asks:

> *"The compliance list you sent in March: which data was it built from, which version of the code, with
> which settings? Can you produce it again, exactly?"*

Git can answer the code part. It can't answer the data part, because data doesn't belong in Git (Day 1).
**DVC** (Data Version Control) fills the gap. It stores data and models outside Git, and puts small
pointer files *into* Git that record exactly which version of each file goes with each commit.

```
Git  ─── code, params.yaml, dvc.yaml, dvc.lock, *.dvc pointer files   (small text files)
DVC  ─── raw data, intermediate files, features, models                (large files, in a cache/remote)
```

The pipeline you'll version is the same job as Lab 2, written as four scripts:

```
data/raw/member_contributions ──► validate ──► transform ──► features ──► train
                                     │                                     │
                           reports/validation.json               reports/metrics.json
```

It builds employer features and trains a simple model that ranks employers by their risk of falling behind
on payments in the next three months.

Open the `contributions-pipeline/` folder and have a quick look before you start:

| File | What it does |
|---|---|
| `src/validate.py` | Removes invalid and duplicate postings (Lab 2, Step 1) |
| `src/transform.py` | Aggregates to one row per employer-month |
| `src/features.py` | Builds employer features up to a cutoff month and the "falls behind" label |
| `src/train.py` | Trains a logistic regression and writes metrics |
| `params.yaml` | Every setting that changes an output |
| `dvc.yaml` | The pipeline: each stage's command, inputs, parameters and outputs |
| `.gitattributes` | Keeps line endings identical across Windows, macOS and Linux (more on this in Part 8) |

---

## Part 1: Set up the project

Copy `contributions-pipeline` to a working folder **outside OneDrive** (DVC keeps a cache of your data,
and you don't want that syncing), then initialise Git and DVC.

```powershell
# Windows
Copy-Item -Recurse contributions-pipeline C:\work\contributions-pipeline
cd C:\work\contributions-pipeline
```

```bash
# macOS / Linux
cp -r contributions-pipeline ~/work/contributions-pipeline
cd ~/work/contributions-pipeline
```

Then, on any system:

```bash
git init
dvc init
git status            # dvc init created .dvc/ and .dvcignore. Commit them.
git add .
git commit -m "Project skeleton: pipeline code and parameters"
```

Make sure your environment from the Day 3 setup is active. `dvc --version` should print a version number.

## Part 2: Put the raw data under version control

Copy the `member_contributions` folder from the Day 3 Labs folder into `data/raw/`:

```powershell
# Windows (adjust the source path to where your Day 3 folder is)
Copy-Item -Recurse <path to DAY3\Labs>\member_contributions data\raw\
```

```bash
# macOS / Linux
cp -r <path to DAY3/Labs>/member_contributions data/raw/
```

Now tell DVC to track it:

```bash
dvc add data/raw/member_contributions
```

Look at what that did:

```bash
git status
```

Two new small files:

- `data/raw/member_contributions.dvc`: the pointer. Open it. It holds an MD5 hash of the folder's
  contents, its size and the number of files. That hash *is* the version of the data.
- `data/raw/.gitignore`: tells Git to ignore the real data. DVC wrote it for you.

The actual data has been moved into DVC's cache (`.dvc/cache`) and linked back into place.

```bash
git add data/raw/member_contributions.dvc data/raw/.gitignore
git commit -m "Track raw member contributions with DVC"
```

From now on, this commit and this exact data belong together.

## Part 3: Run the pipeline

Open `dvc.yaml`. Each stage lists:

- `cmd`: the command to run,
- `deps`: the files it depends on (its own script and its input data),
- `params`: which parts of `params.yaml` it reads,
- `outs`: what it produces (tracked by DVC), and `metrics`, small JSON files you can compare between versions.

See the pipeline as a graph:

```bash
dvc dag
```

Now run it:

```bash
dvc repro
```

You'll see each stage run in order, and log lines like these:

```
kept 2420260 valid rows; {'raw_rows': 2423115, ..., 'duplicates_removed': 2499, ...}
wrote 123363 employer-months
wrote 1236 employers, 8 features, label rate 19.4%
metrics: {'n_features': 8, 'roc_auc': 0.9069, 'pr_auc': 0.7708, 'precision_at_capacity': 0.8378, ...}
```

Your numbers should match these exactly. The data, code and seed are the same, so the result is the same.

```bash
dvc metrics show
```

DVC created a new file, `dvc.lock`. Open it. For every stage it records the **hash of every input, every
parameter value and every output** from this run. `dvc.lock` is the answer to the auditor's question.

Commit this version and give it a name:

```bash
git add dvc.lock data/interim/.gitignore data/processed/.gitignore models/.gitignore reports/
git commit -m "Version 1: employer features and arrears model"
git tag v1
```

(`git status` will tell you exactly which `.gitignore` files DVC created. Add whatever it lists.)

## Part 4: DVC only reruns what changed

Run it again:

```bash
dvc repro
```

Nothing runs. Every stage says it didn't change and gets skipped. DVC compared the hashes in `dvc.lock` with
the files on disk and found nothing to do. On a pipeline that takes hours, that matters.

Now change only a training setting. In `params.yaml`, set `train: C:` to `0.1`, then:

```bash
dvc status        # what's out of date, and why?
dvc repro
```

Only `train` runs. `validate`, `transform` and `features` are skipped, because none of their inputs changed.
Put `C` back to `1.0` and run `dvc repro` once more. You're back at version 1, and DVC restores the version 1 model
from its cache without retraining anything.

## Part 5: Version 2

A colleague suggests two changes:

1. Ignore very small postings: set `transform: min_contribution_tzs:` to `100000` (that's any month where the
   member earned under TZS 500,000).
2. Add a three-month contribution growth feature: set `features: add_growth_3m:` to `true`.

Make both edits in `params.yaml`, then:

```bash
dvc status
dvc repro
```

This time `validate` is skipped (nothing it depends on changed), and the other three stages run.

Compare with version 1:

```bash
dvc params diff
dvc metrics diff
```

You should see something like:

```
Metric                 HEAD    workspace    Change
n_features             8       9            1
pr_auc                 0.7708  0.7119       -0.0589
precision_at_capacity  0.8378  0.7297       -0.1081
recall_at_capacity     0.4306  0.3803       -0.0503
roc_auc                0.9069  0.8916       -0.0153
```

Version 2 is **worse**. The extra feature adds nothing, and dropping small postings throws away exactly the
low-wage employers who are most likely to fall behind. That's a perfectly normal outcome of an
experiment. The point is that you can *see* it, in numbers, before anyone acts on it.

Commit it anyway. Failed experiments are worth keeping a record of:

```bash
git add -A
git commit -m "Version 2: min contribution 100,000 and 3-month growth (worse, see metrics)"
git tag v2
```

## Part 6: Answer the auditor

**Which data produced version 1's features?**

```bash
git show v1:data/raw/member_contributions.dvc
git show v1:dvc.lock
```

The first shows the raw data hash. The second shows, for every stage, the hashes of its inputs and outputs and
the parameter values used. If anyone ever doubts a result, compare these hashes against the files.

**What changed between the two versions?**

```bash
dvc diff v1 v2          # which data files changed
git diff v1 v2 -- params.yaml src/
```

## Part 7: Go back to version 1, exactly

Management decides version 1 was better. Restore it:

```bash
git checkout v1
dvc checkout
dvc status              # "Data and pipelines are up to date."
dvc metrics show        # version 1's numbers
```

`git checkout` brought back version 1's code, parameters and `dvc.lock`. `dvc checkout` then brought back the
matching data, features and model from the cache. Nothing was recomputed.

Return to the latest version when you're done:

```bash
git checkout main       # or master, depending on your Git setup
dvc checkout
```

## Part 8: Share it with a colleague

So far the data only lives in your machine's cache. A **remote** is shared storage where DVC keeps the data
for the whole team. It can be a network share, or an object store (S3, Azure Blob Storage, Google Cloud
Storage, or an on-premises MinIO server). For the lab, a folder will do.

```powershell
# Windows: a folder standing in for a network share such as \\fileserver\dvc-store
mkdir C:\work\dvc-storage
dvc remote add -d shared C:\work\dvc-storage
```

```bash
# macOS / Linux
mkdir -p ~/work/dvc-storage
dvc remote add -d shared ~/work/dvc-storage
```

```bash
git commit -am "Add shared DVC remote"
dvc push
```

Now play the colleague. Clone the repository somewhere else and fetch the data:

```bash
cd ..
git clone contributions-pipeline colleague-copy
cd colleague-copy
dvc pull
dvc status              # "Data and pipelines are up to date."
dvc metrics show
```

Your "colleague" has the same code, the same data, the same model and the same metrics, without copying a single
file by hand.

In a real team, the Git repository sits on your Git server (Day 1) and the remote is something everyone can
reach. Then the workflow is simply: `git pull` then `dvc pull`, and `git push` then `dvc push`.

**Why the `.gitattributes` file?** DVC identifies files by their hash. Windows uses different line endings
(CRLF) from macOS and Linux (LF), and by default Git converts them when you clone. That changes the bytes, so
the hashes change, and a colleague on Windows would see every script reported as "modified" even though
nothing changed. `.gitattributes` tells Git to keep LF everywhere. The scripts also write their JSON reports
with LF endings for the same reason. It's a small detail that saves a very confusing afternoon.

## Part 9: Your turn

Pick one or both:

1. **Add a stage.** Write `src/report.py`, which reads `data/processed/employer_features.parquet` and writes
   `reports/top_risk_employers.csv` (the 50 employers with the highest predicted risk, using the saved model).
   Add it to `dvc.yaml` with the right `deps` and `outs`, run `dvc repro`, and check that only your new stage runs.
2. **Change the cutoff.** Set `features: cutoff_period:` to `"2025-03"`. Which stages rerun? Does the model
   hold up on an earlier period?

## Before you finish

- [ ] `git log --oneline --decorate` shows your `v1` and `v2` tags
- [ ] `dvc metrics diff v1 v2` shows the difference between the versions
- [ ] You restored v1 with `git checkout v1` plus `dvc checkout` and got v1's metrics back
- [ ] The "colleague" clone reports `Data and pipelines are up to date` after `dvc pull`

## How this connects

- **Day 1:** you proved your *environment* could be rebuilt from a file. Today you proved the *data and
  results* can be rebuilt too.
- **Day 2:** the model card recorded what a model was trained on. `dvc.lock` makes that record precise and
  checkable.
- **Day 10:** MLflow will track experiments and models in a registry, and the deployment pipeline will retrain
  from exactly this kind of versioned pipeline.
