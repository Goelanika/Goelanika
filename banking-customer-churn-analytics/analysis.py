"""Banking customer churn and retention analytics."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng=np.random.default_rng(42)
ROOT=Path(__file__).parent
DATA,OUT=ROOT/"data",ROOT/"outputs"
DATA.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
n=10000
df=pd.DataFrame({
 "customer_id":[f"C{i:06d}" for i in range(1,n+1)],
 "age":np.clip(rng.normal(39,11,n).round(),18,80).astype(int),
 "tenure_years":rng.integers(0,11,n),
 "geography":rng.choice(["North","South","East","West"],n),
 "balance":np.maximum(0,rng.normal(85000,52000,n)).round(2),
 "products":rng.choice([1,2,3,4],n,p=[.48,.38,.11,.03]),
 "active_member":rng.binomial(1,.63,n),
 "credit_score":np.clip(rng.normal(650,85,n).round(),300,850).astype(int)
})
logit=-2.6 + .75*(1-df.active_member)+.55*(df.products>=3)+.45*(df.tenure_years<=1)+.35*(df.balance>140000)+.015*(df.age-40)
prob=1/(1+np.exp(-logit))
df["churned"]=rng.binomial(1,prob)
# Create then repair quality issues.
df.loc[rng.choice(n,30,replace=False),"geography"]=None
df=pd.concat([df,df.sample(15,random_state=42)]).drop_duplicates("customer_id")
df["geography"]=df.geography.fillna("Unknown")
df.to_csv(DATA/"customers.csv",index=False)

df["activity_segment"]=np.where(df.active_member.eq(1),"Active","Inactive")
df["tenure_band"]=pd.cut(df.tenure_years,[-1,1,4,7,10],labels=["0-1","2-4","5-7","8-10"])
df["risk_score"]=(2*(1-df.active_member)+1*(df.products>=3)+1*(df.tenure_years<=1)+1*(df.balance>140000))
df["risk_segment"]=pd.cut(df.risk_score,[-1,1,3,5],labels=["Low","Medium","High"])

segment=df.groupby("risk_segment",observed=True).agg(customers=("customer_id","nunique"),churn_rate=("churned","mean"),avg_balance=("balance","mean")).reset_index()
segment.to_csv(OUT/"risk_segments.csv",index=False)
drivers=df.groupby(["activity_segment","tenure_band"],observed=True).agg(customers=("customer_id","nunique"),churn_rate=("churned","mean")).reset_index()
drivers.to_csv(OUT/"churn_drivers.csv",index=False)
summary=pd.DataFrame({"kpi":["Customers","Churn Rate","Active Member Rate","High Risk Customers"],"value":[df.customer_id.nunique(),df.churned.mean(),df.active_member.mean(),df.risk_segment.eq("High").sum()]})
summary.to_csv(OUT/"kpi_summary.csv",index=False)

fig,axes=plt.subplots(1,2,figsize=(11,4.5))
segment.plot.bar(x="risk_segment",y="churn_rate",legend=False,ax=axes[0],color="#C0504D"); axes[0].set_title("Churn Rate by Risk Segment")
df.groupby("tenure_band",observed=True).churned.mean().plot(ax=axes[1],marker="o"); axes[1].set_title("Churn Rate by Tenure")
plt.tight_layout(); plt.savefig(OUT/"churn_dashboard.png",dpi=160)
print(summary.to_string(index=False))
