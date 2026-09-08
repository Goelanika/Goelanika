CREATE TABLE customers (customer_id VARCHAR(10) PRIMARY KEY, signup_date DATE, region VARCHAR(30));
CREATE TABLE products (product_id VARCHAR(10) PRIMARY KEY, category VARCHAR(50), unit_cost DECIMAL(12,2));
CREATE TABLE orders (
 order_id VARCHAR(10) PRIMARY KEY, customer_id VARCHAR(10) NOT NULL REFERENCES customers(customer_id),
 product_id VARCHAR(10) REFERENCES products(product_id), order_date DATE NOT NULL, quantity INT NOT NULL,
 unit_price DECIMAL(12,2) NOT NULL, discount_pct DECIMAL(5,2) DEFAULT 0, returned INT DEFAULT 0
);