CREATE TABLE suppliers (
 supplier_id VARCHAR(10) PRIMARY KEY, supplier_name VARCHAR(100), region VARCHAR(30)
);
CREATE TABLE inventory (
 sku VARCHAR(20) PRIMARY KEY, category VARCHAR(50), supplier_id VARCHAR(10) REFERENCES suppliers(supplier_id),
 units_sold_annual INT, avg_inventory INT, unit_cost DECIMAL(12,2), stockout_days INT,
 lead_time_days INT, on_time_delivery_rate DECIMAL(5,4), defect_rate DECIMAL(5,4)
);
CREATE INDEX idx_inventory_supplier ON inventory(supplier_id);
CREATE INDEX idx_inventory_category ON inventory(category);
