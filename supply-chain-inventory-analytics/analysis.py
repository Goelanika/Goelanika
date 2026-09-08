"""Supply chain, inventory and sales analytics."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng=np.random.default_rng(42)
ROOT=Path(__file__).parent
DATA,OUT=ROOT/"data",ROOT/"outputs"
DATA.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
n=1500
df=pd.DataFrame({
 "sku":[f"SKU{i:05d}" for i in range(1,n+1)],
 "category":rng.choice(["Electronics","Home","Personal Care","Grocery","Fashion"],n),
 "supplier_id":[f"S{x:03d}" for x in rng.integers(1,61,n)],
 "units_sold_annual":rng.integers(20,3000,n),
 "avg_inventory":rng.integers(10,900,n),
 "unit_cost":rng.gamma(2.8,350,n).round(2),
 "stockout_days":rng.integers(0,55,n),
 "lead_time_days":rng.integers(2,45,n),
 "on_time_delivery_rate":rng.uniform(.70,1.0,n).round(3),
 "defect_rate":rng.uniform(0,.09,n).round(3)
})
# Introduce and repair realistic quality issues.
df.loc[rng.choice(n,20,replace=False),"supplier_id"]=None
df=pd.concat([df,df.sample(12,random_state=42)]).drop_duplicates("sku")
df["supplier_id"]=df.supplier_id.fillna("Unknown")
df["cogs"]=df.units_sold_annual*df.unit_cost
df["inventory_value"]=df.avg_inventory*df.unit_cost
df["inventory_turnover"]=df.cogs/df.inventory_value.replace(0,np.nan)
df["days_inventory"]=365/df.inventory_turnover
df["stockout_rate"]=df.stockout_days/365
df["annual_sales_value"]=df.units_sold_annual*df.unit_cost*1.35

ranked=df.sort_values("annual_sales_value",ascending=False).copy()
ranked["cumulative_share"]=ranked.annual_sales_value.cumsum()/ranked.annual_sales_value.sum()
ranked["abc_class"]=np.select([ranked.cumulative_share<=.80,ranked.cumulative_share<=.95],["A","B"],default="C")
ranked["movement"]=pd.qcut(ranked.units_sold_annual.rank(method="first"),3,labels=["Slow","Medium","Fast"])
ranked.to_csv(DATA/"inventory.csv",index=False)

supplier=ranked.groupby("supplier_id").agg(skus=("sku","nunique"),on_time_rate=("on_time_delivery_rate","mean"),defect_rate=("defect_rate","mean"),lead_time=("lead_time_days","mean")).reset_index()
supplier.to_csv(OUT/"supplier_scorecard.csv",index=False)
abc=ranked.groupby("abc_class").agg(skus=("sku","nunique"),sales_value=("annual_sales_value","sum"),avg_stockout_rate=("stockout_rate","mean"),avg_days_inventory=("days_inventory","mean")).reset_index()
abc.to_csv(OUT/"abc_summary.csv",index=False)
summary=pd.DataFrame({"kpi":["SKUs","Inventory Value","Average Turnover","Average Stock-out Rate","A-Class SKUs"],"value":[ranked.sku.nunique(),ranked.inventory_value.sum(),ranked.inventory_turnover.mean(),ranked.stockout_rate.mean(),ranked.abc_class.eq("A").sum()]})
summary.to_csv(OUT/"kpi_summary.csv",index=False)

fig,axes=plt.subplots(1,2,figsize=(11,4.5))
ranked.groupby("category").annual_sales_value.sum().sort_values().plot.barh(ax=axes[0]); axes[0].set_title("Annual Sales Value")
ranked.groupby("abc_class").stockout_rate.mean().plot.bar(ax=axes[1],color=["#4472C4","#ED7D31","#A5A5A5"]); axes[1].set_title("Stock-out Rate by ABC Class")
plt.tight_layout(); plt.savefig(OUT/"inventory_dashboard.png",dpi=160)
print(summary.to_string(index=False))
