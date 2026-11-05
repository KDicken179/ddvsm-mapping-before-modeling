"""Computes the coverage measures reported in the manuscript from maps/variable_register.csv.

Record step is the process step at which a variable's value is created, taken from its source,
not from the map column where it is used. Master data and historical aggregates are available
from Step 1. Prediction points: Case A before carrier tender (after Step 3); Case B at order
release (after Step 2).

Usage: python src/register_counts.py
"""
import pandas as pd
from pathlib import Path

PREDICTION_POINT = {"A": 3, "B": 2}
reg = pd.read_csv(Path(__file__).parent.parent / "maps" / "variable_register.csv")
rows = []
for case, g in reg.groupby("case"):
    p = PREDICTION_POINT[case]
    pred = g[g.status != "post_outcome"]
    avail = pred[pred.status == "in_dataset"]
    valid = avail[pd.to_numeric(avail.record_step) <= p]
    t = pred[pred["class"] == "timing"]
    rows.append({"case": case, "prediction_point_after_step": p, "specified_predictors": len(pred),
                 "in_dataset": len(avail), "in_dataset_and_valid_at_prediction_point": len(valid),
                 "specification_coverage": round(len(valid) / len(pred), 3),
                 "timing_variables": len(t), "timing_in_dataset_and_valid": int(((t.status == "in_dataset") & (pd.to_numeric(t.record_step, errors="coerce") <= p)).sum()),
                 "timing_coverage": round(((t.status == "in_dataset") & (pd.to_numeric(t.record_step, errors="coerce") <= p)).sum() / len(t), 3),
                 "post_outcome_fields": int((g.status == "post_outcome").sum()),
                 "captured_elsewhere": int((pred.status == "captured_elsewhere").sum()), "not_captured": int((pred.status == "not_captured").sum())})
out = pd.DataFrame(rows)
out.to_csv(Path(__file__).parent.parent / "results" / "register_counts.csv", index=False)
print(out.T.to_string())
