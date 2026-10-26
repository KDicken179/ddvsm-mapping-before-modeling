"""Case A: e-commerce shipping (Kaggle "Customer Analytics", prachi13).

Reproduces Table 5, Figure 2, the robustness check, and the threshold analysis.

Usage:
    python src/case_a_ecommerce.py --data data/Train.csv --out results/case_a

The paper uses records with ID <= 8999 (the labeled subset of the public copy).
Use --max-id 0 to run on all records instead.
"""
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, precision_score, recall_score
from sklearn.inspection import permutation_importance

SEED = 42
CAT = ["Warehouse_block", "Mode_of_Shipment", "Product_importance"]
TARGET = "Reached.on.Time_Y.N"   # 1 = late in this dataset
POST_DELIVERY = ["Customer_rating", "Customer_care_calls"]   # flagged by the DDVSM timing audit


def load(path, max_id):
    df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig").drop_duplicates(subset="ID")
    if max_id:
        df = df[df["ID"] <= max_id]
    return df


def preprocessor(num):
    return ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT), ("num", StandardScaler(), num)])


def models(pre, mlp):
    return {
        "Majority-class baseline": Pipeline([("pre", pre), ("m", DummyClassifier(strategy="most_frequent"))]),
        "Logistic regression": Pipeline([("pre", pre), ("m", LogisticRegression(max_iter=2000))]),
        "Random forest": Pipeline([("pre", pre), ("m", RandomForestClassifier(n_estimators=400, min_samples_leaf=5, random_state=SEED, n_jobs=-1))]),
        "Gradient boosting": Pipeline([("pre", pre), ("m", HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300, random_state=SEED))]),
        "ANN (MLP)": mlp,
    }


def evaluate(X, y, label):
    num = [c for c in X.columns if c not in CAT]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=SEED)
    pre = preprocessor(num)
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    grid = GridSearchCV(Pipeline([("pre", pre), ("m", MLPClassifier(max_iter=600, early_stopping=True, validation_fraction=0.15,
                                                                      n_iter_no_change=25, random_state=SEED))]),
                        {"m__hidden_layer_sizes": [(16,), (32,), (32, 16), (64, 32)], "m__alpha": [1e-4, 1e-3, 1e-2]},
                        cv=cv, scoring="roc_auc", n_jobs=-1).fit(Xtr, ytr)
    rows, fitted = [], {}
    for name, m in models(pre, grid.best_estimator_).items():
        if name != "ANN (MLP)":
            m.fit(Xtr, ytr)
        cv_auc = 0.5 if name.startswith("Majority") else cross_val_score(m, Xtr, ytr, cv=cv, scoring="roc_auc").mean()
        p = m.predict_proba(Xte)[:, 1]; yh = (p >= 0.5).astype(int)
        rows.append({"Feature set": label, "Model": name, "CV AUC": cv_auc, "Test AUC": roc_auc_score(yte, p),
                     "Accuracy": accuracy_score(yte, yh), "Precision": precision_score(yte, yh, zero_division=0),
                     "Recall": recall_score(yte, yh), "F1": f1_score(yte, yh)})
        fitted[name] = (m, p)
    return pd.DataFrame(rows), fitted, (Xtr, Xte, ytr, yte), grid.best_params_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--out", default="results/case_a")
    ap.add_argument("--max-id", type=int, default=8999)
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    df = load(a.data, a.max_id)
    y = df[TARGET].astype(int)

    # Main analysis: dataset as supplied (Gender excluded as operationally meaningless)
    X = df.drop(columns=["ID", TARGET, "Gender"])
    res, fitted, (Xtr, Xte, ytr, yte), best = evaluate(X, y, "As supplied")
    res.to_csv(out / "results.csv", index=False)

    ann, p = fitted["ANN (MLP)"]
    pi = permutation_importance(ann, Xte, yte, scoring="roc_auc", n_repeats=20, random_state=SEED)
    pd.Series(pi.importances_mean, index=Xte.columns).sort_values(ascending=False).to_csv(out / "importance.csv")

    # Threshold analysis
    thr = []
    for t in [0.5, 0.4, 0.3]:
        f = p >= t
        thr.append({"threshold": t, "recall": float((f & (yte == 1)).sum() / (yte == 1).sum()), "flagged_share": float(f.mean())})
    pd.DataFrame(thr).to_csv(out / "thresholds.csv", index=False)

    # Gap analysis (Figure 2)
    yh = (p >= 0.5).astype(int); late = (yte == 1).values; hi = (Xte["Discount_offered"] > 10).values
    gap = {"late_total": int(late.sum()), "caught": int((late & (yh == 1)).sum()), "missed": int((late & (yh == 0)).sum()),
           "late_hi": int((late & hi).sum()), "caught_hi": int((late & hi & (yh == 1)).sum()), "missed_hi": int((late & hi & (yh == 0)).sum()),
           "late_lo": int((late & ~hi).sum()), "caught_lo": int((late & ~hi & (yh == 1)).sum()), "missed_lo": int((late & ~hi & (yh == 0)).sum()),
           "ontime_lo_flagged": int((~late & ~hi & (yh == 1)).sum()), "ontime_lo": int((~late & ~hi).sum())}
    json.dump(gap, open(out / "gap.json", "w"), indent=1)

    # Robustness: drop fields the DDVSM flags as likely post-delivery
    rob, _, _, _ = evaluate(X.drop(columns=POST_DELIVERY), y, "Without post-delivery fields")
    rob.to_csv(out / "robustness_without_post_delivery.csv", index=False)

    info = {"n": len(df), "late_rate": float(y.mean()), "ntrain": len(Xtr), "ntest": len(Xte), "mlp_best": {k: str(v) for k, v in best.items()},
            "late_rate_discount_gt10": float(y[df["Discount_offered"] > 10].mean()),
            "late_rate_discount_le10": float(y[df["Discount_offered"] <= 10].mean()),
            "share_discount_gt10": float((df["Discount_offered"] > 10).mean())}
    json.dump(info, open(out / "info.json", "w"), indent=1)
    print(res.round(3).to_string()); print(rob.round(3).to_string()); print(json.dumps(gap, indent=1))


if __name__ == "__main__":
    main()
