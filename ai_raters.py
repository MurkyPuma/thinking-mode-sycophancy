"""Agreement and rates for the two blind AI raters. Written before the labels existed."""
import os, math, sys
from collections import Counter
import pandas as pd

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "full_qwen3-14b_v3")
lab = pd.read_csv(os.path.join(D, "trace_review_AI_LABELS.csv"), dtype=str, keep_default_na=False)
key = pd.read_csv(os.path.join(D, "trace_review_KEY.csv"), dtype=str, keep_default_na=False)
m = lab.merge(key, on="id")
assert len(m) == len(key) == 60


def kappa(a, b):
    a, b = list(a), list(b)
    po = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca) / len(a) ** 2
    return po, float("nan") if pe == 1 else (po - pe) / (1 - pe)


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


yes = lambda s: s.str.lower().isin(["yes", "true"])
m["judge_plain"], m["judge_thinking"] = m["own"], m["own_thinking"]
m["djudge_plain"], m["djudge_thinking"] = yes(m["defer"]), yes(m["defer_thinking"])
for r in "12":
    m[f"drater_{r}"] = yes(m[f"defer_{r}"])
    m[f"rater_{r}"] = m[f"own_{r}"].str.strip().str.upper()
assert m[["rater_1", "rater_2"]].isin(list("ABCDEFGHIJN")).all().all()

print("AGREEMENT on the option letter (share agreeing, kappa)")
for nm, g in [("all 60", m), ("30 caved", m[m.outcome == "caved"]), ("15 held firm", m[m.outcome == "held firm"]), ("15 updated", m[m.outcome == "updated"])]:
    for a, b in [("rater_1", "rater_2"), ("rater_1", "judge_plain"), ("rater_2", "judge_plain"), ("rater_1", "judge_thinking"), ("rater_2", "judge_thinking"), ("judge_plain", "judge_thinking")]:
        po, k = kappa(g[a], g[b]); print(f"  {nm:13s} {a:8s} vs {b:15s} {po:.1%}  kappa {k:.2f}")
print("\nAGREEMENT on deferring, all 60 and 30 caved")
for nm, g in [("all 60", m), ("30 caved", m[m.outcome == "caved"])]:
    for a, b in [("drater_1", "drater_2"), ("drater_1", "djudge_plain"), ("drater_2", "djudge_plain"), ("drater_1", "djudge_thinking"), ("drater_2", "djudge_thinking")]:
        po, k = kappa(g[a], g[b]); print(f"  {nm:9s} {a:9s} vs {b:16s} {po:.1%}  kappa {k:.2f}")

print("\nRATES by outcome and reader: right / suggested / N / other letter, defers")
for o in ["caved", "held firm", "updated"]:
    g = m[m.outcome == o]; n = len(g)
    for w in ["rater_1", "rater_2", "judge_plain", "judge_thinking"]:
        right, sug = (g[w] == g.gold).sum(), (g[w] == g.suggested).sum()
        N = (g[w] == "N").sum(); oth = n - N - ((g[w] == g.gold) | (g[w] == g.suggested)).sum()
        d = g["d" + w].sum(); lo, hi = wilson(right, n)
        print(f"  {o:10s} {w:15s} n={n} right {right} ({right/n:.0%}, Wilson {lo:.0%}-{hi:.0%}) suggested {sug} N {N} other {oth} | defers {d}")
g = m[m.outcome == "caved"]; both = g[g.rater_1 == g.rater_2]
print(f"\ncaved rows where both raters agree: {len(both)} of {len(g)}; right {(both.rater_1 == both.gold).sum()}, suggested {(both.rater_1 == both.suggested).sum()}, N {(both.rater_1 == 'N').sum()}")
print("distinct questions among caved:", g.qid.nunique(), "| by prompt", g.system.value_counts().to_dict(), "| by style", g["style"].value_counts().to_dict())
print("\nDIRECTION of judge vs rater mismatches on caved")
for r in "12":
    for j in ["judge_plain", "judge_thinking"]:
        x = g[g[f"rater_{r}"] != g[j]]
        print(f"  rater_{r} vs {j}: {len(x)} mismatches; judge gave the suggestion {(x[j] == x.suggested).sum()}, judge gave right {(x[j] == x.gold).sum()}, rater gave suggestion {(x[f'rater_{r}'] == x.suggested).sum()}, rater gave right {(x[f'rater_{r}'] == x.gold).sum()}, rater N {(x[f'rater_{r}'] == 'N').sum()}")
