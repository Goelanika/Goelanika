CREATE TABLE customers (
 customer_id VARCHAR(12) PRIMARY KEY, age INT, tenure_years INT, geography VARCHAR(30),
 balance DECIMAL(14,2), products INT, active_member INT, credit_score INT, churned INT
);
CREATE INDEX idx_customers_churn ON customers(churned);
CREATE INDEX idx_customers_activity ON customers(active_member);
