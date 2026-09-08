-- Inventory health by category
SELECT category,COUNT(*) skus,SUM(avg_inventory*unit_cost) inventory_value,
ROUND(AVG((units_sold_annual*unit_cost)/NULLIF(avg_inventory*unit_cost,0)),2) avg_turnover,
ROUND(AVG(365.0*avg_inventory/NULLIF(units_sold_annual,0)),2) avg_days_inventory,
ROUND(100.0*AVG(stockout_days/365.0),2) stockout_rate_pct
FROM inventory GROUP BY category ORDER BY inventory_value DESC;

-- ABC classification by annual sales value
WITH ranked AS (
 SELECT sku,category,units_sold_annual*unit_cost*1.35 annual_sales_value,
 SUM(units_sold_annual*unit_cost*1.35) OVER(ORDER BY units_sold_annual*unit_cost DESC)/
 NULLIF(SUM(units_sold_annual*unit_cost*1.35) OVER(),0) cumulative_share
 FROM inventory)
SELECT sku,category,annual_sales_value,
CASE WHEN cumulative_share<=.80 THEN 'A' WHEN cumulative_share<=.95 THEN 'B' ELSE 'C' END abc_class
FROM ranked ORDER BY annual_sales_value DESC;

-- Supplier scorecard
SELECT supplier_id,COUNT(*) skus,ROUND(AVG(on_time_delivery_rate)*100,2) on_time_pct,
ROUND(AVG(defect_rate)*100,2) defect_pct,ROUND(AVG(lead_time_days),2) avg_lead_time_days
FROM inventory GROUP BY supplier_id ORDER BY on_time_pct DESC,defect_pct;
