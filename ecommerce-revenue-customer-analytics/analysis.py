"""Reproducible e-commerce analytics portfolio project."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
ROOT = Path(__file__).parent
DATA, OUT = ROOT / "data", ROOT / "outputs"
DATA.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

n = 12000
orders = pd.DataFrame({
    "order_id": [f"O{i:06d}" for i in range(1, n + 1)],
    "customer_id": [f"C{x:05d}" for x in rng.integers(1, 3001, n)],
    "order_date": pd.to_datetime(rng.choice(pd.date_range("2025-01-01", "2025-12-31"), n)),
    "category": rng.choice(["Electronics","Fashion","Home","Beauty","Grocery"], n),
    "region": rng.choice(["North","South","East","West"], n),
    "quantity": rng.integers(1, 5, n),
    "unit_price": rng.gamma(3.2, 650, n).round(2),
})
orders["discount_pct"] = rng.choice([0,5,10,15,20], n, p=[.25,.25,.25,.15,.10])
orders["returned"] = rng.binomial(1, np.where(orders["category"].eq("Fashion"), .14, .07))
orders["revenue"] = (orders.quantity * orders.unit_price * (1-orders.discount_pct/100)).round(2)

# Introduce and then clean realistic quality issues.
orders.loc[rng.choice(n, 35, replace=False), "region"] = None
orders = pd.concat([orders, orders.sample(20, random_state=42)]).drop_duplicates("order_id")
orders["region"] = orders["region"].fillna("Unknown")
orders = orders.query("quantity > 0 and unit_price > 0").copy()
orders.to_csv(DATA / "orders.csv", index=False)

net = orders.query("returned == 0").copy()
net["month"] = net.order_date.dt.to_period("M").astype(str)
monthly = net.groupby("month").agg(revenue=("revenue","sum"),orders=("order_id","nunique"),customers=("customer_id","nunique")).reset_index()
monthly["aov"] = monthly.revenue / monthly.orders
monthly["mom_growth_pct"] = monthly.revenue.pct_change().mul(100)
monthly.to_csv(OUT / "monthly_kpis.csv", index=False)

snapshot = orders.order_date.max() + pd.Timedelta(days=1)
rfm = net.groupby("customer_id").agg(
    recency=("order_date", lambda x: (snapshot-x.max()).days),
    frequency=("order_id","nunique"), monetary=("revenue","sum")).reset_index()
rfm["r"] = pd.qcut(rfm.recency.rank(method="first"), 4, labels=[4,3,2,1])
rfm["f"] = pd.qcut(rfm.frequency.rank(method="first"), 4, labels=[1,2,3,4])
rfm["m"] = pd.qcut(rfm.monetary.rank(method="first"), 4, labels=[1,2,3,4])
rfm["score"] = rfm[["r","f","m"]].astype(int).sum(axis=1)
rfm["segment"] = pd.cut(rfm.score,[0,5,8,10,12],labels=["At Risk","Regular","Loyal","Champions"])
rfm.to_csv(OUT / "rfm_segments.csv", index=False)

summary = pd.DataFrame({"kpi":["Revenue","Orders","AOV","Return Rate","Repeat Customer Rate"],
"value":[net.revenue.sum(),net.order_id.nunique(),net.revenue.sum()/net.order_id.nunique(),orders.returned.mean(),(net.groupby("customer_id").order_id.nunique()>1).mean()]})
summary.to_csv(OUT / "kpi_summary.csv", index=False)

fig, axes = plt.subplots(1,2,figsize=(12,4.5))
axes[0].plot(monthly.month,monthly.revenue,marker="o"); axes[0].set_title("Monthly Net Revenue"); axes[0].tick_params(axis="x",rotation=45)
net.groupby("category").revenue.sum().sort_values().plot.barh(ax=axes[1]); axes[1].set_title("Revenue by Category")
plt.tight_layout(); plt.savefig(OUT/"executive_dashboard.png",dpi=160)
print(summary.to_string(index=False))
