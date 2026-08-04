# Relationship and Grain Document

## Purpose
This document defines the grain of every source table and documents all join risks before any integration occurs.

---

## Table Grain Summary

| Table | Grain | Candidate Key | Relationship Key | Key Unique? |
|---|---|---|---|---|
| orders | One row per order | `order_id` | `order_id` | ✅ Yes |
| order_items | One row per order item | `order_id` + `order_item_id` | `order_id` | ✅ Yes (composite) |
| customers | One row per order-customer ID | `customer_id` | `customer_id` | ✅ Yes |
| products | One row per product | `product_id` | `product_id` | ✅ Yes |
| sellers | One row per seller | `seller_id` | `seller_id` | ✅ Yes |
| payments | One row per payment sequence | `order_id` + `payment_sequential` | `order_id` | ✅ Yes (composite) |
| reviews | One review record | `review_id` | `order_id` | ⚠️ review_id has 814 dupes |
| geolocation | Multiple rows per ZIP prefix | None in raw form | ZIP prefix | ❌ Not unique |
| category_translation | One row per category | `product_category_name` | `product_category_name` | ✅ Yes |

---

## Relationships

```
orders (1) ──────────────────────── (*) order_items
orders (1) ──────────────────────── (1) customers
orders (1) ──────────────────────── (*) payments
orders (1) ──────────────────────── (*) reviews
order_items (*) ─────────────────── (1) products
order_items (*) ─────────────────── (1) sellers
customers (*) ───────────────────── (1) geolocation [via ZIP prefix, after aggregation]
sellers (*) ─────────────────────── (1) geolocation [via ZIP prefix, after aggregation]
products (*) ────────────────────── (1) category_translation
```

---

## Critical Join Risks

### Risk 1: Payments to Orders (Many-to-One)
- **Problem:** 103,886 payment rows for 99,441 orders. 2,961 orders have more than one payment row.
- **Impact:** Joining payments directly to orders without aggregation will create extra rows in the result and inflate GMV and freight counts.
- **Resolution:** Aggregate payments to order level first (total payment value, max installments, primary payment type, payment count).

### Risk 2: Reviews to Orders (Many-to-One)
- **Problem:** 99,224 review rows for 99,441 orders. 547 orders have more than one review.
- **Impact:** Joining reviews directly will multiply rows and corrupt all metrics for those orders.
- **Resolution:** Aggregate reviews to order level first (average score, latest score, review count, comment flag).

### Risk 3: Order Items to Orders (Many-to-One)
- **Problem:** 112,650 item rows for 99,441 orders.
- **Impact:** If payment and review aggregations are not done BEFORE joining items, the row count will multiply by ~1.13x and inflate all totals.
- **Resolution:** Keep the order-level fact table and item-level fact table separate. Aggregate item data (GMV, freight, item count) to order level for the order fact.

### Risk 4: Geolocation (Many per ZIP prefix)
- **Problem:** 1,000,163 raw rows for only 19,015 unique ZIP prefixes. 261,831 are exact duplicates.
- **Impact:** Joining raw geolocation directly multiplies rows severely.
- **Resolution:** Aggregate to one representative row per ZIP prefix using median lat/lng before joining.

### Risk 5: Items × Payments × Reviews (Triple Join)
- **Forbidden join pattern:**
  ```
  Order Items × Payments × Reviews (all raw)
  ```
- **Impact:** This creates a cartesian-like explosion of rows that produces completely incorrect GMV, freight, payment, and review metrics.
- **Resolution:** Never join raw versions of these three tables together. Always aggregate payments and reviews to order level first.

---

## Grain Decision for Target Tables

### fact_orders (Order-Level Fact)
- **Grain:** One row per order
- **Source:** orders (base), + aggregated payments, + aggregated reviews, + aggregated item summary
- **Key:** `order_id`

### fact_order_items (Item-Level Fact)
- **Grain:** One row per order item
- **Source:** order_items (base), + order timestamps and status from orders, + product from products, + seller from sellers
- **Key:** `order_id` + `order_item_id`

### fact_payments (Payment-Level Fact)
- **Grain:** One row per payment sequence
- **Source:** payments raw (kept as-is)
- **Key:** `order_id` + `payment_sequential`

### fact_reviews (Review-Level Fact)
- **Grain:** One review record
- **Source:** reviews raw (kept as-is with review_id deduplication)
- **Key:** `review_id` (after deduplication)

### dim_customers
- **Grain:** One row per customer_id (order-specific)
- **Key:** `customer_id`
- **Note:** Use `customer_unique_id` for repeat customer analysis

### dim_products
- **Grain:** One row per product
- **Key:** `product_id`

### dim_sellers
- **Grain:** One row per seller
- **Key:** `seller_id`

### dim_customer_geography
- **Grain:** One row per ZIP prefix (aggregated from geolocation)
- **Key:** `customer_zip_code_prefix`

### dim_seller_geography
- **Grain:** One row per ZIP prefix (aggregated from geolocation)
- **Key:** `seller_zip_code_prefix`

---

## Key Data Quality Flags Identified

| Table | Issue | Count | Severity | Planned Treatment |
|---|---|---|---|---|
| orders | Missing `order_approved_at` | 160 | Medium | Flag as `missing_approval_flag` |
| orders | Missing `order_delivered_carrier_date` | 1,783 | Medium | Flag as `missing_carrier_flag` |
| orders | Missing `order_delivered_customer_date` | 2,965 | High | Flag as `missing_delivery_flag`; exclude from delivery calcs |
| products | Missing `product_category_name` | 610 | Medium | Label as `unknown_category` |
| products | Missing physical dimensions | 2 | Low | Flag and exclude from volume calc |
| reviews | `review_id` not unique | 814 | Medium | Deduplicate; keep one per review_id |
| reviews | Multiple reviews per order | 547 | Medium | Aggregate to order level |
| payments | Multiple payment rows per order | 2,961 | High | Aggregate to order level before joining |
| geolocation | Full row duplicates | 261,831 | High | Remove duplicates; median per ZIP prefix |
| geolocation | Multiple coords per ZIP prefix | 1,000,163 → 19,015 | High | Aggregate using median lat/lng |
