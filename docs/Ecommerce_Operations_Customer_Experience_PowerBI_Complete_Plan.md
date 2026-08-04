# Enterprise E-Commerce Operations and Customer Experience Control Tower
## Complete End-to-End Power BI Project Build Plan

**Recommended resume title:** Enterprise E-Commerce Operations and Customer Experience Control Tower  
**Level:** Intermediate to advanced  
**Primary dashboard:** Microsoft Power BI  
**Recommended dataset:** Brazilian E-Commerce Public Dataset by Olist  
**Main domains:** E-commerce, order operations, delivery performance, seller performance, customer experience, payments, freight, geography, and executive reporting

---

# 1. Why This Project Is Stronger

This project is stronger than a normal sales dashboard because it demonstrates:

- Multi-table relational data analysis
- Source profiling across several CSV files
- Fact and dimension modeling
- Power Query transformations
- Python-based cleaning and validation
- SQL database implementation
- Advanced DAX measures
- Delivery SLA analysis
- Customer-review analysis
- Seller and category scorecards
- Geographic and freight analysis
- Decomposition Tree root-cause exploration
- Key Influencers analysis where appropriate
- What-If scenario analysis
- Drill-through and report-page tooltips
- Field parameters, bookmarks, and navigation
- KPI reconciliation across Python, SQL, and Power BI
- Optional row-level security and mobile layout

The final report should work like an operations control tower that answers:

1. What is happening?
2. Where is the problem?
3. Why might it be happening?
4. Which sellers, categories, states, and order stages are affected?
5. What action should management take?

---

# 2. Final Project Deliverables

At completion, the repository should contain:

1. Preserved raw source files
2. Source inventory and grain document
3. Data-quality audit
4. Cleaned staging tables
5. Final fact and dimension tables
6. Six Python notebooks
7. SQL database and at least 30 business queries
8. Power BI star schema
9. Reusable DAX measure library
10. Five main dashboard pages
11. Seller and order drill-through pages
12. Tooltip pages
13. Hidden QA and reconciliation page
14. Business-insights report
15. Complete GitHub README
16. Dashboard screenshots
17. Resume-ready project bullets
18. Interview-preparation notes

---

# 3. Business Scenario

An e-commerce marketplace connects customers, sellers, products, logistics, payments, and reviews. Its data is stored in disconnected tables, making it difficult to monitor order value, delivery performance, customer satisfaction, seller quality, freight, payments, and geographical operations.

The proposed control tower should allow management to:

- Monitor orders and Gross Merchandise Value
- Track delivered, cancelled, unavailable, and in-progress orders
- Measure on-time and late-delivery performance
- Compare promised and actual delivery durations
- Identify sellers, categories, and states with poor fulfillment
- Analyze freight and delivery-distance patterns
- Track review scores and customer satisfaction
- Identify segments associated with low reviews
- Build seller scorecards
- Investigate individual orders and sellers
- Evaluate operational targets using What-If scenarios

---

# 4. Important Metric Definitions

## 4.1 Gross Merchandise Value

```text
GMV = Sum of item price
```

Do not call GMV profit or net revenue.

## 4.2 Freight Value

```text
Freight Value = Sum of freight_value
```

## 4.3 Total Customer Order Value

```text
Total Customer Order Value = GMV + Freight Value
```

## 4.4 Delivery Time

```text
Delivery Time = Delivered Customer Date - Purchase Date
```

## 4.5 Promised Delivery Time

```text
Promised Delivery Time = Estimated Delivery Date - Purchase Date
```

## 4.6 Delay Days

```text
Delay Days = Actual Delivery Date - Estimated Delivery Date
```

- Negative: early delivery
- Zero: delivered on the estimated date
- Positive: late delivery

## 4.7 On-Time Delivery

```text
Actual Delivery Date <= Estimated Delivery Date
```

## 4.8 Review Groups

Use a documented analytical grouping:

- Positive: score 4 or 5
- Neutral: score 3
- Negative: score 1 or 2

---

# 5. Dataset Tables

The dataset normally contains these related files:

| File | Grain | Main use |
|---|---|---|
| `olist_orders_dataset.csv` | One row per order | Status and timestamps |
| `olist_order_items_dataset.csv` | One row per order item | Product, seller, price, freight |
| `olist_customers_dataset.csv` | One row per order customer ID | Customer identity and location |
| `olist_products_dataset.csv` | One row per product | Category and dimensions |
| `olist_sellers_dataset.csv` | One row per seller | Seller and location |
| `olist_order_payments_dataset.csv` | One row per payment sequence | Payment type and installments |
| `olist_order_reviews_dataset.csv` | One review record | Review score and comments |
| `olist_geolocation_dataset.csv` | Multiple rows per ZIP prefix | Latitude and longitude |
| `product_category_name_translation.csv` | One row per category | Category translation |

Verify all file names, columns, and row counts after downloading.

---

# 6. Critical Data-Model Challenge

The source tables have different grains:

- Orders: one row per order
- Items: one row per order item
- Payments: one order can have multiple payment rows
- Reviews: one order can have one or more review records
- Geolocation: one ZIP prefix can have multiple coordinates

A direct join such as:

```text
Order Items × Payments × Reviews
```

can multiply rows and produce incorrect GMV, freight, payment, and review metrics.

Therefore:

- Aggregate payments to order level before joining
- Aggregate reviews to order level before joining
- Keep order facts separate from item facts
- Document the grain of every table
- Test totals before and after each join

---

# 7. Technology Stack

| Module | Tool |
|---|---|
| Initial inspection | Excel |
| Data profiling | Python and Pandas |
| Transformation | Python and Power Query |
| Numerical work | NumPy |
| EDA | Matplotlib |
| Database | SQLite or MySQL |
| Database access | SQLAlchemy or `sqlite3` |
| Data model | Power BI |
| Measures | DAX |
| Root-cause analysis | Decomposition Tree |
| Driver exploration | Key Influencers |
| Scenario analysis | What-If Parameter |
| Version control | Git |
| Portfolio | GitHub |
| Documentation | Markdown and PDF |

---

# 8. Repository Structure

```text
ecommerce-operations-customer-experience-control-tower/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   ├── olist_orders_dataset.csv
│   │   ├── olist_order_items_dataset.csv
│   │   ├── olist_customers_dataset.csv
│   │   ├── olist_products_dataset.csv
│   │   ├── olist_sellers_dataset.csv
│   │   ├── olist_order_payments_dataset.csv
│   │   ├── olist_order_reviews_dataset.csv
│   │   ├── olist_geolocation_dataset.csv
│   │   └── product_category_name_translation.csv
│   │
│   ├── staging/
│   │   ├── stg_orders.csv
│   │   ├── stg_order_items.csv
│   │   ├── stg_customers.csv
│   │   ├── stg_products.csv
│   │   ├── stg_sellers.csv
│   │   ├── stg_payments.csv
│   │   ├── stg_reviews.csv
│   │   └── stg_geolocation.csv
│   │
│   └── processed/
│       ├── fact_orders.csv
│       ├── fact_order_items.csv
│       ├── fact_payments.csv
│       ├── fact_reviews.csv
│       ├── dim_customers.csv
│       ├── dim_products.csv
│       ├── dim_sellers.csv
│       ├── dim_customer_geography.csv
│       ├── dim_seller_geography.csv
│       ├── seller_scorecard.csv
│       ├── customer_summary.csv
│       └── data_quality_report.csv
│
├── notebooks/
│   ├── 01_source_inventory_and_data_profiling.ipynb
│   ├── 02_data_cleaning_and_staging.ipynb
│   ├── 03_data_integration_and_feature_engineering.ipynb
│   ├── 04_exploratory_business_analysis.ipynb
│   ├── 05_delivery_and_customer_experience_analysis.ipynb
│   └── 06_kpi_reconciliation_and_validation.ipynb
│
├── src/
│   ├── config.py
│   ├── profiling.py
│   ├── cleaning.py
│   ├── integration.py
│   ├── feature_engineering.py
│   ├── geospatial.py
│   ├── validation.py
│   └── utils.py
│
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_create_staging_tables.sql
│   ├── 03_create_analytics_schema.sql
│   ├── 04_load_data.sql
│   ├── 05_business_analysis_queries.sql
│   └── 06_validation_queries.sql
│
├── database/
│   └── ecommerce_control_tower.db
│
├── powerbi/
│   ├── ecommerce_operations_control_tower.pbix
│   ├── data_model.png
│   ├── page_1_executive_command_center.png
│   ├── page_2_delivery_sla_operations.png
│   ├── page_3_customer_experience.png
│   ├── page_4_seller_product_performance.png
│   ├── page_5_root_cause_scenario.png
│   ├── seller_drillthrough.png
│   └── order_drillthrough.png
│
├── reports/
│   ├── data_quality_report.md
│   ├── executive_insights_report.md
│   └── executive_insights_report.pdf
│
├── docs/
│   ├── business_requirements.md
│   ├── source_inventory.md
│   ├── relationship_and_grain_document.md
│   ├── source_to_target_mapping.md
│   ├── data_dictionary.md
│   ├── metric_definitions.md
│   ├── star_schema_design.md
│   ├── dashboard_user_guide.md
│   ├── qa_reconciliation.md
│   └── interview_notes.md
│
└── assets/
    ├── architecture_diagram.png
    ├── workflow_diagram.png
    └── dashboard_cover.png
```

---

# 9. Architecture

```text
Raw CSV Files
      │
      ▼
Source Inventory and Grain Analysis
      │
      ▼
Python Data Profiling
      │
      ▼
Cleaning and Staging Layer
      │
      ▼
Integration and Aggregation
      │
      ├── Order fact
      ├── Order-item fact
      ├── Payment fact
      ├── Review fact
      ├── Customer dimension
      ├── Product dimension
      ├── Seller dimension
      └── Geography dimensions
      │
      ▼
SQL Analytics Database
      │
      ▼
Power Query
      │
      ▼
Power BI Star Schema
      │
      ├── DAX
      ├── Drill-through
      ├── Tooltips
      ├── Field parameters
      ├── What-If analysis
      ├── Decomposition Tree
      └── Optional RLS
      │
      ▼
Executive Control Tower
```

---

# 10. Phase 0 — Business Requirements

Create `docs/business_requirements.md`.

## Stakeholders

- E-commerce operations manager
- Logistics manager
- Seller-management team
- Customer-experience team
- Category manager
- Commercial analyst
- Executive management

## Executive questions

- How many orders were placed?
- What is GMV?
- What is average order value?
- How are orders and GMV trending?
- What percentage of orders were delivered, cancelled, or unavailable?

## Delivery questions

- What is the on-time delivery rate?
- What is average delivery time?
- Which states, sellers, and categories have high late-delivery rates?
- Which stage consumes the most time: approval, handling, or transit?
- Is distance associated with delay?

## Customer-experience questions

- What is average review score?
- What percentage of reviews are positive or negative?
- How do reviews differ between on-time and late orders?
- Which sellers and categories have poor ratings?

## Seller and category questions

- Which sellers generate the highest GMV?
- Which sellers combine strong GMV with poor delivery performance?
- Which categories have high freight ratios?
- Which categories have strong ratings but low volume?

## Payments questions

- Which payment types are most common?
- What is average installment count?
- Are payment totals consistent with item and freight totals?

## Out of scope

- Profit without cost data
- Inventory analysis without stock data
- Real-time tracking
- Causal claims
- Production machine-learning deployment
- Exact carrier analysis without carrier information

## Phase acceptance criteria

- Every KPI has a definition.
- Every visual maps to a business question.
- Table grain is documented.
- No unsupported metric is promised.

---

# 11. Phase 1 — Environment Setup

```bash
python -m venv .venv
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install:

```bash
pip install pandas numpy matplotlib sqlalchemy jupyter openpyxl geopy
```

`requirements.txt`:

```text
pandas
numpy
matplotlib
sqlalchemy
jupyter
openpyxl
geopy
```

Initialize Git:

```bash
git init
git add .
git commit -m "Initialize e-commerce control tower project"
```

Acceptance criteria:

- Jupyter works.
- Raw data is stored under `data/raw/`.
- Power BI Desktop is installed.
- Git repository is initialized.
- Raw files remain unchanged.

---

# 12. Phase 2 — Source Inventory and Grain Analysis

Create `source_inventory.md` and `relationship_and_grain_document.md`.

For each file, record:

- File name
- Row count
- Column count
- Candidate primary key
- Foreign keys
- Grain
- Duplicate-key count
- Null count
- Date range
- Join risks
- Planned target table

Example:

| Table | Grain | Candidate key | Relationship key |
|---|---|---|---|
| Orders | One row per order | `order_id` | `order_id` |
| Order Items | One row per order item | `order_id + order_item_id` | `order_id` |
| Payments | One row per payment sequence | `order_id + payment_sequential` | `order_id` |
| Reviews | One review record | `review_id` | `order_id` |
| Customers | One row per customer order ID | `customer_id` | `customer_id` |
| Products | One row per product | `product_id` | `product_id` |
| Sellers | One row per seller | `seller_id` | `seller_id` |
| Geolocation | Multiple rows per ZIP prefix | None in raw form | ZIP prefix |

Acceptance criteria:

- Grain is known for every source.
- Key uniqueness is tested.
- Join risks are documented.
- Order-level and item-level metrics are separated.

---

# 13. Phase 3 — Data Profiling

Create `01_source_inventory_and_data_profiling.ipynb`.

Generic checks:

```python
df.shape
df.head()
df.info()
df.describe(include="all")
df.isnull().sum()
df.duplicated().sum()
df.nunique()
```

## Orders checks

- Unique order IDs
- Status distribution
- Missing timestamps
- Purchase-date range
- Delivered orders without delivery date
- Estimated delivery before purchase
- Timestamp-sequence errors

## Order-items checks

- Duplicate `order_id + order_item_id`
- Missing product or seller IDs
- Price less than or equal to zero
- Freight below zero
- Items per order
- Sellers per order

## Customers checks

- Unique customer ID
- Relationship between `customer_id` and `customer_unique_id`
- Missing location fields
- Repeat unique customers

## Products checks

- Unique product ID
- Missing category
- Missing or invalid dimensions
- Missing weight
- Translation coverage

## Sellers checks

- Unique seller ID
- Missing state, city, or ZIP
- Seller count by state

## Payments checks

- Duplicate payment sequence
- Negative payment values
- Installment distribution
- Orders with multiple payment records
- Payment total per order

## Reviews checks

- Score distribution
- Duplicate review IDs
- Multiple reviews per order
- Missing dates
- Comment availability

## Geolocation checks

- Duplicate ZIP prefixes
- Invalid latitude and longitude
- Multiple coordinates per ZIP prefix
- Missing city and state

Create a data-quality table:

| Table | Rule | Count | Percentage | Severity | Treatment |
|---|---|---:|---:|---|---|

Acceptance criteria:

- Every source is profiled.
- Every key is tested.
- Quality issues are saved to CSV.
- No merge occurs before profiling.

---

# 14. Phase 4 — Cleaning and Staging

Create `02_data_cleaning_and_staging.ipynb`.

## Common rules

- Convert names to snake_case
- Trim text
- Convert dates safely
- Convert numbers safely
- Remove exact duplicate rows
- Preserve valid one-to-many relationships
- Add quality flags
- Save staged files

## Orders

Create flags:

```text
missing_approval_flag
missing_carrier_flag
missing_delivery_flag
invalid_timestamp_sequence_flag
delivered_status_mismatch_flag
```

## Order items

Validate:

```text
price > 0
freight_value >= 0
order_item_id > 0
```

Create:

```text
item_total_value = price + freight_value
freight_to_price_ratio = freight_value / price
```

## Customers

Preserve:

- `customer_id` for order relationship
- `customer_unique_id` for repeat-customer analysis

## Products

- Join English category translation
- Keep the original category
- Validate dimensions and weight
- Create product volume
- Create size bands

```text
product_volume_cm3 = length × height × width
```

## Payments

Aggregate to order level:

```text
order_id
payment_value_total
payment_installments_max
payment_record_count
primary_payment_type
multi_payment_flag
```

Define primary payment type as the payment type representing the largest payment value, or use another documented rule.

## Reviews

Aggregate to order level:

```text
order_id
review_score
review_count
review_comment_flag
review_response_hours
```

For multiple reviews, use a documented rule such as average review score or latest review.

## Geolocation

Aggregate ZIP prefixes:

```python
geo_zip = (
    geolocation.groupby("geolocation_zip_code_prefix", as_index=False)
    .agg(
        latitude=("geolocation_lat", "median"),
        longitude=("geolocation_lng", "median"),
        city=("geolocation_city", "first"),
        state=("geolocation_state", "first"),
    )
)
```

Acceptance criteria:

- Correct data types
- Documented aggregation rules
- One staged output per source
- No unexplained row removal
- Geolocation has one chosen row per ZIP prefix

---

# 15. Phase 5 — Integration and Feature Engineering

Create `03_data_integration_and_feature_engineering.ipynb`.

## Order-level fact

Start from orders and join:

- Customer dimension
- Order-level payment summary
- Order-level review summary
- Order-item summary

Order-item summary per order:

```text
item_count
unique_product_count
unique_seller_count
gmv
freight_value
total_order_value
average_item_price
maximum_item_price
average_freight_to_price_ratio
```

## Item-level fact

Keep one row per order item and join:

- Order status and timestamps
- Product
- Seller
- Customer state
- Delivery features

## Delivery features

```python
orders["approval_hours"] = (
    orders["approved_timestamp"] - orders["purchase_timestamp"]
).dt.total_seconds() / 3600

orders["handling_days"] = (
    orders["carrier_timestamp"] - orders["approved_timestamp"]
).dt.total_seconds() / 86400

orders["transit_days"] = (
    orders["delivered_customer_timestamp"] - orders["carrier_timestamp"]
).dt.total_seconds() / 86400

orders["delivery_days"] = (
    orders["delivered_customer_timestamp"] - orders["purchase_timestamp"]
).dt.total_seconds() / 86400

orders["promised_delivery_days"] = (
    orders["estimated_delivery_timestamp"] - orders["purchase_timestamp"]
).dt.total_seconds() / 86400

orders["delay_days"] = (
    orders["delivered_customer_timestamp"] - orders["estimated_delivery_timestamp"]
).dt.total_seconds() / 86400
```

Create:

```text
delivery_status = Early / On Time / Late / Not Delivered
late_delivery_flag
severe_delay_flag
delay_band
```

Suggested delay bands:

- Early or on time
- 1–3 days late
- 4–7 days late
- 8+ days late

## Review features

```text
review_group
low_review_flag
high_review_flag
```

## Customer summary

Using `customer_unique_id`, calculate:

- First purchase date
- Last purchase date
- Order count
- Total GMV
- Average order value
- Repeat-customer flag
- Average review score
- Average delivery days
- Late-order count

## Seller scorecard

For each seller:

- Orders
- Items sold
- GMV
- Freight value
- Average review score
- On-time rate
- Late-delivery rate
- Average delay days
- Customer states served
- Categories sold
- Freight-to-price ratio

## Optional distance feature

Calculate approximate Haversine distance between seller and customer ZIP-prefix coordinates.

Create bands:

- 0–100 km
- 101–500 km
- 501–1,000 km
- 1,001–2,000 km
- 2,000+ km

Document that the result is approximate.

Acceptance criteria:

- Order fact remains one row per order.
- Item fact remains one row per item.
- Payment joins do not multiply rows.
- Review joins do not multiply rows.
- Repeat customers use `customer_unique_id`.
- Derived fields have definitions.

---

# 16. Phase 6 — SQL Database

Recommended tables:

## Facts

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

## Dimensions

- `dim_date`
- `dim_customer`
- `dim_product`
- `dim_seller`
- `dim_customer_geography`
- `dim_seller_geography`
- `dim_order_status`
- `dim_payment_type`

Write at least 30 queries.

## Executive

1. Total orders
2. Delivered orders
3. Cancelled orders
4. GMV
5. Freight value
6. Total customer order value
7. Average order value
8. Items per order
9. Monthly orders
10. Monthly GMV

## Delivery

11. On-time rate
12. Late rate
13. Average delivery days
14. Average delay days
15. State-level delivery
16. Seller-state delivery
17. Category delivery
18. Severe delays
19. Handling time
20. Transit time

## Customer experience

21. Average review score
22. Positive-review rate
23. Negative-review rate
24. Review by delivery status
25. Review by delay band
26. Review by category
27. Review by seller
28. Low-review high-value orders

## Seller and category

29. Top sellers by GMV
30. Seller late-delivery ranking
31. Seller review ranking
32. High-GMV poor-service sellers
33. Category GMV
34. Category freight ratio
35. Category late rate
36. Category satisfaction rate

## Customer and payment

37. Repeat-customer rate
38. Top repeat customers
39. Payment-type distribution
40. Installments
41. Multi-payment orders
42. Payment reconciliation

## Advanced

43. Seller Pareto contribution
44. Category Pareto contribution
45. Month-over-month GMV
46. Rolling three-month GMV
47. Seller rank within state
48. Distance-band performance
49. Root-cause candidate summary
50. Validation queries

Example on-time query:

```sql
SELECT
    COUNT(*) AS delivered_orders,
    SUM(
        CASE
            WHEN delivered_customer_date <= estimated_delivery_date
            THEN 1 ELSE 0
        END
    ) AS on_time_orders,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN delivered_customer_date <= estimated_delivery_date
                THEN 1 ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS on_time_delivery_rate
FROM fact_orders
WHERE order_status = 'delivered'
  AND delivered_customer_date IS NOT NULL
  AND estimated_delivery_date IS NOT NULL;
```

Acceptance criteria:

- All queries execute.
- SQL totals match Python.
- CTEs and window functions are included.
- Rankings use minimum-volume thresholds where needed.
- Every query includes a business-purpose comment.

---

# 17. Phase 7 — Exploratory Analysis

Create:

- `04_exploratory_business_analysis.ipynb`
- `05_delivery_and_customer_experience_analysis.ipynb`

## Executive analysis

- Orders over time
- GMV over time
- Order statuses
- Average order value
- Items per order
- Freight contribution
- Customer-state distribution
- Repeat customers

## Delivery analysis

- On-time rate
- Late rate
- Delivery-duration distribution
- Promised versus actual duration
- Handling and transit time
- State-level delay
- Seller-level delay
- Category-level delay
- Distance-band delay

## Customer-experience analysis

- Review-score distribution
- Positive and negative review rates
- Review versus delivery status
- Review versus delay days
- Review versus freight ratio
- Review versus category
- Review versus seller
- Review versus distance

## Seller analysis

- GMV
- Orders
- On-time rate
- Review score
- Delay days
- Freight ratio
- Geographic reach
- Category reach

Create a seller quadrant:

- High GMV / High service
- High GMV / Low service
- Low GMV / High service
- Low GMV / Low service

## Product and category analysis

- GMV
- Items
- Freight ratio
- Product size and freight
- Delivery time
- Review score
- Cancellation or unavailability exposure

## Payment analysis

- Payment types
- Installments
- Payment value
- Multiple-payment orders
- Payment reconciliation

Acceptance criteria:

- Every chart answers a business question.
- Rates include suitable denominators.
- Small samples are treated carefully.
- No causation is claimed.
- EDA results match SQL.

---

# 18. Phase 8 — Power Query

Recommended queries:

## Staging queries

- `stg_Orders`
- `stg_OrderItems`
- `stg_Customers`
- `stg_Products`
- `stg_Sellers`
- `stg_Payments`
- `stg_Reviews`
- `stg_Geography`
- `stg_CategoryTranslation`

## Final model queries

- `FactOrders`
- `FactOrderItems`
- `FactPayments`
- `FactReviews`
- `DimCustomer`
- `DimProduct`
- `DimSeller`
- `DimCustomerGeography`
- `DimSellerGeography`
- `DimDate`
- `DimOrderStatus`

Power Query tasks:

- Confirm types
- Rename fields
- Remove unused columns
- Use query references
- Disable load for staging queries
- Add readable step names
- Add error checks
- Use a configurable folder path parameter

Acceptance criteria:

- No refresh errors.
- Staging queries have load disabled.
- Final tables have correct types.
- Folder path can be changed.
- Power Query logic matches Python definitions.

---

# 19. Phase 9 — Power BI Star Schema

Recommended relationships:

```text
DimDate 1 ─────── * FactOrders
DimDate 1 ─────── * FactOrderItems
DimCustomer 1 ─── * FactOrders
DimProduct 1 ───── * FactOrderItems
DimSeller 1 ────── * FactOrderItems
DimOrderStatus 1 ─ * FactOrders
```

Use separate geography dimensions for customer and seller roles.

## Date roles

The order table contains:

- Purchase date
- Approval date
- Carrier date
- Delivery date
- Estimated delivery date

Use one active relationship for purchase date and inactive relationships for the other dates. Use `USERELATIONSHIP` in DAX where required.

Model rules:

- One-to-many relationships
- Single-direction filtering by default
- No unnecessary bidirectional filters
- No direct many-to-many relation
- Dedicated Measures table
- Technical keys hidden
- Date table marked
- Item and order measures kept separate

Acceptance criteria:

- No ambiguous relationship.
- Order counts are not inflated by item rows.
- Payment totals are not multiplied.
- Date intelligence works.
- Model image is exported.

---

# 20. Phase 10 — DAX Measure Library

## Executive

```DAX
Total Orders =
DISTINCTCOUNT(FactOrders[OrderID])
```

```DAX
Delivered Orders =
CALCULATE(
    [Total Orders],
    FactOrders[OrderStatus] = "delivered"
)
```

```DAX
Cancelled Orders =
CALCULATE(
    [Total Orders],
    FactOrders[OrderStatus] = "canceled"
)
```

```DAX
GMV =
SUM(FactOrderItems[Price])
```

```DAX
Freight Value =
SUM(FactOrderItems[FreightValue])
```

```DAX
Total Customer Order Value =
[GMV] + [Freight Value]
```

```DAX
Average Order Value =
DIVIDE([GMV], [Total Orders], 0)
```

```DAX
Items Sold =
COUNTROWS(FactOrderItems)
```

```DAX
Average Items per Order =
DIVIDE([Items Sold], [Total Orders], 0)
```

## Status

```DAX
Order Completion Rate =
DIVIDE([Delivered Orders], [Total Orders], 0)
```

```DAX
Cancellation Rate =
DIVIDE([Cancelled Orders], [Total Orders], 0)
```

## Delivery

```DAX
On-Time Delivered Orders =
CALCULATE(
    [Delivered Orders],
    FactOrders[LateDeliveryFlag] = 0
)
```

```DAX
Late Delivered Orders =
CALCULATE(
    [Delivered Orders],
    FactOrders[LateDeliveryFlag] = 1
)
```

```DAX
On-Time Delivery Rate =
DIVIDE([On-Time Delivered Orders], [Delivered Orders], 0)
```

```DAX
Late Delivery Rate =
DIVIDE([Late Delivered Orders], [Delivered Orders], 0)
```

```DAX
Average Delivery Days =
AVERAGE(FactOrders[DeliveryDays])
```

```DAX
Average Delay Days =
AVERAGE(FactOrders[DelayDays])
```

## Reviews

```DAX
Reviewed Orders =
CALCULATE(
    [Total Orders],
    NOT ISBLANK(FactOrders[ReviewScore])
)
```

```DAX
Average Review Score =
AVERAGE(FactOrders[ReviewScore])
```

```DAX
Positive Reviews =
CALCULATE(
    [Reviewed Orders],
    FactOrders[ReviewScore] >= 4
)
```

```DAX
Negative Reviews =
CALCULATE(
    [Reviewed Orders],
    FactOrders[ReviewScore] <= 2
)
```

```DAX
Positive Review Rate =
DIVIDE([Positive Reviews], [Reviewed Orders], 0)
```

```DAX
Negative Review Rate =
DIVIDE([Negative Reviews], [Reviewed Orders], 0)
```

## Customers

```DAX
Unique Customers =
DISTINCTCOUNT(DimCustomer[CustomerUniqueID])
```

```DAX
Repeat Customers =
COUNTROWS(
    FILTER(
        VALUES(DimCustomer[CustomerUniqueID]),
        CALCULATE(DISTINCTCOUNT(FactOrders[OrderID])) > 1
    )
)
```

```DAX
Repeat Customer Rate =
DIVIDE([Repeat Customers], [Unique Customers], 0)
```

## Freight

```DAX
Freight to GMV Ratio =
DIVIDE([Freight Value], [GMV], 0)
```

```DAX
Average Freight per Order =
DIVIDE([Freight Value], [Total Orders], 0)
```

## Time intelligence

```DAX
Previous Month GMV =
CALCULATE(
    [GMV],
    DATEADD(DimDate[Date], -1, MONTH)
)
```

```DAX
MoM GMV Growth % =
DIVIDE(
    [GMV] - [Previous Month GMV],
    [Previous Month GMV],
    0
)
```

```DAX
Rolling 3 Month GMV =
CALCULATE(
    [GMV],
    DATESINPERIOD(
        DimDate[Date],
        MAX(DimDate[Date]),
        -3,
        MONTH
    )
)
```

Alternate relationship example:

```DAX
Delivered Orders by Delivery Date =
CALCULATE(
    [Delivered Orders],
    USERELATIONSHIP(
        DimDate[Date],
        FactOrders[DeliveredCustomerDate]
    )
)
```

---

# 21. Dashboard Page 1 — Executive Command Center

## KPIs

- Total Orders
- GMV
- Average Order Value
- Delivered Orders
- On-Time Delivery Rate
- Average Review Score
- Cancellation Rate
- Freight-to-GMV Ratio

## Visuals

1. Monthly GMV and order trend
2. Order-status breakdown
3. GMV by customer state
4. Top categories by GMV
5. On-time versus late orders
6. Review distribution
7. Freight contribution
8. Executive KPI status table

## Slicers

- Date
- Customer state
- Seller state
- Category
- Order status
- Delivery status
- Review group
- Payment type

## Features

- Reset filters
- Navigation
- Dynamic title
- Selected-filter summary
- Bookmarks for commercial and operations views

---

# 22. Dashboard Page 2 — Delivery and SLA Operations

## KPIs

- Delivered Orders
- On-Time Delivery Rate
- Late Delivery Rate
- Average Delivery Days
- Average Delay Days
- Severe Delays
- Average Handling Days
- Average Transit Days

## Visuals

1. On-time rate by month
2. Delay-days distribution
3. Delivery by customer state
4. Delivery by seller state
5. Category late-delivery rate
6. Handling versus transit time
7. Distance band versus delivery performance
8. Severe-delay order table
9. Decomposition Tree

## Decomposition Tree

Analyze:

```text
Late Delivered Orders
```

Explain by:

- Customer state
- Seller state
- Category
- Distance band
- Freight band
- Item-count band
- Purchase month
- Seller

---

# 23. Dashboard Page 3 — Customer Experience

## KPIs

- Reviewed Orders
- Average Review Score
- Positive Review Rate
- Negative Review Rate
- Review Comment Rate
- Average Response Time

## Visuals

1. Review-score distribution
2. Review by delivery status
3. Review by delay band
4. Negative-review rate by category
5. Negative-review rate by seller
6. Review versus freight ratio
7. Review versus distance band
8. Low-review high-value orders
9. Key Influencers for low-review flag

Possible Key Influencers fields:

- Late delivery flag
- Delay band
- Product category
- Customer state
- Seller state
- Freight band
- Distance band
- Item-count band
- Payment type
- Installment band

Interpret results as associations, not proof of causation.

---

# 24. Dashboard Page 4 — Seller and Product Performance

## KPIs

- Active Sellers
- Active Products
- Categories
- GMV per Seller
- Average Seller Review Score
- Seller On-Time Rate

## Visuals

1. Seller performance quadrant
2. Top sellers by GMV
3. Sellers with high late rate
4. Sellers with low review score
5. Category GMV and review score
6. Category freight ratio
7. Category on-time rate
8. Seller detail matrix
9. Seller Pareto chart
10. Category Pareto chart

Seller quadrant:

- X-axis: GMV
- Y-axis: On-Time Delivery Rate or Review Score
- Bubble size: Orders

Use a minimum order threshold to avoid unfair rankings.

---

# 25. Dashboard Page 5 — Root Cause and Scenario Analysis

## Components

- Metric field parameter
- Dimension field parameter
- Decomposition Tree
- What-If parameter
- Scenario KPI cards
- Dynamic title
- Selected-segment table

## Metric selector

- GMV
- Orders
- On-Time Delivery Rate
- Late Delivery Rate
- Average Review Score
- Negative Review Rate
- Freight-to-GMV Ratio

## Dimension selector

- Customer state
- Seller state
- Category
- Seller
- Payment type
- Distance band
- Delivery status

## What-If parameter

Create:

```text
Target On-Time Delivery Rate
```

Range:

```text
70% to 100%, in 1% steps
```

```DAX
On-Time Target Gap =
[On-Time Delivery Rate]
- [Target On-Time Delivery Rate Value]
```

```DAX
Orders Needed to Reach Target =
VAR Delivered = [Delivered Orders]
VAR OnTime = [On-Time Delivered Orders]
VAR TargetRate = [Target On-Time Delivery Rate Value]
RETURN
MAX(
    0,
    ROUNDUP(TargetRate * Delivered - OnTime, 0)
)
```

Describe this as a simplified operational scenario, not a forecast.

---

# 26. Drill-Through Pages

## Seller drill-through

- Seller ID
- GMV
- Orders
- Items
- Categories
- Customer states
- On-time rate
- Delay days
- Review score
- Freight ratio
- Monthly trend
- Delayed-order table

## Order drill-through

- Order ID
- Purchase date
- Status
- Customer state
- Sellers
- Products
- Item count
- GMV
- Freight
- Payment method
- Installments
- Estimated delivery
- Actual delivery
- Delay days
- Review score

Add a working Back button.

---

# 27. Tooltip Pages

Create:

## Seller tooltip

- Orders
- GMV
- On-time rate
- Review score
- Freight ratio

## Category tooltip

- Orders
- GMV
- Average item price
- On-time rate
- Review score

## Geography tooltip

- Orders
- GMV
- Delivery days
- Late rate
- Review score

---

# 28. Optional Enterprise Features

## Row-Level Security

Create a dummy security mapping:

```text
user_email
seller_state
```

Demonstrate a seller-state manager role. Use dummy email addresses only.

## Mobile layout

Create a mobile version of the executive page.

## Performance optimization

- Remove unused columns
- Use star schema
- Avoid unnecessary calculated columns
- Limit bidirectional relationships
- Use Performance Analyzer
- Reduce high-cardinality fields in visuals

## Refresh process

1. Replace source files
2. Run Python pipeline
3. Validate outputs
4. Refresh Power BI
5. Review QA page
6. Publish

---

# 29. Dashboard UX Standards

- Use 16:9 layout
- Place KPIs at the top
- Keep filters in a dedicated panel
- Use consistent navigation
- Maintain equal spacing
- Use descriptive titles
- Format GMV and freight as BRL
- Use one decimal place for rates
- Avoid color-only communication
- Add alt text
- Test tab order
- Avoid overcrowding

Navigation buttons:

- Home
- Executive
- Delivery
- Customer Experience
- Seller and Product
- Root Cause
- Reset Filters
- Help

---

# 30. Testing and Reconciliation

Create `06_kpi_reconciliation_and_validation.ipynb` and a hidden Power BI QA page.

| KPI | Python | SQL | Power BI | Match |
|---|---:|---:|---:|---|
| Total orders | | | | |
| Delivered orders | | | | |
| Cancelled orders | | | | |
| GMV | | | | |
| Freight | | | | |
| Average order value | | | | |
| On-time rate | | | | |
| Delivery days | | | | |
| Reviewed orders | | | | |
| Average review score | | | | |
| Unique customers | | | | |
| Active sellers | | | | |

## Join tests

```text
Raw item rows = Final item fact rows
```

unless exclusions are documented.

```text
GMV before joins = GMV after joins
```

## Timestamp tests

- Purchase <= approval
- Approval <= carrier handoff when available
- Carrier <= delivery when delivered
- Purchase <= estimated delivery
- Delivery denominator includes only delivered orders with valid dates

## Dashboard tests

- Slicers work
- Reset button works
- Bookmarks behave correctly
- Drill-through works
- Tooltips work
- Field parameters update visuals and titles
- What-If parameter works
- Decomposition Tree uses correct fields
- Key Influencers target is correct
- No unexplained blank visuals

---

# 31. Business Insights Report

Create `executive_insights_report.md`, then export to PDF.

Sections:

1. Executive summary
2. Business context
3. Dataset and source tables
4. Grain and data model
5. Data-quality findings
6. Cleaning process
7. KPI definitions
8. Commercial performance
9. Delivery performance
10. Customer experience
11. Seller performance
12. Product-category performance
13. Geographic performance
14. Payment behavior
15. Root-cause observations
16. Recommendations
17. Limitations
18. Future improvements

Recommendation format:

- Observed issue
- Supporting KPI
- Affected segment
- Recommended action
- Measurement plan
- Limitation

Do not invent business impact.

---

# 32. Documentation

## README

```markdown
# Enterprise E-Commerce Operations and Customer Experience Control Tower

## Project Overview
## Business Problem
## Dataset
## Source Tables and Grain
## Technology Stack
## Architecture
## Data Quality Audit
## Cleaning and Staging
## Integration Strategy
## Feature Engineering
## SQL Analysis
## Power BI Star Schema
## DAX Measures
## Dashboard Pages
## Advanced Power BI Features
## Key Findings
## Recommendations
## Quality Assurance
## Limitations
## How to Run
## Screenshots
## Author
```

## Data dictionary

Include:

- Field
- Source table
- Target table
- Data type
- Grain
- Definition
- Transformation
- Null rule
- Example

## Source-to-target mapping

| Source field | Source table | Target field | Target table | Transformation |
|---|---|---|---|---|

## Metric documentation

Document:

- GMV
- Freight Value
- Total Customer Order Value
- Average Order Value
- Delivered Orders
- Cancellation Rate
- On-Time Rate
- Late Rate
- Delivery Days
- Delay Days
- Positive Review Rate
- Negative Review Rate
- Repeat Customer Rate
- Freight-to-GMV Ratio

---

# 33. Git Workflow

Suggested commits:

```text
Initialize project structure
Add source inventory and grain documentation
Complete source profiling
Add cleaning and staging pipeline
Build order and item facts
Add delivery and customer-experience features
Create SQL analytics schema
Add SQL queries
Build Power BI star schema
Add DAX measures
Complete executive and delivery pages
Complete customer-experience page
Complete seller and product page
Add root-cause and scenario page
Add drill-through and tooltips
Complete QA reconciliation
Add report and README
Finalize portfolio assets
```

Repository topics:

- `power-bi`
- `data-analysis`
- `ecommerce`
- `sql`
- `python`
- `dax`
- `power-query`
- `data-modeling`
- `customer-experience`
- `delivery-analytics`

---

# 34. Resume Entry

Use this only after completing the project and replacing general claims with actual verified results.

```text
Enterprise E-Commerce Operations and Customer Experience Control Tower
Python | SQL | Power BI | Power Query | DAX

• Profiled, cleaned, and integrated nine relational e-commerce datasets covering
  approximately 100,000 orders, customers, products, sellers, payments, reviews,
  geolocation, and delivery timestamps.

• Designed a Power BI star schema with separate order-level and item-level fact
  tables, role-playing date relationships, reusable DAX measures, and documented
  KPI definitions to prevent double counting across multi-grain sources.

• Developed a five-page operational control tower for GMV, order status,
  delivery SLA, customer reviews, seller performance, product categories,
  freight, and geographic analysis.

• Implemented drill-through, report-page tooltips, field parameters, What-If
  analysis, and root-cause exploration while reconciling critical KPIs across
  Python, SQL, and Power BI.
```

Add one actual finding after analysis:

```text
• Identified [verified seller/category/state] as an operational-priority segment
  based on an actual late-delivery rate of [value] and review score of [value].
```

---

# 35. Interview Questions

1. Why is this more complex than a sales dashboard?
2. What is the grain of the order-items table?
3. Why can items, payments, and reviews not be directly joined?
4. How did you prevent double counting?
5. What is GMV?
6. Why is GMV not profit?
7. How did you calculate on-time delivery?
8. What denominator did you use?
9. Why are there two customer IDs?
10. How did you identify repeat customers?
11. How did you aggregate geolocation?
12. What is a star schema?
13. Why did you use separate order and item facts?
14. What is an inactive relationship?
15. How did you use `USERELATIONSHIP`?
16. What is a measure?
17. How did you validate DAX?
18. What is a field parameter?
19. What is a What-If parameter?
20. How did Decomposition Tree help?
21. How should Key Influencers be interpreted?
22. What are the review-analysis limitations?
23. How did you compare sellers fairly?
24. What recommendation did you make?
25. What would you improve?

---

# 36. Suggested 14-Day Schedule

| Day | Work |
|---|---|
| 1 | Requirements, repository, source inventory |
| 2 | Profile orders, items, customers, and products |
| 3 | Profile sellers, payments, reviews, and geolocation |
| 4 | Cleaning and staging |
| 5 | Order and item integration |
| 6 | Delivery, customer, seller, and distance features |
| 7 | SQL database and core queries |
| 8 | Advanced SQL and validation |
| 9 | Power Query and star schema |
| 10 | DAX measure library |
| 11 | Executive and delivery dashboards |
| 12 | Customer-experience and seller dashboards |
| 13 | Root cause, scenarios, drill-through, and tooltips |
| 14 | QA, report, README, screenshots, and resume bullets |

Optional days:

- RLS demonstration
- Mobile layout
- Performance optimization
- Video walkthrough
- LinkedIn post

---

# 37. Final Acceptance Checklist

## Planning

- [ ] Business requirements exist
- [ ] Stakeholders are defined
- [ ] KPI definitions are written
- [ ] Out-of-scope items are documented

## Data inventory

- [ ] All files are listed
- [ ] Grain is documented
- [ ] Keys are tested
- [ ] Join risks are documented

## Python

- [ ] Six notebooks exist
- [ ] All notebooks run fully
- [ ] Raw data is unchanged
- [ ] Staging outputs are reproducible
- [ ] Join tests pass
- [ ] Findings use real results

## SQL

- [ ] Database exists
- [ ] At least 30 queries exist
- [ ] CTEs are used
- [ ] Window functions are used
- [ ] Totals match Python
- [ ] Validation queries exist

## Power Query

- [ ] Staging queries have load disabled
- [ ] Final queries have correct types
- [ ] Folder path is configurable
- [ ] No refresh errors exist

## Power BI model

- [ ] Star schema is complete
- [ ] Order and item facts are separate
- [ ] Relationships are one-to-many
- [ ] Date table is marked
- [ ] Alternate dates are handled
- [ ] Technical keys are hidden
- [ ] Measures table exists

## DAX

- [ ] GMV is correct
- [ ] Order counts are correct
- [ ] Delivery-rate denominators are correct
- [ ] Review-rate denominators are correct
- [ ] Repeat customers use unique customer ID
- [ ] Time intelligence works
- [ ] Scenario measures work
- [ ] Python, SQL, and DAX values match

## Dashboard

- [ ] Five main pages are complete
- [ ] Seller drill-through works
- [ ] Order drill-through works
- [ ] Tooltips work
- [ ] Field parameters work
- [ ] Reset buttons work
- [ ] Decomposition Tree is useful
- [ ] Key Influencers is interpreted carefully
- [ ] What-If scenario is documented
- [ ] QA page exists
- [ ] Screenshots are exported

## Documentation

- [ ] README is complete
- [ ] Data dictionary exists
- [ ] Grain document exists
- [ ] Source-to-target mapping exists
- [ ] Metric definitions exist
- [ ] Dashboard guide exists
- [ ] Business report exists
- [ ] Limitations are stated

## Resume and interview

- [ ] Resume bullets are truthful
- [ ] No fake metrics are included
- [ ] Every relationship can be explained
- [ ] Every listed DAX feature can be explained
- [ ] A two-minute demo is prepared

---

# 38. Definition of Done

The project is complete only when:

1. Another person can understand the source tables and their grain.
2. Raw data can be transformed reproducibly.
3. No join causes double counting.
4. Python, SQL, and Power BI metrics match.
5. The report includes commercial, delivery, customer, seller, and category views.
6. Root-cause and scenario features work.
7. Recommendations use verified evidence.
8. GitHub is professional.
9. Resume bullets are truthful.
10. You can demonstrate the complete workflow without reading the documentation.

---

# 39. Best Resume Project Order

For a one-page data-analyst internship resume, use:

1. **Enterprise E-Commerce Operations and Customer Experience Control Tower** — Python, SQL, Power BI, Power Query, DAX
2. **Telecom Customer Churn and Retention Analytics** — Python, SQL, Tableau

Keep the Retail Sales and Customer Analytics Dashboard in GitHub as an additional portfolio project.

---

# 40. Reference Notes

- Dataset: Brazilian E-Commerce Public Dataset by Olist on Kaggle
- Power BI feature guidance: Microsoft Learn documentation for Decomposition Tree, Key Influencers, mobile reports, and report modeling
