-- Monthly revenue, AOV and growth
WITH monthly AS (
 SELECT DATE_TRUNC('month',order_date) month,
 SUM(quantity*unit_price*(1-discount_pct/100.0)) revenue, COUNT(DISTINCT order_id) orders
 FROM orders WHERE returned=0 GROUP BY 1)
SELECT month,revenue,orders,revenue/NULLIF(orders,0) aov,
100.0*(revenue-LAG(revenue) OVER(ORDER BY month))/NULLIF(LAG(revenue) OVER(ORDER BY month),0) mom_growth_pct
FROM monthly ORDER BY month;

-- Repeat customer rate
WITH f AS (SELECT customer_id,COUNT(DISTINCT order_id) n FROM orders WHERE returned=0 GROUP BY customer_id)
SELECT ROUND(100.0*AVG(CASE WHEN n>1 THEN 1 ELSE 0 END),2) repeat_customer_rate_pct FROM f;

-- Category return rate
SELECT p.category,SUM(CASE WHEN o.returned=0 THEN o.quantity*o.unit_price*(1-o.discount_pct/100.0) ELSE 0 END) net_revenue,
ROUND(100.0*AVG(o.returned),2) return_rate_pct
FROM orders o JOIN products p ON o.product_id=p.product_id GROUP BY p.category ORDER BY net_revenue DESC;
