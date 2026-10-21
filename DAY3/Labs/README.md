# Day 3 Labs: Neural Networks, Scale and Reproducibility

Today has three problems, and each needs a different tool:

1. **A modelling problem.** Can a neural network score claims better than yesterday's XGBoost? (PyTorch)
2. **A scale problem.** The member-level contribution history is millions of rows. How do you turn it into
   features without running out of memory? (Dask, with a look at Spark)
3. **A trust problem.** Six months from now, someone asks which data and which code produced the features
   behind a model. Can you answer, and can you rebuild them exactly? (DVC)

By the end of the day you'll have taken data all the way through the chain:

```
raw data (versioned) ─► large-scale processing ─► features ─► model ─► evaluation ─► reproducible again
```

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. A feed-forward network in PyTorch | `Lab1_Neural_Network_PyTorch.ipynb` | about 75 min |
| 2. Processing millions of contribution records | `Lab2_Large_Scale_Processing.ipynb` | about 60 min |
| 3. A versioned pipeline with DVC | `Lab3_DVC_Pipeline_Guide.md` + the `contributions-pipeline/` folder | about 75 min |

## Files in this folder

| File / folder | What it is |
|---|---|
| `claims_review_history.csv` | The same audited claims you used on Day 2 |
| `member_contributions/` | About 2.4 million member-level contribution postings for 2017-2025, stored as Parquet files split by year (`year=2017/`, `year=2018/`, ...) |
| `contributions_monthly_clean.csv` | Employer-level monthly remittances (the cleaned version of Day 1's table), for checking that the member-level data adds up |
| `employers.csv` | The employer register, cleaned |
| `contributions-pipeline/` | The starting project for Lab 3 |
| `requirements.txt` | Today's libraries |

## Setup

Open `Lab1_Neural_Network_PyTorch.ipynb` and run its first code cell. It finds the course environment you built on Day 1,
installs today's libraries into it, including PyTorch, and tells you if the notebook needs switching to the
**Python (fund-ai)** kernel. If it asks you to switch, do that and run the cell once more. You can run it as
often as you like; it only installs what's missing.

PyTorch is a large download. If your laptop has an NVIDIA GPU, the cell spots it and installs the GPU build
(about 2.5 GB) instead of the CPU one. Every lab today also runs fine on a CPU.

With conda:

```bash
conda install -c conda-forge pytorch dask pyarrow scikit-learn xgboost pyyaml -y
python -m pip install dvc
```

Check that everything imports:

```bash
python -c "import torch, dask, pyarrow, dvc; print('torch', torch.__version__, '| dask', dask.__version__)"
```
