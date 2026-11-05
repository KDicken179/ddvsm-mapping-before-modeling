# Mapping Before Modeling: Decision Data Value Stream Map (DDVSM)

Replication materials for:

> Dickenson, K. S. (2026). *Mapping before modeling: A decision data value stream method for specifying AI-ready data in manufacturing supply chains.* Manuscript submitted for publication.

The Decision Data Value Stream Map integrates value stream mapping with a decision, question, variable, and data-source cascade at each process step. It produces an a priori data specification for a supervised learning task, audits a candidate dataset for coverage gaps and post-outcome fields, applies prediction-time validity and intervention-usefulness tests, and serves as a pre-modeling readiness gate. This repository reproduces the two public-data demonstrations reported in the paper.

## Contents

| Path | Purpose |
|---|---|
| `src/case_a_ecommerce.py` | Case A (e-commerce shipping): confirmation models, robustness check without post-delivery fields, threshold and information-gap analysis (Figure 3, panel A). Uses records with ID up to 8,999, the labeled subset of the public copy |
| `src/case_b_dataco.py` | Case B (DataCo): population rule, feature sets restricted to variables on the map, ablation, importance, intervention-usefulness test (Table 4) |
| `src/case_b_robustness.py` | Bootstrap 95% intervals for the nested feature sets and the First Class sensitivity check (Table 4) |
| `src/case_b_visibility.py` | Automated feature selection baseline (Table 5), temporal-window leakage and order-status proxy tests (Table 4) |
| `src/register_counts.py` | Computes coverage measures from `maps/variable_register.csv` |
| `src/make_figures.py` | Builds Figure 3 (confirmation) from saved results |
| `maps/` | HTML sources for the map figures (Figures 1 and 2), the variable register with record steps and classes, and a renderer |
| `docs/method_comparison_evidence.md` | Source evidence, with page references, for the method comparison (Tables 1 and 5) |
| `notebooks/case_a_ann_walkthrough.ipynb` | Step-by-step notebook for the Case A neural network |
| `results/` | Outputs produced for the manuscript |
| `figures/` | Submission figures (vector PDF and high-resolution PNG) |
| `data/` | Download instructions; data are not redistributed |

## Reproducing the results

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Place the two datasets in data/ (see data/README.md), then:
python src/case_a_ecommerce.py --data data/Train.csv --out results/case_a
python src/case_b_dataco.py   --data data/DataCoSupplyChainDataset.csv --out results/case_b
python src/case_b_robustness.py --data data/DataCoSupplyChainDataset.csv --out results/case_b
python src/case_b_visibility.py --data data/DataCoSupplyChainDataset.csv --out results/case_b
python src/register_counts.py
python src/make_figures.py    --case-a results/case_a --case-b results/case_b --out figures
```

Case B trains neural networks on about 140,000 rows and takes several minutes; add `--skip-ann` for a faster run of the gradient boosted models only. Random seeds are fixed at 42. Results in the manuscript were produced with Python 3.13, pandas 3.0, NumPy 2.5, scikit-learn 1.9, and matplotlib 3.11; small numerical differences can occur with other library versions.

To re-render the map figures (optional), install Node.js and Playwright, then run `node maps/render_maps.js`.

## Key design choices

- **Case A** excludes `Gender` (no operational meaning). The main results retain the dataset as supplied; a robustness run removes `Customer_rating` and `Customer_care_calls`, which the map flags as likely recorded during or after delivery.
- **Record steps.** Each variable's record step is the process step at which its value is created, taken from its source rather than from the map column where it is used. Master data and historical aggregates are available from Step 1. Prediction points are before carrier tender for Case A and order release for Case B.
- **Case B** removes canceled and suspected-fraud lines (no delivery outcome), uses a chronological split (train before 2017-04-22, test after), restricts feature sets to variables on the map, and derives workload variables from prior orders only. The naive feature set deliberately includes post-outcome fields to show the leakage the map detects. Every First Class line is late; a sensitivity run excludes First Class.

## Version history

- **v1.1** (revision): feature sets restricted to the map; variable register with record steps; record-step and timing badges on the maps; bootstrap intervals; First Class sensitivity; feature-selection, temporal-window and order-status tests; method-comparison evidence.
- **v1.0**: initial release.

## License and citation

Code is released under the MIT License (see `LICENSE`). Please cite the article and this repository (see `CITATION.cff`). The datasets remain subject to their original licenses.
