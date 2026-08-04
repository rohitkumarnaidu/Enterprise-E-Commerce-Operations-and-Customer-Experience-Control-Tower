# Business Requirements Document

## Stakeholders
- E-commerce operations manager
- Logistics manager
- Seller-management team
- Customer-experience team
- Category manager
- Commercial analyst
- Executive management

## Business Questions

### Executive Questions
- How many orders were placed?
- What is GMV?
- What is average order value?
- How are orders and GMV trending?
- What percentage of orders were delivered, cancelled, or unavailable?

### Delivery Questions
- What is the on-time delivery rate?
- What is average delivery time?
- Which states, sellers, and categories have high late-delivery rates?
- Which stage consumes the most time: approval, handling, or transit?
- Is distance associated with delay?

### Customer-Experience Questions
- What is average review score?
- What percentage of reviews are positive or negative?
- How do reviews differ between on-time and late orders?
- Which sellers and categories have poor ratings?

### Seller and Category Questions
- Which sellers generate the highest GMV?
- Which sellers combine strong GMV with poor delivery performance?
- Which categories have high freight ratios?
- Which categories have strong ratings but low volume?

### Payments Questions
- Which payment types are most common?
- What is average installment count?
- Are payment totals consistent with item and freight totals?

## Out of Scope
- Profit without cost data
- Inventory analysis without stock data
- Real-time tracking
- Causal claims
- Production machine-learning deployment
- Exact carrier analysis without carrier information

## Important Metric Definitions
- **Gross Merchandise Value (GMV):** Sum of item price. (Do not call GMV profit or net revenue).
- **Freight Value:** Sum of freight_value.
- **Total Customer Order Value:** GMV + Freight Value.
- **Delivery Time:** Delivered Customer Date - Purchase Date.
- **Promised Delivery Time:** Estimated Delivery Date - Purchase Date.
- **Delay Days:** Actual Delivery Date - Estimated Delivery Date. (Negative: early delivery, Zero: delivered on the estimated date, Positive: late delivery).
- **On-Time Delivery:** Actual Delivery Date <= Estimated Delivery Date.
- **Review Groups:** Positive (score 4 or 5), Neutral (score 3), Negative (score 1 or 2).

## Source Tables and Grain
- **olist_orders_dataset.csv:** One row per order (Status and timestamps)
- **olist_order_items_dataset.csv:** One row per order item (Product, seller, price, freight)
- **olist_customers_dataset.csv:** One row per order customer ID (Customer identity and location)
- **olist_products_dataset.csv:** One row per product (Category and dimensions)
- **olist_sellers_dataset.csv:** One row per seller (Seller and location)
- **olist_order_payments_dataset.csv:** One row per payment sequence (Payment type and installments)
- **olist_order_reviews_dataset.csv:** One review record (Review score and comments)
- **olist_geolocation_dataset.csv:** Multiple rows per ZIP prefix (Latitude and longitude)
- **product_category_name_translation.csv:** One row per category (Category translation)
