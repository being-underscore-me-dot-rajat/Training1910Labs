# contributions-pipeline

A versioned pipeline that turns raw member contribution postings into employer features and a simple
"falls behind on payments" model.

```
data/raw/member_contributions ─► validate ─► transform ─► features ─► train
                                    │                                  │
                          reports/validation.json            reports/metrics.json
```

- Code: `src/`, versioned with Git
- Settings: `params.yaml`, versioned with Git
- Pipeline definition: `dvc.yaml`; exact versions of every input and output: `dvc.lock`
- Data and models: versioned with DVC, stored in the DVC cache and remote, never in Git

## Run it

```bash
python -m pip install -r ../requirements.txt
dvc pull          # get the data this commit expects (if a remote is set up)
dvc repro         # rerun whatever is out of date
dvc metrics show
```

See `../Lab3_DVC_Pipeline_Guide.md` for the full walkthrough.
