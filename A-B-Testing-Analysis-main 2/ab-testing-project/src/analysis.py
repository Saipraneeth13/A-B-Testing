"""A/B test analysis: sanity checks, significance test, CI, bootstrap, segments, power."""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ALPHA = 0.05
rng = np.random.default_rng(0)
df = pd.read_csv("data/ab_test_data.csv")
out = []

def log(s=""):
    print(s); out.append(s)

# 1. Sanity check: Sample Ratio Mismatch (are groups ~50/50?)
counts = df["group"].value_counts().sort_index()
chi_srm, p_srm = stats.chisquare(counts.values)
log("1) SANITY CHECK (sample ratio)")
log(f"   A={counts['A']}, B={counts['B']}  | SRM p-value={p_srm:.3f} -> {'OK' if p_srm > 0.01 else 'PROBLEM'}")

# 2. Conversion summary
g = df.groupby("group").agg(visitors=("user_id", "count"),
                            conversions=("converted", "sum"),
                            rate=("converted", "mean"),
                            revenue_per_visitor=("revenue", "mean"))
log("\n2) SUMMARY\n" + g.round(4).to_string())

# 3. Two-proportion z-test
nA, nB = g.loc["A", "visitors"], g.loc["B", "visitors"]
xA, xB = g.loc["A", "conversions"], g.loc["B", "conversions"]
pA, pB = xA / nA, xB / nB
pp = (xA + xB) / (nA + nB)
z = (pB - pA) / np.sqrt(pp * (1 - pp) * (1 / nA + 1 / nB))
p_val = 2 * (1 - stats.norm.cdf(abs(z)))
se = np.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
diff = pB - pA
ci = (diff - 1.96 * se, diff + 1.96 * se)
log("\n3) SIGNIFICANCE TEST (two-proportion z-test)")
log(f"   z={z:.3f}, p-value={p_val:.4f}")
log(f"   Lift: {diff:.4f} abs ({diff / pA:.1%} relative), 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]")
log(f"   Decision: {'Reject H0 - B is different from A' if p_val < ALPHA else 'Fail to reject H0'}")

# 4. Bootstrap CI (assumption-free check)
a = df.loc[df.group == "A", "converted"].values
b = df.loc[df.group == "B", "converted"].values
boot = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(5000)]
bl, bh = np.percentile(boot, [2.5, 97.5])
log(f"\n4) BOOTSTRAP 95% CI for lift: [{bl:.4f}, {bh:.4f}]")

# 5. Revenue per visitor (Welch t-test)
t, p_rev = stats.ttest_ind(df.loc[df.group == "B", "revenue"], df.loc[df.group == "A", "revenue"], equal_var=False)
log(f"\n5) REVENUE PER VISITOR: Welch t-test p-value={p_rev:.4f}")

# 6. Segment analysis by device (Bonferroni-corrected)
log("\n6) SEGMENTS BY DEVICE (Bonferroni alpha = %.4f)" % (ALPHA / 3))
for dev, sub in df.groupby("device"):
    ct = pd.crosstab(sub["group"], sub["converted"])
    _, p, _, _ = stats.chi2_contingency(ct)
    r = sub.groupby("group")["converted"].mean()
    log(f"   {dev:8s} A={r['A']:.3f} B={r['B']:.3f}  p={p:.4f}  {'significant' if p < ALPHA / 3 else 'not significant'}")

# 7. Observed power
z_b = (abs(diff) - 1.96 * np.sqrt(pp * (1 - pp) * (1 / nA + 1 / nB))) / se
log(f"\n7) APPROXIMATE POWER at observed effect: {stats.norm.cdf(z_b):.1%}")

# Charts
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].bar(["A", "B"], [pA, pB], color=["#8da0cb", "#66c2a5"])
for i, v in enumerate([pA, pB]): ax[0].text(i, v + .002, f"{v:.2%}", ha="center")
ax[0].set_title("Overall conversion rate")

seg = df.groupby(["device", "group"])["converted"].mean().unstack()
seg.plot(kind="bar", ax=ax[1], color=["#8da0cb", "#66c2a5"], rot=0)
ax[1].set_title("Conversion by device"); ax[1].set_xlabel("")

ax[2].hist(boot, bins=40, color="#e78ac3")
ax[2].axvline(0, color="k", ls="--"); ax[2].axvline(bl, color="gray"); ax[2].axvline(bh, color="gray")
ax[2].set_title("Bootstrap distribution of lift (B - A)")
plt.tight_layout(); plt.savefig("results/ab_test_results.png", dpi=150)

open("results/summary.txt", "w").write("\n".join(out))
