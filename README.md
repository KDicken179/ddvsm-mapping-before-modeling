# Mapping Before Modeling: Decision Data Value Stream Map (DDVSM)

Replication materials for:

> Dickenson, K. S. (2026). *Mapping before modeling: A decision data value stream method for specifying AI-ready data in manufacturing supply chains.* Manuscript submitted for publication.

The Decision Data Value Stream Map integrates value stream mapping with a decision, question, variable, and data-source cascade at each process step. It produces an a priori data specification for a supervised learning task, audits a candidate dataset for coverage gaps and post-outcome fields, applies prediction-time validity and intervention-usefulness tests, and serves as a pre-modeling readiness gate. This repository reproduces the two public-data demonstrations reported in the paper.

## Contents

| Path | Purpose |
|---|---|
| `src/case_a_ecommerce.py` | Case A (e-commerce shipping): model comparison (Table 5), robustness check without post-delivery fields, threshold analysis, information-gap analysis (Figure 2) |
| `src/case_b_dataco.py` | Case B (DataCo): population rule, three feature sets (Table 6), ablation (Table 7), importance, intervention-usefulness test |
| `src/make_figures.py` | Builds Figures 2 and 4 from saved results |
| `maps/` | HTML sources for the value stream map figures (Figures 1 and 3) and a renderer |
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
python src/make_figures.py    --case-a results/case_a --case-b results/case_b --out figures
```

Case B trains neural networks on about 140,000 rows and takes several minutes; add `--skip-ann` for a faster run of the gradient boosted models only. Random seeds are fixed at 42. Results in the manuscript were produced with Python 3.13, pandas 3.0, NumPy 2.5, scikit-learn 1.9, and matplotlib 3.11; small numerical differences can occur with other library versions.

To re-render the map figures (optional), install Node.js and Playwright, then run `node maps/render_maps.js`.

## Key design choices

- **Case A** excludes `Gender` (no operational meaning). The main results retain the dataset as supplied; a robustness run removes `Customer_rating` and `Customer_care_calls`, which the map flags as likely recorded during or after delivery.
- **Case B** removes canceled shipments (no delivery outcome), uses a chronological split (train before 2017-04-22, test after), defines the prediction point as order release, and derives workload variables from prior orders only. The naive feature set deliberately includes post-outcome fields to show the leakage the map detects.

## License and citation

Code is released under the MIT License (see `LICENSE`). Please cite the article and this repository (see `CITATION.cff`). The datasets remain subject to their original licenses.
