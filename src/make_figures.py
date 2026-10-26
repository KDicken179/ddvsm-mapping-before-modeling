"""Builds Figure 2 (information gap, Case A) and Figure 4 (AUC by feature set, Case B) from saved results.

Usage:
    python src/make_figures.py --case-a results/case_a --case-b results/case_b --out figures
Red is used consistently to mark a deficiency or an invalid result.
"""
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

RED, DARK, LIGHT = "#c0392b", "#4d4d4d", "#9a9a9a"
plt.rcParams.update({"font.family": "serif", "font.size": 10.5, "pdf.fonttype": 42})


def figure2(gap, out):
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3), gridspec_kw={"width_ratios": [1.25, 1]})
    segs = [("Discount > 10\n(artificial rule)", gap["caught_hi"], gap["missed_hi"]), ("Discount ≤ 10\n(operational zone)", gap["caught_lo"], gap["missed_lo"])]
    for i, (_, c, m) in enumerate(segs):
        a.barh(i, c, color=DARK, height=0.6); a.barh(i, m, left=c, color=RED, height=0.6)
        a.text(c / 2, i, f"{c}", ha="center", va="center", color="white", fontsize=9.5)
        if m > 20:
            a.text(c + m / 2, i, f"{m}", ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
        else:
            a.text(c + m + 12, i, f"{m} missed", ha="left", va="center", fontsize=9)
    a.text(gap["late_lo"] + 15, 1, f"{gap['missed_lo']/gap['missed']*100:.1f}% of\nall misses", ha="left", va="center", fontsize=9, color=RED, fontweight="bold")
    a.set_yticks([0, 1]); a.set_yticklabels([s[0] for s in segs]); a.invert_yaxis(); a.set_xlim(0, 1000)
    a.set_xlabel("Late shipments in test set"); a.set_title("A. Where the missed late shipments fall", fontsize=10.5, loc="left")
    a.legend(handles=[Patch(color=DARK, label="Caught"), Patch(color=RED, label="Missed")], frameon=False, fontsize=9, loc="lower right", bbox_to_anchor=(1.0, 0.52))
    a.spines[["top", "right"]].set_visible(False)
    cls = [("Order and product\nattributes", 6, 6), ("Timing and queue\nvariables", 0, 10), ("Capacity and carrier\nperformance", 0, 6)]  # from the Case A map
    for i, (_, av, tot) in enumerate(cls):
        b.barh(i, tot, color="#e6e6e6", edgecolor="#999999", height=0.6)
        if av:
            b.barh(i, av, color=DARK, height=0.6)
        b.text(tot + 0.3, i, f"{av} of {tot}", va="center", fontsize=9.5, fontweight="bold" if av == 0 else None, color=RED if av == 0 else "black")
    b.set_yticks(range(3)); b.set_yticklabels([c[0] for c in cls]); b.invert_yaxis(); b.set_xlim(0, 12.5)
    b.set_xlabel("Variables specified by the map"); b.set_title("B. What the dataset contains", fontsize=10.5, loc="left")
    b.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "Figure2_Information_Gap.pdf"); fig.savefig(out / "Figure2_Information_Gap.png", dpi=600)


def figure4(r, out):
    sets = ["S1 Commercial attributes", "S2 DDVSM specification", "S0 Naive (all fields)"]
    lab = ["Commercial attributes\n(like the e-commerce case)", "DDVSM specification\n(decision-window variables)", "Naive: all fields\n(includes post-outcome data)"]
    fig, ax = plt.subplots(figsize=(6.5, 3.4)); x = np.arange(3); w = 0.36
    for i, (m, c) in enumerate([("GBT", "#333333"), ("ANN", LIGHT)]):
        sub = r[r.Model == m]
        if sub.empty:
            continue
        v = [sub[sub["Feature set"] == s]["AUC"].iloc[0] for s in sets]
        for k, (xi, vi) in enumerate(zip(x + (i - 0.5) * w, v)):
            inval = k == 2
            ax.bar(xi, vi, w, color=c, edgecolor=RED if inval else c, linewidth=2.2 if inval else 0, hatch="//" if inval else None, label=m if k == 0 else None)
            ax.text(xi, vi + 0.012, f"{vi:.2f}", ha="center", fontsize=9, color=RED if inval else "black")
    ax.text(2, 1.06, "Invalid at decision time", ha="center", fontsize=8.5, color=RED)
    ax.axhline(0.5, color="#777", ls="--", lw=0.9); ax.text(2.62, 0.505, "chance", fontsize=8.5, color="#555", ha="right", va="bottom")
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=9); ax.set_ylim(0.4, 1.12); ax.set_ylabel("Test AUC (chronological holdout)")
    ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(out / "Figure4_DataCo_AUC.pdf"); fig.savefig(out / "Figure4_DataCo_AUC.png", dpi=600)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-a", default="results/case_a"); ap.add_argument("--case-b", default="results/case_b"); ap.add_argument("--out", default="figures")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    figure2(json.load(open(Path(a.case_a) / "gap.json")), out)
    figure4(pd.read_csv(Path(a.case_b) / "results.csv"), out)
    print("figures written to", out)
