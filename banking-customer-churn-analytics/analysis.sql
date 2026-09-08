-- Overall churn KPIs
SELECT COUNT(*) customers,ROUND(100.0*AVG(churned),2) churn_rate_pct,
ROUND(100.0*AVG(active_member),2) active_member_rate_pct FROM customers;

-- Churn by activity and tenure
SELECT CASE WHEN active_member=1 THEN 'Active' ELSE 'Inactive' END activity,
CASE WHEN tenure_years<=1 THEN '0-1' WHEN tenure_years<=4 THEN '2-4'
WHEN tenure_years<=7 THEN '5-7' ELSE '8-10' END tenure_band,
COUNT(*) customers,ROUND(100.0*AVG(churned),2) churn_rate_pct
FROM customers GROUP BY 1,2 ORDER BY 1,2;

-- Interpretable risk segments
WITH scored AS (
 SELECT *,2*(1-active_member)+CASE WHEN products>=3 THEN 1 ELSE 0 END+
 CASE WHEN tenure_years<=1 THEN 1 ELSE 0 END+CASE WHEN balance>140000 THEN 1 ELSE 0 END risk_score
 FROM customers)
SELECT CASE WHEN risk_score>=4 THEN 'High' WHEN risk_score>=2 THEN 'Medium' ELSE 'Low' END risk_segment,
COUNT(*) customers,ROUND(100.0*AVG(churned),2) churn_rate_pct,ROUND(AVG(balance),2) avg_balance
FROM scored GROUP BY 1 ORDER BY churn_rate_pct DESC;
