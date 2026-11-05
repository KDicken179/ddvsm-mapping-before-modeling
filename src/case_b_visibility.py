"""Case B additional analyses for the revised manuscript (repository release v1.1).

1. Data-driven baseline: rank every non-identifier field by mutual information with the
   label on the training period, as an automated feature selection procedure would,
   and record where the post-outcome fields fall in that ranking.
2. Subtle temporal leakage: replace the prior-only regional workload variable that the
   map specifies with versions whose 7-day window extends past the prediction point,
   and measure the change in test AUC.
3. Indirect proxy: Order Status is recorded at extract time and does not restate the
   label. Measure how much outcome information it carries on its own and when added
   to the DDVSM specification.

Uses the same population rule, chronological split and model as case_b_dataco.py.

Usage:
    python src/case_b_visibility.py --data data/DataCoSupplyChainDataset.csv --out results/case_b
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif

sys.path.insert(0, str(Path(__file__).parent))
from case_b_dataco import prepare, pipe, gbt, score, DDVSM_NUM, DDVSM_CAT, SEED

IDENTIFIERS = {"Order Id", "Order Item Id", "Order Customer Id", "Customer Id", "Product Card Id", "Order Item Cardprod Id",
               "Product Category Id", "Category Id", "Department Id", "Customer Email", "Customer Password", "Customer Fname",
               "Customer Lname", "Customer Street", "Customer Zipcode", "Order Zipcode", "Product Image", "Product Description",
               "Product Name", "Late_delivery_risk", "order_dt", "ship_dt",
               # raw timestamp strings are near-unique per order and inflate mutual information; their
               # decision-relevant content is carried by the derived timing variables and ship_lag_days
               "order date (DateOrders)", "shipping date (DateOrders)",
               # constructed in this repository rather than present in the extract
               "ship_lag_days", "ship_wday", "order_hour", "order_wday", "order_month", "load_24h", "load_7d", "region_load_7d", "lane", "lines_in_order"}
POST_OUTCOME = {"Days for shipping (real)", "shipping date (DateOrders)", "Delivery Status", "Order Status",
                "ship_lag_days", "ship_wday"}


def window_counts(times, before, after):
    """Count events in [t - before, t + after], excluding the event itself."""
    t = times.values.astype("datetime64[ns]").astype(np.int64)
    lo = np.searchsorted(t, t - before, side="left")
    hi = np.searchsorted(t, t + after, side="right")
    return hi - lo - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--out", default="results/case_b")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    df, _, _ = prepare(a.data)
    y = df["Late_delivery_risk"].astype(int)
    cut = df.order_dt.quantile(0.8); tr, te = df.order_dt < cut, df.order_dt >= cut

    # 1. Automated feature selection on all non-identifier fields (training period only)
    cand = [c for c in df.columns if c not in IDENTIFIERS]
    X = df.loc[tr, cand].copy()
    disc = []
    for c in cand:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype("category").cat.codes; disc.append(True)
        else:
            X[c] = pd.to_numeric(X[c], errors="coerce").fillna(0); disc.append(False)
    samp = X.sample(40000, random_state=SEED)
    mi = mutual_info_classif(samp, y.loc[samp.index], discrete_features=np.array(disc), random_state=SEED)
    rank = pd.DataFrame({"field": cand, "mutual_information": mi}).sort_values("mutual_information", ascending=False)
    rank["rank"] = range(1, len(rank) + 1)
    rank["post_outcome"] = rank.field.isin(POST_OUTCOME)
    rank.to_csv(out / "feature_selection_mi.csv", index=False)

    # 2. Temporal window leakage on the regional workload variable
    day = np.int64(86400 * 1e9)
    variants = {"Prior 7 days only (as specified)": None,
                "Centered 7-day window (3.5 days after)": (int(3.5 * day), int(3.5 * day)),
                "Following 7 days only": (0, 7 * day)}
    rows = []
    for name, win in variants.items():
        d = df.copy()
        if win is None:  # keep the variables exactly as specified in case_b_dataco.py
            m = pipe(DDVSM_NUM, DDVSM_CAT, gbt()).fit(d[tr][DDVSM_NUM + DDVSM_CAT], y[tr])
            rows.append(score(y[te], m.predict_proba(d[te][DDVSM_NUM + DDVSM_CAT])[:, 1], **{"Workload window": name}))
            continue
        b, f = win
        vals = pd.Series(index=d.index, dtype=float)
        for _, g in d.groupby("Order Region"):
            g = g.sort_values("order_dt")
            vals.loc[g.index] = window_counts(g.order_dt, b, f)
        d["region_load_7d"] = vals
        if f > 0:  # also move the company-wide load windows the same way
            d["load_7d"] = window_counts(d.order_dt, b, f)
        m = pipe(DDVSM_NUM, DDVSM_CAT, gbt()).fit(d[tr][DDVSM_NUM + DDVSM_CAT], y[tr])
        rows.append(score(y[te], m.predict_proba(d[te][DDVSM_NUM + DDVSM_CAT])[:, 1], **{"Workload window": name}))
        print(name, round(rows[-1]["AUC"], 4), flush=True)
    pd.DataFrame(rows).to_csv(out / "temporal_window_leakage.csv", index=False)

    # 3. Order Status as an indirect proxy
    prox = []
    m = pipe([], ["Order Status"], gbt()).fit(df[tr][["Order Status"]], y[tr])
    prox.append(score(y[te], m.predict_proba(df[te][["Order Status"]])[:, 1], **{"Feature set": "Order Status alone"}))
    m = pipe(DDVSM_NUM, DDVSM_CAT + ["Order Status"], gbt()).fit(df[tr][DDVSM_NUM + DDVSM_CAT + ["Order Status"]], y[tr])
    prox.append(score(y[te], m.predict_proba(df[te][DDVSM_NUM + DDVSM_CAT + ["Order Status"]])[:, 1], **{"Feature set": "DDVSM specification + Order Status"}))
    pd.DataFrame(prox).to_csv(out / "order_status_proxy.csv", index=False)
    ct = pd.crosstab(df["Order Status"], y, normalize="index").rename(columns={0: "on_time_share", 1: "late_share"})
    ct["lines"] = df["Order Status"].value_counts()
    ct.to_csv(out / "order_status_by_outcome.csv")

    # 3b. Cross-stage dependency: Order Status before the population rule is applied
    raw = pd.read_csv(a.data, encoding="latin-1")
    raw["order_dt"] = pd.to_datetime(raw["order date (DateOrders)"])
    yr = raw["Late_delivery_risk"].astype(int); cr = raw.order_dt.quantile(0.8)
    rtr, rte = raw.order_dt < cr, raw.order_dt >= cr
    m = pipe([], ["Order Status"], gbt()).fit(raw[rtr][["Order Status"]], yr[rtr])
    prox.append(score(yr[rte], m.predict_proba(raw[rte][["Order Status"]])[:, 1], **{"Feature set": "Order Status alone, canceled lines retained"}))
    pd.DataFrame(prox).to_csv(out / "order_status_proxy.csv", index=False)
    ctr = pd.crosstab(raw["Order Status"], yr, normalize="index").rename(columns={0: "on_time_share", 1: "late_share"})
    ctr["lines"] = raw["Order Status"].value_counts()
    ctr.to_csv(out / "order_status_by_outcome_all_lines.csv")
    print(ctr.round(3).to_string())

    print(rank.head(15).to_string()); print(pd.DataFrame(rows).round(4).to_string())
    print(pd.DataFrame(prox).round(4).to_string()); print(ct.round(3).to_string())


if __name__ == "__main__":
    main()
