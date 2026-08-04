# Source Inventory Document

## Dataset: Brazilian E-Commerce Public Dataset by Olist

---

## 1. olist_orders_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 99,441 |
| **Columns** | 8 |
| **Candidate Primary Key** | `order_id` |
| **Foreign Keys** | `customer_id` → customers |
| **Grain** | One row per order |
| **Duplicate Key Count** | 0 (order_id is fully unique) |
| **Date Range** | 2016-09-04 to 2018-10-17 |
| **Planned Target Table** | `fact_orders` |

**Columns:** `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`

**Null Counts:**
| Column | Null Count | Note |
|---|---|---|
| `order_approved_at` | 160 | Orders not yet approved |
| `order_delivered_carrier_date` | 1,783 | Orders not yet with carrier |
| `order_delivered_customer_date` | 2,965 | Orders not yet delivered |

**Order Status Distribution:**
| Status | Count |
|---|---|
| delivered | 96,478 |
| shipped | 1,107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

**Join Risks:** Missing timestamps for non-delivered orders must be excluded from delivery-time calculations.

---

## 2. olist_order_items_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 112,650 |
| **Columns** | 7 |
| **Candidate Primary Key** | `order_id` + `order_item_id` (composite) |
| **Foreign Keys** | `order_id` → orders, `product_id` → products, `seller_id` → sellers |
| **Grain** | One row per order item |
| **Duplicate Key Count** | 0 (composite key is fully unique) |
| **Null Count** | 0 (no nulls in any column) |
| **Planned Target Table** | `fact_order_items` |

**Columns:** `order_id`, `order_item_id`, `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value`

**Join Risks:** 112,650 item rows for 99,441 orders — average ~1.13 items per order. Direct join to payments or reviews will multiply rows and inflate GMV. Must aggregate item data to order level before joining.

---

## 3. olist_customers_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 99,441 |
| **Columns** | 5 |
| **Candidate Primary Key** | `customer_id` |
| **Foreign Keys** | None (referenced by orders) |
| **Grain** | One row per order-customer ID |
| **Duplicate Key Count** | 0 (customer_id is fully unique) |
| **Null Count** | 0 (no nulls in any column) |
| **Planned Target Table** | `dim_customers` |

**Columns:** `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state`

**Key Insight:** `customer_unique_id` has only 96,096 unique values vs 99,441 rows — meaning 3,345 customers placed more than one order. Repeat-customer analysis must use `customer_unique_id`.

**Join Risks:** `customer_id` is order-specific; using `customer_unique_id` for repeat-customer counts is essential.

---

## 4. olist_products_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 32,951 |
| **Columns** | 9 |
| **Candidate Primary Key** | `product_id` |
| **Foreign Keys** | `product_category_name` → category_translation |
| **Grain** | One row per product |
| **Duplicate Key Count** | 0 (product_id is fully unique) |
| **Planned Target Table** | `dim_products` |

**Columns:** `product_id`, `product_category_name`, `product_name_lenght`, `product_description_lenght`, `product_photos_qty`, `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`

**Null Counts:**
| Column | Null Count | Note |
|---|---|---|
| `product_category_name` | 610 | Missing category — to be flagged |
| `product_name_lenght` | 610 | Same 610 rows |
| `product_description_lenght` | 610 | Same 610 rows |
| `product_photos_qty` | 610 | Same 610 rows |
| `product_weight_g` | 2 | Minor, to be treated |
| `product_length_cm` | 2 | Same 2 rows |
| `product_height_cm` | 2 | Same 2 rows |
| `product_width_cm` | 2 | Same 2 rows |

**Note:** Column names contain a typo (`lenght` instead of `length`) — will be renamed during staging.

**Join Risks:** 610 products have no category. Will be labelled `unknown_category` during cleaning.

---

## 5. olist_sellers_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 3,095 |
| **Columns** | 4 |
| **Candidate Primary Key** | `seller_id` |
| **Foreign Keys** | None (referenced by order_items) |
| **Grain** | One row per seller |
| **Duplicate Key Count** | 0 (seller_id is fully unique) |
| **Null Count** | 0 (no nulls in any column) |
| **Planned Target Table** | `dim_sellers` |

**Columns:** `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state`

**Top 5 States by Seller Count:** SP (1,849), PR (349), MG (244), SC (190), RJ (171)

---

## 6. olist_order_payments_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 103,886 |
| **Columns** | 5 |
| **Candidate Primary Key** | `order_id` + `payment_sequential` (composite) |
| **Foreign Keys** | `order_id` → orders |
| **Grain** | One row per payment sequence per order |
| **Duplicate Key Count** | 0 (composite key is fully unique) |
| **Null Count** | 0 (no nulls in any column) |
| **Planned Target Table** | `fact_payments` (also aggregated to `fact_orders`) |

**Columns:** `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value`

**Key Insight:** 2,961 orders have more than one payment row (e.g. voucher + credit card). Must aggregate to order level before joining to avoid row multiplication.

**Payment Type Distribution:**
| Type | Count |
|---|---|
| credit_card | 76,795 |
| boleto | 19,784 |
| voucher | 5,775 |
| debit_card | 1,529 |
| not_defined | 3 |

**Join Risks:** Direct join to orders on `order_id` without prior aggregation will inflate payment totals.

---

## 7. olist_order_reviews_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 99,224 |
| **Columns** | 7 |
| **Candidate Primary Key** | `review_id` (NOT fully unique — 814 duplicates) |
| **Foreign Keys** | `order_id` → orders |
| **Grain** | One review record per order (mostly) |
| **Duplicate Key Count** | review_id has 814 non-unique values |
| **Planned Target Table** | `fact_reviews` (also aggregated to `fact_orders`) |

**Columns:** `review_id`, `order_id`, `review_score`, `review_comment_title`, `review_comment_message`, `review_creation_date`, `review_answer_timestamp`

**Null Counts:**
| Column | Null Count | Note |
|---|---|---|
| `review_comment_title` | 87,656 | Most reviews have no title |
| `review_comment_message` | 58,247 | Many reviews have no message |

**Key Insight:** 547 orders have multiple review records. Review score must be aggregated (e.g. average or latest) to order level before joining.

**Review Score Distribution:**
| Score | Count | Group |
|---|---|---|
| 1 | 11,424 | Negative |
| 2 | 3,151 | Negative |
| 3 | 8,179 | Neutral |
| 4 | 19,142 | Positive |
| 5 | 57,328 | Positive |

**Join Risks:** Must aggregate to order level. Direct join will multiply rows.

---

## 8. olist_geolocation_dataset.csv

| Property | Value |
|---|---|
| **Rows** | 1,000,163 |
| **Columns** | 5 |
| **Candidate Primary Key** | None (ZIP prefix is not unique) |
| **Foreign Keys** | `geolocation_zip_code_prefix` → customers, sellers |
| **Grain** | Multiple rows per ZIP prefix |
| **Unique ZIP Prefixes** | 19,015 |
| **Full Row Duplicates** | 261,831 |
| **Null Count** | 0 |
| **Planned Target Table** | `dim_customer_geography`, `dim_seller_geography` |

**Columns:** `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state`

**Join Risks:** Must aggregate to one representative coordinate per ZIP prefix (using median lat/lng) before joining. Direct join multiplies rows massively.

---

## 9. product_category_name_translation.csv

| Property | Value |
|---|---|
| **Rows** | 71 |
| **Columns** | 2 |
| **Candidate Primary Key** | `product_category_name` |
| **Foreign Keys** | None (lookup table joined to products) |
| **Grain** | One row per category |
| **Duplicate Key Count** | 0 |
| **Null Count** | 0 |
| **Planned Target Table** | Joined into `dim_products` |

**Columns:** `product_category_name`, `product_category_name_english`

**Note:** Only 71 category translations available. The 610 products with null category will receive `unknown_category`.
