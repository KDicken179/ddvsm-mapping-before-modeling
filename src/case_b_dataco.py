"""Case B: DataCo Smart Supply Chain (Constante et al., 2019).

Reproduces Tables 6 and 7, Figure 4 inputs, the population rule, the
post-outcome audit, and the intervention-usefulness test.

Usage:
    python src/case_b_dataco.py --data data/DataCoSupplyChainDataset.csv --out results/case_b
"""
import argparse, json, time
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score, precision_score, f1_score
from sklearn.inspection import permutation_importance

SEED = 42
COMMERCIAL_NUM = ["Order Item Discount", "Order Item Discount Rate", "Order Item Product Price", "Order Item Quantity", "Sales",
                  "Order Item Total", "Order Item Profit Ratio", "Order Profit Per Order", "Benefit per order"]
COMMERCIAL_CAT = ["Type", "Category Name", "Department Name", "Customer Segment", "Market"]
TIMING = ["order_hour", "order_wday", "order_month", "load_24h", "load_7d", "region_load_7d"]
DDVSM_NUM = COMMERCIAL_NUM + ["Days for shipment (scheduled)", "lines_in_order"] + TIMING
DDVSM_CAT = COMMERCIAL_CAT + ["Shipping Mode", "Order Region", "Order Country", "Customer State", "lane"]
# Fields the DDVSM flags as recorded after the decision window or after the outcome
POST_OUTCOME_NUM = ["Days for shipping (real)", "ship_lag_days", "ship_wday", "Latitude", "Longitude"]
POST_OUTCOME_CAT = ["Order Status"]


def prepare(path):
    df = pd.read_csv(path, encoding="latin-1")
    n_raw = len(df)
    df["order_dt"] = pd.to_datetime(df["order date (DateOrders)"])
    df["ship_dt"] = pd.to_datetime(df["shipping date (DateOrders)"])
    canceled = df["Delivery Status"] == "Shipping canceled"          # population rule: no delivery outcome
    df = df[~canceled].copy()
    df["order_hour"] = df.order_dt.dt.hour; df["order_wday"] = df.order_dt.dt.dayofweek; df["order_month"] = df.order_dt.dt.month
    df["lines_in_order"] = df.groupby("Order Id")["Order Item Id"].transform("count")
    df["lane"] = df["Shipping Mode"] + " | " + df["Order Region"]
    df = df.sort_values("order_dt")
    s = pd.Series(1, index=df.order_dt)                                # workload proxies use prior orders only
    df["load_24h"] = s.rolling("24h").sum().values - 1
    df["load_7d"] = s.rolling("7D").sum().values - 1
    reg = [pd.Series(pd.Series(1, index=g.order_dt).rolling("7D").sum().values - 1, index=g.index) for _, g in df.groupby("Order Region")]
    df["region_load_7d"] = pd.concat(reg)
    df["ship_lag_days"] = (df.ship_dt - df.order_dt).dt.total_seconds() / 86400
    df["ship_wday"] = df.ship_dt.dt.dayofweek
    return df, n_raw, int(canceled.sum())


def pipe(num, cat, model):
    pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=20, sparse_output=False), cat),
                             ("n", StandardScaler(), num)])
    return Pipeline([("p", pre), ("m", model)])


def gbt():
    return HistGradientBoostingClassifier(max_iter=400, learning_rate=0.08, max_leaf_nodes=63, random_state=SEED)


def ann():
    return MLPClassifier(hidden_layer_sizes=(64, 32), alpha=1e-3, early_stopping=True, max_iter=200, random_state=SEED)


def score(y, p, **kw):
    yh = (p >= 0.5).astype(int)
    return dict(kw, AUC=roc_auc_score(y, p), Accuracy=accuracy_score(y, yh), Recall=recall_score(y, yh),
                Precision=precision_score(y, yh, zero_division=0), F1=f1_score(y, yh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--out", default="results/case_b")
    ap.add_argument("--skip-ann", action="store_true", help="skip the slower neural network runs")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    df, n_raw, n_cancel = prepare(a.data)
    y = df["Late_delivery_risk"].astype(int)
    cut = df.order_dt.quantile(0.8); tr, te = df.order_dt < cut, df.order_dt >= cut   # chronological split

    sets = {"S0 Naive (all fields)": (DDVSM_NUM + POST_OUTCOME_NUM, DDVSM_CAT + POST_OUTCOME_CAT),
            "S1 Commercial attributes": (COMMERCIAL_NUM, COMMERCIAL_CAT),
            "S2 DDVSM specification": (DDVSM_NUM, DDVSM_CAT)}
    base = DummyClassifier(strategy="most_frequent").fit(df[tr][["Sales"]], y[tr])
    rows = [score(y[te], base.predict_proba(df[te][["Sales"]])[:, 1], **{"Feature set": "Majority-class baseline", "Model": "None"})]
    rows[0]["AUC"] = 0.5
    fitted = {}
    for name, (num, cat) in sets.items():
        for mname, mk in [("GBT", gbt), ("ANN", ann)]:
            if mname == "ANN" and a.skip_ann:
                continue
            t0 = time.time()
            m = pipe(num, cat, mk()).fit(df[tr][num + cat], y[tr])
            rows.append(score(y[te], m.predict_proba(df[te][num + cat])[:, 1], **{"Feature set": name, "Model": mname}))
            fitted[(name, mname)] = m
            print(name, mname, round(rows[-1]["AUC"], 4), f"{time.time()-t0:.0f}s", flush=True)
    pd.DataFrame(rows).to_csv(out / "results.csv", index=False)

    # Ablation (Table 7)
    abl = {"Commercial + shipping mode and scheduled days": (COMMERCIAL_NUM + ["Days for shipment (scheduled)"], COMMERCIAL_CAT + ["Shipping Mode"]),
           "DDVSM spec without timing and workload variables": ([c for c in DDVSM_NUM if c not in TIMING], DDVSM_CAT),
           "Full DDVSM specification": (DDVSM_NUM, DDVSM_CAT)}
    ab = []
    for name, (num, cat) in abl.items():
        m = pipe(num, cat, gbt()).fit(df[tr][num + cat], y[tr])
        ab.append(score(y[te], m.predict_proba(df[te][num + cat])[:, 1], **{"Feature set": name}))
    pd.DataFrame(ab).to_csv(out / "ablation.csv", index=False)

    # Permutation importance for the DDVSM GBT model (sample of the test set)
    num, cat = sets["S2 DDVSM specification"]
    Xs = df[te][num + cat].sample(8000, random_state=1)
    pi = permutation_importance(fitted[("S2 DDVSM specification", "GBT")], Xs, y.loc[Xs.index], scoring="roc_auc", n_repeats=5, random_state=SEED)
    pd.Series(pi.importances_mean, index=Xs.columns).sort_values(ascending=False).to_csv(out / "importance.csv")

    # Intervention-usefulness test: lead time at order release is bounded by scheduled shipping days
    t = df[te]
    by_mode = t.groupby("Shipping Mode").agg(lines=("Late_delivery_risk", "size"), late_rate=("Late_delivery_risk", "mean"),
                                              scheduled_days=("Days for shipment (scheduled)", "first"))
    by_mode.to_csv(out / "intervention_by_mode.csv")
    no_window = t["Days for shipment (scheduled)"] < 1               # illustrative assumption: countermeasure needs >= 1 day

    info = {"n_raw": n_raw, "n_canceled_removed": n_cancel, "n_model": len(df), "late_rate": float(y.mean()),
            "n_train": int(tr.sum()), "n_test": int(te.sum()), "split_date": str(cut),
            "label_rule_match": float(((df["Days for shipping (real)"] > df["Days for shipment (scheduled)"]).astype(int) == y).mean()),
            "late_rate_morning": float(y[df.order_hour < 12].mean()), "late_rate_afternoon": float(y[df.order_hour >= 12].mean()),
            "test_lines_no_window": int(no_window.sum()), "test_late_no_window": int(t.loc[no_window, "Late_delivery_risk"].sum()),
            "test_late_total": int(t["Late_delivery_risk"].sum())}
    json.dump(info, open(out / "info.json", "w"), indent=1)
    print(pd.DataFrame(rows).round(3).to_string()); print(pd.DataFrame(ab).round(3).to_string()); print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
