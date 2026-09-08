# E-Commerce Revenue & Customer Analytics

## Business problem
Management needs a reliable view of revenue performance, average order value, returns, customer retention and product/category trends.

## What this project demonstrates
- Python/Pandas data generation, cleaning and exploratory analysis
- SQL joins, CTEs, CASE expressions and window functions
- Revenue, AOV, return rate, repeat-customer rate and monthly growth
- RFM customer segmentation and cohort-style retention analysis
- Reproducible KPI tables and dashboard charts

## Files
- `analysis.py`: generates realistic data, cleans it, calculates KPIs and creates charts
- `schema.sql`: relational database schema
- `analysis.sql`: business-focused SQL queries
- `dashboard_design.md`: Power BI page and KPI plan
- `requirements.txt`: dependencies

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python analysis.py
```
The script creates `data/orders.csv` and analysis outputs. Data is synthetic and generated with a fixed seed; no real customer information is included.