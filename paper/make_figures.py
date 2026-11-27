"""Draws the paper's figures at IEEE column width from the result tables. Run from this folder."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "full_qwen3-14b_v3")
OUT = os.path.dirname(os.path.abspath(__file__))
t = lambda n: pd.read_csv(os.path.join(D, f"table_{n}.csv"))
plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8, "axes.linewidth": 0.6,
                     "pdf.fonttype": 42})
COL = {"think": "#1f5fae", "nothink": "#d9541e"}
LAB = {"think": "Thinking on", "nothink": "Thinking off"}
MK = {"think": "o", "nothink": "s"}
OFF = {"think": -0.13, "nothink": 0.13}


def dot(ax, x, r, n, m, label=None):
    ax.plot([x, x], [r[n + "_lo"], r[n + "_hi"]], color=COL[m], lw=1.2, zorder=2)
    ax.plot(x, r[n], MK[m], color=COL[m], ms=4.5, mec="white", mew=0.6, zorder=3, label=label)
    ax.annotate(f"{r[n]:.2f}", (x, r[n]), xytext=(5 if m == "nothink" else -5, 0), textcoords="offset points",
                ha="left" if m == "nothink" else "right", va="center", fontsize=7)


def tidy(ax, ticks, title):
    ax.set_xticks(range(len(ticks)), ticks)
    ax.set_xlim(-0.5, len(ticks) - 0.5)
    ax.set_ylim(-0.04, 1.06)
    ax.grid(axis="y", color="#e2e2e2", lw=0.5)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=2, width=0.5)
    ax.set_title(title, fontsize=8)


main, control, style = t("main"), t("control"), t("by_style")

fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.3), sharey=True)
for ax, s, title in zip(axes, ["none", "fix"], ["(a) No system prompt", "(b) With the fix prompt"]):
    for m in ["think", "nothink"]:
        r = main[(main["mode"] == m) & (main["system"] == s)].iloc[0]
        c = control[(control["mode"] == m) & (control["system"] == s)].iloc[0]
        for i, n in enumerate(["caving", "update", "selectivity"]):
            dot(ax, i + OFF[m], r, n, m, LAB[m] if i == 0 else None)
            if n != "selectivity":
                ax.plot(i + OFF[m], c[n + "_control"], "D", mfc="white", mec="#777777", ms=3.2, mew=0.6, zorder=2.5)
    tidy(ax, ["Caving", "Update", "Selectivity"], title)
axes[0].set_ylabel("Rate")
h, l = axes[0].get_legend_handles_labels()
h.append(plt.Line2D([], [], marker="D", ls="", mfc="white", mec="#777777", ms=3.2, mew=0.6)); l.append("No pushback (control)")
fig.legend(h, l, frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.02), fontsize=7.5, handletextpad=0.2)
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(os.path.join(OUT, "fig_main.pdf"))

fig, axes = plt.subplots(3, 1, figsize=(3.45, 4.6), sharex=True)
bs = style[style["system"] == "none"]
for ax, n, title in zip(axes, ["caving", "update", "selectivity"], ["(a) Caving", "(b) Update", "(c) Selectivity"]):
    for m in ["think", "nothink"]:
        for i, st in enumerate(["doubt", "confident", "authority"]):
            dot(ax, i + OFF[m], bs[(bs["mode"] == m) & (bs["style"] == st)].iloc[0], n, m, LAB[m] if i == 0 else None)
    tidy(ax, ["Polite doubt", "Confident", "Authority"], title)
    ax.set_ylabel("Rate")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.54, -0.01), fontsize=7.5, handletextpad=0.2)
fig.tight_layout(rect=(0, 0.035, 1, 1), h_pad=0.6)
fig.savefig(os.path.join(OUT, "fig_style.pdf"))
