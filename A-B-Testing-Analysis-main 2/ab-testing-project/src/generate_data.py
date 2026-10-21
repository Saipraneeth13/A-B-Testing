"""Generate a realistic A/B test dataset (replace with real data if you have it)."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 8000  # total visitors

df = pd.DataFrame({
    "user_id": np.arange(1, N + 1),
    "group": rng.choice(["A", "B"], size=N),           # random assignment
    "device": rng.choice(["mobile", "desktop", "tablet"], size=N, p=[0.55, 0.35, 0.10]),
})

# Baseline conversion by device; variant B gives a lift (stronger on mobile)
base = df["device"].map({"mobile": 0.08, "desktop": 0.13, "tablet": 0.10})
lift = np.where(df["group"] == "B", df["device"].map({"mobile": 0.035, "desktop": 0.015, "tablet": 0.01}), 0)
df["converted"] = rng.binomial(1, base + lift)
df["revenue"] = np.where(df["converted"] == 1, rng.gamma(shape=4, scale=15, size=N).round(2), 0.0)

df.to_csv("data/ab_test_data.csv", index=False)
print(f"Saved {len(df)} rows to data/ab_test_data.csv")
