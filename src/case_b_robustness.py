"""Case B robustness for the revised manuscript.

1. Bootstrap 95% intervals (1,000 test-set resamples) for test AUC of the three nested GBT feature sets
   and for the paired differences between them.
2. Sensitivity to the First Class artifact: every First Class line in the modeling population is late,
   so the nested sets are refit and scored with First Class lines removed from training and test.

Usage: python src/case_b_robustness.py --data data/DataCoSupplyChainDataset.csv --out results/case_b
"""
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
sys.path.insert(0, str(Path(__file__).parent))
from case_b_dataco import prepare, pipe, gbt, score, COMMERCIAL_NUM, COMMERCIAL_CAT, DDVSM_NUM, DDVSM_CAT, SEED

SETS = {"Commercial attributes": (COMMERCIAL_NUM, COMMERCIAL_CAT),
        "Commercial + shipping mode and scheduled days": (COMMERCIAL_NUM + ["Days for shipment (scheduled)"], COMMERCIAL_CAT + ["Shipping Mode"]),
        "Full DDVSM specification": (DDVSM_NUM, DDVSM_CAT)}


def fit_predict(df, tr, te, num, cat):
    m = pipe(num, cat, gbt()).fit(df[tr][num + cat], df.loc[tr, "Late_delivery_risk"].astype(int))
    return m.predict_proba(df[te][num + cat])[:, 1]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out", default="results/case_b")
    a = ap.parse_args(); out = Path(a.out)
    df, _, _ = prepare(a.data)
    cut = df.order_dt.quantile(0.8); tr, te = df.order_dt < cut, df.order_dt >= cut
    y = df.loc[te, "Late_delivery_risk"].astype(int).values
    preds = {k: fit_predict(df, tr, te, *v) for k, v in SETS.items()}
    rng = np.random.default_rng(SEED); n = len(y); B = 1000
    boots = {k: [] for k in preds}; d1, d2 = [], []
    for _ in range(B):
        i = rng.integers(0, n, n)
        if y[i].min() == y[i].max():
            continue
        a_ = {k: roc_auc_score(y[i], p[i]) for k, p in preds.items()}
        for k in a_: boots[k].append(a_[k])
        d1.append(a_["Commercial + shipping mode and scheduled days"] - a_["Commercial attributes"])
        d2.append(a_["Full DDVSM specification"] - a_["Commercial + shipping mode and scheduled days"])
    rows = [{"Quantity": f"AUC: {k}", "Estimate": roc_auc_score(y, p), "CI low": np.percentile(boots[k], 2.5), "CI high": np.percentile(boots[k], 97.5)} for k, p in preds.items()]
    rows.append({"Quantity": "Difference: + shipping mode and scheduled days", "Estimate": roc_auc_score(y, preds["Commercial + shipping mode and scheduled days"]) - roc_auc_score(y, preds["Commercial attributes"]), "CI low": np.percentile(d1, 2.5), "CI high": np.percentile(d1, 97.5)})
    rows.append({"Quantity": "Difference: + timing variables (full specification)", "Estimate": roc_auc_score(y, preds["Full DDVSM specification"]) - roc_auc_score(y, preds["Commercial + shipping mode and scheduled days"]), "CI low": np.percentile(d2, 2.5), "CI high": np.percentile(d2, 97.5)})
    pd.DataFrame(rows).to_csv(out / "bootstrap_auc.csv", index=False)
    # First Class sensitivity
    nf = df["Shipping Mode"] != "First Class"
    rows2 = []
    for k, (num, cat) in SETS.items():
        p = fit_predict(df, tr & nf, te & nf, num, cat)
        rows2.append(score(df.loc[te & nf, "Late_delivery_risk"].astype(int), p, **{"Feature set": k, "Population": "First Class lines excluded"}))
    pd.DataFrame(rows2).to_csv(out / "first_class_excluded.csv", index=False)
    print(pd.DataFrame(rows).round(4).to_string()); print(pd.DataFrame(rows2).round(4).to_string())


if __name__ == "__main__":
    main()
