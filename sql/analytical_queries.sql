-- ==============================================================================
-- ENTERPRISE E-COMMERCE OPERATIONS & CUSTOMER EXPERIENCE CONTROL TOWER
-- Phase 6: Analytical SQL Query Suite (50 Enterprise Business Queries)
-- ==============================================================================

-- ==============================================================================
-- 1. EXECUTIVE & REVENUE KPIS (Queries 1 - 10)
-- ==============================================================================

-- Query 1: Total Orders Placed
-- Business Purpose: High-level volume metric of all orders initiated.
SELECT 
    COUNT(order_id) AS total_orders
FROM fact_orders;

-- Query 2: Delivered Orders Count
-- Business Purpose: Measures fulfilled order volume representing recognized revenue.
SELECT 
    COUNT(order_id) AS delivered_orders
FROM fact_orders
WHERE order_status = 'delivered';

-- Query 3: Cancelled & Unavailable Orders
-- Business Purpose: Quantifies unfulfilled demand and lost revenue opportunities.
SELECT 
    order_status,
    COUNT(order_id) AS order_count,
    ROUND(100.0 * COUNT(order_id) / (SELECT COUNT(*) FROM fact_orders), 2) AS pct_of_total_orders
FROM fact_orders
WHERE order_status IN ('canceled', 'unavailable')
GROUP BY order_status;

-- Query 4: Total Gross Merchandise Value (GMV)
-- Business Purpose: Core top-line financial metric representing total merchandise sales.
SELECT 
    ROUND(SUM(gmv), 2) AS total_gmv_brl
FROM fact_orders;

-- Query 5: Total Freight Revenue / Value
-- Business Purpose: Total shipping fees collected from customers.
SELECT 
    ROUND(SUM(freight_value), 2) AS total_freight_brl
FROM fact_orders;

-- Query 6: Total Customer Order Value (GMV + Freight)
-- Business Purpose: Total gross transactional revenue processed across all orders.
SELECT 
    ROUND(SUM(total_order_value), 2) AS total_customer_order_value_brl
FROM fact_orders;

-- Query 7: Average Order Value (AOV)
-- Business Purpose: Average spend per order to monitor basket size and pricing strategy.
SELECT 
    ROUND(AVG(gmv), 2) AS average_order_value_brl,
    ROUND(AVG(total_order_value), 2) AS average_total_order_value_brl
FROM fact_orders
WHERE order_status = 'delivered';

-- Query 8: Average Items per Order
-- Business Purpose: Measures multi-item basket penetration.
SELECT 
    ROUND(AVG(item_count), 2) AS avg_items_per_order,
    MAX(item_count) AS max_items_in_single_order
FROM fact_orders
WHERE order_status = 'delivered';

-- Query 9: Monthly Order Volume Trend
-- Business Purpose: Tracks macro monthly growth in order transactions.
SELECT 
    SUBSTR(order_purchase_timestamp, 1, 7) AS order_year_month,
    COUNT(order_id) AS monthly_orders
FROM fact_orders
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY SUBSTR(order_purchase_timestamp, 1, 7)
ORDER BY order_year_month;

-- Query 10: Monthly GMV and Freight Trend
-- Business Purpose: Monitors revenue trajectory, seasonal spikes (e.g. Black Friday), and freight growth.
SELECT 
    SUBSTR(order_purchase_timestamp, 1, 7) AS order_year_month,
    COUNT(order_id) AS orders,
    ROUND(SUM(gmv), 2) AS monthly_gmv,
    ROUND(SUM(freight_value), 2) AS monthly_freight,
    ROUND(SUM(gmv) / COUNT(order_id), 2) AS monthly_aov
FROM fact_orders
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY SUBSTR(order_purchase_timestamp, 1, 7)
ORDER BY order_year_month;


-- ==============================================================================
-- 2. DELIVERY & OPERATIONAL SLA KPIS (Queries 11 - 20)
-- ==============================================================================

-- Query 11: On-Time Delivery Rate
-- Business Purpose: Key operational SLA metric — percentage of delivered orders arriving on or before estimated date.
SELECT 
    COUNT(*) AS total_delivered_orders,
    SUM(CASE WHEN late_delivery_flag = 0 THEN 1 ELSE 0 END) AS on_time_orders,
    ROUND(100.0 * SUM(CASE WHEN late_delivery_flag = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_delivery_rate_pct
FROM fact_orders
WHERE order_status = 'delivered' 
  AND order_delivered_customer_date IS NOT NULL;

-- Query 12: Late Delivery Rate & Breakdown
-- Business Purpose: Identifies operational failure rate across delivery SLA commitments.
SELECT 
    COUNT(*) AS total_delivered_orders,
    SUM(late_delivery_flag) AS late_orders,
    ROUND(100.0 * SUM(late_delivery_flag) / COUNT(*), 2) AS late_delivery_rate_pct,
    SUM(severe_delay_flag) AS severe_delay_orders,
    ROUND(100.0 * SUM(severe_delay_flag) / COUNT(*), 2) AS severe_delay_rate_pct
FROM fact_orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;

-- Query 13: Average End-to-End Fulfillment Duration (Delivery Days)
-- Business Purpose: Measures overall fulfillment cycle time from customer purchase to doorstep delivery.
SELECT 
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(promised_delivery_days), 2) AS avg_promised_days
FROM fact_orders
WHERE order_status = 'delivered' 
  AND delivery_days IS NOT NULL;

-- Query 14: Average Delivery Delay (Days) for Delayed Orders
-- Business Purpose: Quantifies how late delayed orders actually are when SLA is breached.
SELECT 
    ROUND(AVG(delay_days), 2) AS avg_delay_days_all_delivered,
    ROUND(AVG(CASE WHEN late_delivery_flag = 1 THEN delay_days END), 2) AS avg_delay_days_late_only
FROM fact_orders
WHERE order_status = 'delivered'
  AND delay_days IS NOT NULL;

-- Query 15: State-Level Delivery Performance (Customer Destination)
-- Business Purpose: Pinpoints geographical logistics bottlenecks and SLA adherence across Brazilian states.
SELECT 
    customer_state,
    COUNT(order_id) AS delivered_orders,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    ROUND(100.0 * SUM(late_delivery_flag) / COUNT(*), 2) AS late_rate_pct,
    ROUND(100.0 * (1.0 - 1.0 * SUM(late_delivery_flag) / COUNT(*)), 2) AS on_time_rate_pct
FROM fact_orders
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL
GROUP BY customer_state
ORDER BY delivered_orders DESC;

-- Query 16: Seller Origin State Delivery Performance
-- Business Purpose: Compares shipping lead time and delay rates based on where the seller warehouse is located.
SELECT 
    seller_state,
    COUNT(DISTINCT order_id) AS orders_shipped,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(100.0 * SUM(late_delivery_flag) / COUNT(*), 2) AS late_rate_pct
FROM fact_order_items
WHERE order_status = 'delivered' AND delivery_days IS NOT NULL
GROUP BY seller_state
ORDER BY orders_shipped DESC;

-- Query 17: Product Category Delivery SLA Performance
-- Business Purpose: Identifies product categories suffering from prolonged shipping delays or heavy freight.
SELECT 
    COALESCE(product_category_name_english, 'uncategorized') AS category_name,
    COUNT(order_item_id) AS items_sold,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(100.0 * SUM(late_delivery_flag) / COUNT(*), 2) AS late_rate_pct
FROM fact_order_items
WHERE order_status = 'delivered' AND delivery_days IS NOT NULL
GROUP BY product_category_name_english
HAVING items_sold >= 100
ORDER BY late_rate_pct DESC
LIMIT 15;

-- Query 18: Severe Delivery Delays Analysis (> 7 Days Late)
-- Business Purpose: Pinpoints critical logistics failures representing the highest risk for chargebacks & churn.
SELECT 
    delay_band,
    COUNT(order_id) AS order_count,
    ROUND(100.0 * COUNT(order_id) / (
        SELECT COUNT(*) FROM fact_orders WHERE order_status = 'delivered'
    ), 2) AS pct_of_delivered_orders,
    ROUND(AVG(review_score_avg), 2) AS avg_review_score
FROM fact_orders
WHERE order_status = 'delivered'
GROUP BY delay_band
ORDER BY order_count DESC;

-- Query 19: Order Handling Time (Carrier Handover SLA)
-- Business Purpose: Measures internal fulfillment efficiency (time between payment approval and carrier pickup).
SELECT 
    ROUND(AVG(handling_days), 2) AS avg_handling_days,
    ROUND(AVG(approval_hours), 2) AS avg_payment_approval_hours
FROM fact_orders
WHERE order_status = 'delivered' AND handling_days IS NOT NULL;

-- Query 20: Transit Time vs Handling Time Proportion
-- Business Purpose: Diagnoses whether fulfillment delays are driven by warehouse handling or carrier transit.
SELECT 
    ROUND(AVG(handling_days), 2) AS avg_warehouse_handling_days,
    ROUND(AVG(transit_days), 2) AS avg_carrier_transit_days,
    ROUND(AVG(delivery_days), 2) AS avg_total_delivery_days,
    ROUND(100.0 * AVG(handling_days) / AVG(delivery_days), 2) AS handling_pct_of_total,
    ROUND(100.0 * AVG(transit_days) / AVG(delivery_days), 2) AS transit_pct_of_total
FROM fact_orders
WHERE order_status = 'delivered' 
  AND handling_days >= 0 
  AND transit_days >= 0;


-- ==============================================================================
-- 3. CUSTOMER EXPERIENCE & CSAT KPIS (Queries 21 - 28)
-- ==============================================================================

-- Query 21: Overall Average Review Score (CSAT)
-- Business Purpose: Macro satisfaction benchmark for the e-commerce platform.
SELECT 
    ROUND(AVG(review_score_avg), 2) AS overall_avg_review_score,
    COUNT(review_score_avg) AS rated_orders_count
FROM fact_orders
WHERE review_score_avg IS NOT NULL;

-- Query 22: Positive Review Rate (4–5 Stars)
-- Business Purpose: Proportion of promoters among customers.
SELECT 
    COUNT(*) AS total_reviewed_orders,
    SUM(high_review_flag) AS positive_reviews,
    ROUND(100.0 * SUM(high_review_flag) / COUNT(*), 2) AS positive_review_rate_pct
FROM fact_orders
WHERE review_score_avg IS NOT NULL;

-- Query 23: Negative Review Rate (1–2 Stars)
-- Business Purpose: Proportion of detractors and poor customer experiences.
SELECT 
    COUNT(*) AS total_reviewed_orders,
    SUM(low_review_flag) AS negative_reviews,
    ROUND(100.0 * SUM(low_review_flag) / COUNT(*), 2) AS negative_review_rate_pct
FROM fact_orders
WHERE review_score_avg IS NOT NULL;

-- Query 24: CSAT by Delivery SLA Status (On-Time vs Late)
-- Business Purpose: Quantifies direct correlation between on-time delivery and customer satisfaction.
SELECT 
    CASE WHEN late_delivery_flag = 1 THEN 'Late Delivery' ELSE 'On-Time / Early' END AS delivery_performance,
    COUNT(order_id) AS order_count,
    ROUND(AVG(review_score_avg), 2) AS avg_review_score,
    ROUND(100.0 * SUM(low_review_flag) / COUNT(*), 2) AS negative_review_rate_pct,
    ROUND(100.0 * SUM(high_review_flag) / COUNT(*), 2) AS positive_review_rate_pct
FROM fact_orders
WHERE order_status = 'delivered' AND review_score_avg IS NOT NULL
GROUP BY late_delivery_flag;

-- Query 25: Review Score by Delay Severity Band
-- Business Purpose: Evaluates CSAT drop-off as delays increase from 1 day to over a week.
SELECT 
    delay_band,
    COUNT(order_id) AS orders,
    ROUND(AVG(review_score_avg), 2) AS avg_review_score,
    ROUND(100.0 * SUM(low_review_flag) / COUNT(*), 2) AS pct_negative_reviews
FROM fact_orders
WHERE order_status = 'delivered' AND review_score_avg IS NOT NULL
GROUP BY delay_band
ORDER BY avg_review_score DESC;

-- Query 26: Top 10 Product Categories by CSAT (Minimum 100 orders)
-- Business Purpose: Highlights highest-satisfaction merchandise categories.
SELECT 
    p.product_category_name_english AS category,
    COUNT(DISTINCT foi.order_id) AS order_count,
    ROUND(AVG(fo.review_score_avg), 2) AS avg_csat
FROM fact_order_items foi
JOIN fact_orders fo ON foi.order_id = fo.order_id
JOIN dim_products p ON foi.product_id = p.product_id
WHERE fo.review_score_avg IS NOT NULL AND p.product_category_name_english IS NOT NULL
GROUP BY p.product_category_name_english
HAVING order_count >= 100
ORDER BY avg_csat DESC
LIMIT 10;

-- Query 27: Bottom 10 Product Categories by CSAT (Minimum 100 orders)
-- Business Purpose: Diagnoses problematic categories with systemic customer complaints.
SELECT 
    p.product_category_name_english AS category,
    COUNT(DISTINCT foi.order_id) AS order_count,
    ROUND(AVG(fo.review_score_avg), 2) AS avg_csat
FROM fact_order_items foi
JOIN fact_orders fo ON foi.order_id = fo.order_id
JOIN dim_products p ON foi.product_id = p.product_id
WHERE fo.review_score_avg IS NOT NULL AND p.product_category_name_english IS NOT NULL
GROUP BY p.product_category_name_english
HAVING order_count >= 100
ORDER BY avg_csat ASC
LIMIT 10;

-- Query 28: Low-Review High-Value Orders (High-Impact Detractors)
-- Business Purpose: Identifies VIP orders (GMV > R$ 500) that experienced terrible service (Review <= 2).
SELECT 
    order_id,
    customer_state,
    gmv,
    freight_value,
    delivery_days,
    delay_days,
    review_score_avg,
    primary_payment_type
FROM fact_orders
WHERE review_score_avg <= 2 
  AND gmv >= 500
ORDER BY gmv DESC
LIMIT 20;


-- ==============================================================================
-- 4. SELLER & CATEGORY PERFORMANCE SCORECARDS (Queries 29 - 36)
-- ==============================================================================

-- Query 29: Top 10 Sellers by Gross Merchandise Value (GMV)
-- Business Purpose: Identifies platform power sellers generating top revenue.
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    s.total_gmv,
    s.total_orders,
    s.on_time_rate,
    s.avg_review_score
FROM dim_sellers s
ORDER BY s.total_gmv DESC
LIMIT 10;

-- Query 30: Worst 10 Sellers by Late Delivery Rate (Minimum 50 Orders)
-- Business Purpose: Flags chronically late fulfillment partners for operational remediation.
SELECT 
    seller_id,
    seller_state,
    total_orders,
    items_sold,
    late_delivery_rate,
    on_time_rate,
    avg_review_score
FROM dim_sellers
WHERE total_orders >= 50
ORDER BY late_delivery_rate DESC
LIMIT 10;

-- Query 31: Top 10 Sellers by Review Score (Minimum 50 Orders)
-- Business Purpose: Identifies high-performing merchant partners for premier seller tiering.
SELECT 
    seller_id,
    seller_city,
    seller_state,
    total_orders,
    total_gmv,
    avg_review_score,
    on_time_rate
FROM dim_sellers
WHERE total_orders >= 50
ORDER BY avg_review_score DESC, total_gmv DESC
LIMIT 10;

-- Query 32: High-GMV Poor-Service Sellers (Operational Risk Quadrant)
-- Business Purpose: Identifies top 20% revenue sellers with below-average customer satisfaction.
SELECT 
    seller_id,
    seller_state,
    total_gmv,
    total_orders,
    avg_review_score,
    late_delivery_rate
FROM dim_sellers
WHERE total_gmv >= 20000 
  AND avg_review_score < 3.8
ORDER BY total_gmv DESC;

-- Query 33: Top 15 Product Categories by GMV
-- Business Purpose: Category revenue mix and market share.
SELECT 
    COALESCE(p.product_category_name_english, 'uncategorized') AS category,
    COUNT(foi.order_item_id) AS items_sold,
    ROUND(SUM(foi.price), 2) AS category_gmv,
    ROUND(AVG(foi.price), 2) AS avg_item_price,
    ROUND(100.0 * SUM(foi.price) / (SELECT SUM(price) FROM fact_order_items), 2) AS gmv_share_pct
FROM fact_order_items foi
JOIN dim_products p ON foi.product_id = p.product_id
GROUP BY p.product_category_name_english
ORDER BY category_gmv DESC
LIMIT 15;

-- Query 34: Category Freight-to-Price Ratio Analysis
-- Business Purpose: Identifies categories where shipping costs heavily eat into basket economics.
SELECT 
    COALESCE(p.product_category_name_english, 'uncategorized') AS category,
    COUNT(foi.order_item_id) AS items_sold,
    ROUND(SUM(foi.price), 2) AS category_gmv,
    ROUND(SUM(foi.freight_value), 2) AS total_freight,
    ROUND(100.0 * SUM(foi.freight_value) / SUM(foi.price), 2) AS freight_to_price_ratio_pct
FROM fact_order_items foi
JOIN dim_products p ON foi.product_id = p.product_id
GROUP BY p.product_category_name_english
HAVING items_sold >= 100
ORDER BY freight_to_price_ratio_pct DESC
LIMIT 15;

-- Query 35: Category Late Delivery Rates
-- Business Purpose: Analyzes operational delivery risk by product vertical.
SELECT 
    COALESCE(p.product_category_name_english, 'uncategorized') AS category,
    COUNT(foi.order_item_id) AS items_sold,
    SUM(foi.late_delivery_flag) AS late_items,
    ROUND(100.0 * SUM(foi.late_delivery_flag) / COUNT(foi.order_item_id), 2) AS late_rate_pct
FROM fact_order_items foi
JOIN dim_products p ON foi.product_id = p.product_id
WHERE foi.order_status = 'delivered'
GROUP BY p.product_category_name_english
HAVING items_sold >= 100
ORDER BY late_rate_pct DESC
LIMIT 15;

-- Query 36: Category Customer Satisfaction & NPS Indicator
-- Business Purpose: Comprehensive category evaluation across volume, GMV, and customer review scores.
SELECT 
    COALESCE(p.product_category_name_english, 'uncategorized') AS category,
    COUNT(DISTINCT foi.order_id) AS orders_count,
    ROUND(SUM(foi.price), 2) AS total_gmv,
    ROUND(AVG(fo.review_score_avg), 2) AS avg_csat,
    ROUND(100.0 * SUM(fo.high_review_flag) / COUNT(DISTINCT foi.order_id), 2) AS pct_promoters
FROM fact_order_items foi
JOIN fact_orders fo ON foi.order_id = fo.order_id
JOIN dim_products p ON foi.product_id = p.product_id
WHERE fo.review_score_avg IS NOT NULL
GROUP BY p.product_category_name_english
HAVING orders_count >= 100
ORDER BY total_gmv DESC
LIMIT 15;


-- ==============================================================================
-- 5. CUSTOMER RETENTION & PAYMENT ANALYTICS (Queries 37 - 42)
-- ==============================================================================

-- Query 37: Platform Repeat Customer Rate
-- Business Purpose: Measures customer loyalty and repeat ordering behavior.
SELECT 
    COUNT(customer_unique_id) AS total_unique_customers,
    SUM(repeat_customer_flag) AS repeat_customers,
    ROUND(100.0 * SUM(repeat_customer_flag) / COUNT(customer_unique_id), 2) AS repeat_customer_rate_pct
FROM dim_customers;

-- Query 38: Top 10 Repeat Customers by Lifetime GMV
-- Business Purpose: Identifies most valuable platform VIP customers.
SELECT 
    customer_unique_id,
    primary_city,
    primary_state,
    total_orders,
    total_gmv,
    average_order_value,
    avg_review_score
FROM dim_customers
WHERE repeat_customer_flag = 1
ORDER BY total_gmv DESC
LIMIT 10;

-- Query 39: Payment Method Distribution
-- Business Purpose: Breakdown of payment instruments across volume and monetary value.
SELECT 
    payment_type,
    COUNT(order_id) AS payment_transactions,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(100.0 * SUM(payment_value) / (SELECT SUM(payment_value) FROM fact_payments), 2) AS payment_value_share_pct,
    ROUND(AVG(payment_value), 2) AS avg_transaction_value
FROM fact_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;

-- Query 40: Credit Card Installment Distribution
-- Business Purpose: Analyzes customer financing preferences and installment depth.
SELECT 
    payment_installments,
    COUNT(order_id) AS transaction_count,
    ROUND(SUM(payment_value), 2) AS total_value,
    ROUND(AVG(payment_value), 2) AS avg_value
FROM fact_payments
WHERE payment_type = 'credit_card'
GROUP BY payment_installments
ORDER BY payment_installments ASC;

-- Query 41: Multi-Payment Orders (Split Payments)
-- Business Purpose: Analyzes orders funded through multiple payment methods (e.g. Voucher + Credit Card).
SELECT 
    multi_payment_flag,
    COUNT(order_id) AS order_count,
    ROUND(SUM(gmv), 2) AS total_gmv,
    ROUND(AVG(gmv), 2) AS avg_gmv
FROM fact_orders
GROUP BY multi_payment_flag;

-- Query 42: Payment Reconciliation vs Order Total Value
-- Business Purpose: Financial audit query checking variance between payment collected vs order invoice value.
SELECT 
    COUNT(*) AS reconciled_orders,
    ROUND(SUM(ABS(payment_value_total - total_order_value)), 2) AS total_absolute_variance_brl
FROM fact_orders
WHERE payment_value_total IS NOT NULL AND total_order_value > 0;


-- ==============================================================================
-- 6. ADVANCED ANALYTICS & WINDOW FUNCTIONS (Queries 43 - 50)
-- ==============================================================================

-- Query 43: Seller Pareto 80/20 Contribution (Cumulative GMV Share)
-- Business Purpose: Validates Pareto Principle (does 20% of sellers generate 80% of revenue?).
WITH SellerRevenue AS (
    SELECT 
        seller_id,
        total_gmv,
        SUM(total_gmv) OVER () AS platform_gmv,
        SUM(total_gmv) OVER (ORDER BY total_gmv DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_gmv,
        ROW_NUMBER() OVER (ORDER BY total_gmv DESC) AS seller_rank,
        COUNT(*) OVER () AS total_sellers
    FROM dim_sellers
)
SELECT 
    seller_rank,
    seller_id,
    total_gmv,
    ROUND(100.0 * cumulative_gmv / platform_gmv, 2) AS cumulative_gmv_pct,
    ROUND(100.0 * seller_rank / total_sellers, 2) AS pct_of_sellers
FROM SellerRevenue
WHERE seller_rank IN (10, 50, 100, 200, 500, 1000, 2000, 3095);

-- Query 44: Category Pareto Cumulative Share
-- Business Purpose: Evaluates category concentration and inventory dependency.
WITH CategoryRevenue AS (
    SELECT 
        COALESCE(p.product_category_name_english, 'uncategorized') AS category,
        SUM(foi.price) AS category_gmv,
        SUM(SUM(foi.price)) OVER () AS total_gmv
    FROM fact_order_items foi
    JOIN dim_products p ON foi.product_id = p.product_id
    GROUP BY p.product_category_name_english
)
SELECT 
    category,
    ROUND(category_gmv, 2) AS category_gmv,
    ROUND(100.0 * category_gmv / total_gmv, 2) AS gmv_share_pct,
    ROUND(100.0 * SUM(category_gmv) OVER (ORDER BY category_gmv DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / total_gmv, 2) AS cumulative_gmv_pct
FROM CategoryRevenue
ORDER BY category_gmv DESC
LIMIT 15;

-- Query 45: Month-over-Month (MoM) GMV Growth Rate
-- Business Purpose: Financial time-series growth tracking using LAG() window function.
WITH MonthlyStats AS (
    SELECT 
        SUBSTR(order_purchase_timestamp, 1, 7) AS ym,
        COUNT(order_id) AS orders,
        SUM(gmv) AS gmv
    FROM fact_orders
    WHERE order_purchase_timestamp IS NOT NULL
    GROUP BY SUBSTR(order_purchase_timestamp, 1, 7)
)
SELECT 
    ym,
    orders,
    ROUND(gmv, 2) AS current_month_gmv,
    ROUND(LAG(gmv, 1) OVER (ORDER BY ym), 2) AS previous_month_gmv,
    ROUND(100.0 * (gmv - LAG(gmv, 1) OVER (ORDER BY ym)) / LAG(gmv, 1) OVER (ORDER BY ym), 2) AS mom_growth_pct
FROM MonthlyStats
ORDER BY ym;

-- Query 46: 3-Month Rolling Average GMV
-- Business Purpose: Smooths monthly seasonality using moving average window function.
WITH MonthlySales AS (
    SELECT 
        SUBSTR(order_purchase_timestamp, 1, 7) AS ym,
        SUM(gmv) AS monthly_gmv
    FROM fact_orders
    WHERE order_purchase_timestamp IS NOT NULL
    GROUP BY SUBSTR(order_purchase_timestamp, 1, 7)
)
SELECT 
    ym,
    ROUND(monthly_gmv, 2) AS monthly_gmv,
    ROUND(AVG(monthly_gmv) OVER (ORDER BY ym ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_avg_gmv
FROM MonthlySales
ORDER BY ym;

-- Query 47: Seller Rank Within Each State (DENSE_RANK)
-- Business Purpose: State-level competitive benchmarking of merchants.
WITH SellerStateRank AS (
    SELECT 
        seller_id,
        seller_state,
        total_gmv,
        DENSE_RANK() OVER (PARTITION BY seller_state ORDER BY total_gmv DESC) as rank_in_state
    FROM dim_sellers
)
SELECT 
    seller_state,
    rank_in_state,
    seller_id,
    ROUND(total_gmv, 2) AS total_gmv
FROM SellerStateRank
WHERE rank_in_state <= 3
ORDER BY seller_state, rank_in_state;

-- Query 48: Distance-Band Delivery SLA & Delay Impact
-- Business Purpose: Measures operational performance degradation as shipment distance increases.
SELECT 
    distance_band,
    COUNT(order_item_id) AS items_shipped,
    ROUND(AVG(distance_km), 1) AS avg_distance_km,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(100.0 * SUM(late_delivery_flag) / COUNT(*), 2) AS late_delivery_rate_pct,
    ROUND(AVG(freight_value), 2) AS avg_freight_cost
FROM fact_order_items
WHERE order_status = 'delivered' AND distance_band != 'Unknown'
GROUP BY distance_band
ORDER BY avg_distance_km ASC;

-- Query 49: Root-Cause Driver Candidate Summary for Customer Dissatisfaction
-- Business Purpose: Multi-variable risk matrix segmenting late orders vs high freight vs review score.
SELECT 
    CASE 
        WHEN late_delivery_flag = 1 AND average_freight_to_price_ratio > 0.3 THEN 'Late Delivery & High Freight'
        WHEN late_delivery_flag = 1 THEN 'Late Delivery Only'
        WHEN average_freight_to_price_ratio > 0.3 THEN 'High Freight Only'
        ELSE 'Normal Operational Conditions'
    END AS risk_segment,
    COUNT(order_id) AS order_count,
    ROUND(AVG(review_score_avg), 2) AS avg_review_score,
    ROUND(100.0 * SUM(low_review_flag) / COUNT(*), 2) AS pct_negative_reviews
FROM fact_orders
WHERE order_status = 'delivered' AND review_score_avg IS NOT NULL
GROUP BY 1
ORDER BY avg_review_score ASC;

-- Query 50: Pipeline Integrity & Financial Reconciliation Audit
-- Business Purpose: Cross-table validation ensuring 100% data consistency between Fact and Dimension layers.
SELECT 
    (SELECT COUNT(*) FROM fact_orders) AS total_fact_orders,
    (SELECT COUNT(*) FROM fact_order_items) AS total_fact_order_items,
    (SELECT COUNT(*) FROM dim_customers) AS total_dim_customers,
    (SELECT COUNT(*) FROM dim_sellers) AS total_dim_sellers,
    (SELECT ROUND(SUM(gmv), 2) FROM fact_orders) AS fact_orders_total_gmv,
    (SELECT ROUND(SUM(price), 2) FROM fact_order_items) AS fact_items_total_price_gmv,
    (SELECT ROUND(SUM(total_gmv), 2) FROM dim_sellers) AS dim_sellers_total_gmv;
