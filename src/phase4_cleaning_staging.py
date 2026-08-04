"""
Phase 4 - Data Cleaning and Staging Script
Applies all cleaning rules, creates data quality flags,
computes order-level aggregations for payments and reviews,
and saves clean staged outputs to data/staging/.
"""
import os
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

RAW_PATH = 'data/raw/'
STAGING_PATH = 'data/staging/'
os.makedirs(STAGING_PATH, exist_ok=True)

print("=" * 70)
print("PHASE 4 — DATA CLEANING & STAGING PIPELINE")
print("=" * 70)

# ── 1. ORDERS ────────────────────────────────────────────────────────────────
print("\n[1/8] Cleaning Orders...")
orders = pd.read_csv(os.path.join(RAW_PATH, 'olist_orders_dataset.csv'))

# Standardize strings
orders['order_status'] = orders['order_status'].str.strip().str.lower()

# Parse timestamps
date_cols = [
    'order_purchase_timestamp', 'order_approved_at',
    'order_delivered_carrier_date', 'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for c in date_cols:
    orders[c] = pd.to_datetime(orders[c], errors='coerce')

# Add quality flags
orders['missing_approval_flag'] = orders['order_approved_at'].isnull().astype(int)
orders['missing_carrier_flag'] = orders['order_delivered_carrier_date'].isnull().astype(int)
orders['missing_delivery_flag'] = orders['order_delivered_customer_date'].isnull().astype(int)

# Sequence errors: delivery before purchase, carrier before purchase, delivery before carrier
seq_err = (
    (orders['order_delivered_customer_date'] < orders['order_purchase_timestamp']) |
    (orders['order_delivered_carrier_date'] < orders['order_purchase_timestamp']) |
    (orders['order_delivered_customer_date'] < orders['order_delivered_carrier_date'])
).fillna(False)
orders['invalid_timestamp_sequence_flag'] = seq_err.astype(int)

# Delivered status mismatch: status says delivered but no customer delivery timestamp
status_mismatch = (orders['order_status'] == 'delivered') & (orders['order_delivered_customer_date'].isnull())
orders['delivered_status_mismatch_flag'] = status_mismatch.astype(int)

orders.to_csv(os.path.join(STAGING_PATH, 'stg_orders.csv'), index=False)
print(f"  -> Saved stg_orders.csv: {orders.shape[0]:,} rows x {orders.shape[1]} cols")
print(f"     Quality flags: missing_delivery={orders['missing_delivery_flag'].sum():,}, "
      f"seq_errors={orders['invalid_timestamp_sequence_flag'].sum():,}, "
      f"status_mismatches={orders['delivered_status_mismatch_flag'].sum():,}")

# ── 2. ORDER ITEMS ───────────────────────────────────────────────────────────
print("\n[2/8] Cleaning Order Items...")
items = pd.read_csv(os.path.join(RAW_PATH, 'olist_order_items_dataset.csv'))

# Parse shipping limit date
items['shipping_limit_date'] = pd.to_datetime(items['shipping_limit_date'], errors='coerce')

# Ensure numeric values are valid
items['price'] = pd.to_numeric(items['price'], errors='coerce').fillna(0)
items['freight_value'] = pd.to_numeric(items['freight_value'], errors='coerce').fillna(0).clip(lower=0)

# Feature engineering
items['item_total_value'] = items['price'] + items['freight_value']
items['freight_to_price_ratio'] = np.where(items['price'] > 0, items['freight_value'] / items['price'], 0.0)

items.to_csv(os.path.join(STAGING_PATH, 'stg_order_items.csv'), index=False)
print(f"  -> Saved stg_order_items.csv: {items.shape[0]:,} rows x {items.shape[1]} cols")
print(f"     Total GMV: R$ {items['price'].sum():,.2f} | Total Freight: R$ {items['freight_value'].sum():,.2f}")

# ── 3. CUSTOMERS ─────────────────────────────────────────────────────────────
print("\n[3/8] Cleaning Customers...")
customers = pd.read_csv(os.path.join(RAW_PATH, 'olist_customers_dataset.csv'))

# String cleanup
customers['customer_city'] = customers['customer_city'].str.strip().str.title()
customers['customer_state'] = customers['customer_state'].str.strip().str.upper()

customers.to_csv(os.path.join(STAGING_PATH, 'stg_customers.csv'), index=False)
print(f"  -> Saved stg_customers.csv: {customers.shape[0]:,} rows x {customers.shape[1]} cols")
print(f"     Distinct customer_id: {customers['customer_id'].nunique():,}, "
      f"Unique buyers: {customers['customer_unique_id'].nunique():,}")

# ── 4. PRODUCTS & CATEGORIES ─────────────────────────────────────────────────
print("\n[4/8] Cleaning Products & Categories...")
products = pd.read_csv(os.path.join(RAW_PATH, 'olist_products_dataset.csv'))
cat_trans = pd.read_csv(os.path.join(RAW_PATH, 'product_category_name_translation.csv'))

# Merge English translation
products = products.merge(cat_trans, on='product_category_name', how='left')

# Fill missing category names
products['product_category_name'] = products['product_category_name'].fillna('outros')
products['product_category_name_english'] = products['product_category_name_english'].fillna('other')

# Fix specific untranslated categories if any
products.loc[products['product_category_name'] == 'pc_gamer', 'product_category_name_english'] = 'pc_gamer'
products.loc[products['product_category_name'] == 'portateis_cozinha_e_preparadores_de_alimentos', 'product_category_name_english'] = 'kitchen_small_appliances'

# Clean dimensions & calculate volume
num_dim_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
for c in num_dim_cols:
    products[c] = pd.to_numeric(products[c], errors='coerce')

# Volume calculation (cm3)
products['product_volume_cm3'] = (
    products['product_length_cm'] * products['product_height_cm'] * products['product_width_cm']
)

# Size bands
def categorize_volume(v):
    if pd.isna(v):
        return 'Unknown'
    elif v < 5000:
        return 'Small (<5L)'
    elif v < 20000:
        return 'Medium (5-20L)'
    elif v < 60000:
        return 'Large (20-60L)'
    else:
        return 'Extra Large (>=60L)'

def categorize_weight(w):
    if pd.isna(w):
        return 'Unknown'
    elif w < 1000:
        return 'Light (<1kg)'
    elif w < 5000:
        return 'Medium (1-5kg)'
    else:
        return 'Heavy (>=5kg)'

products['product_size_band'] = products['product_volume_cm3'].apply(categorize_volume)
products['product_weight_band'] = products['product_weight_g'].apply(categorize_weight)

products.to_csv(os.path.join(STAGING_PATH, 'stg_products.csv'), index=False)
print(f"  -> Saved stg_products.csv: {products.shape[0]:,} rows x {products.shape[1]} cols")
print(f"     Categories mapped: {products['product_category_name_english'].nunique()} unique English categories")

# ── 5. SELLERS ───────────────────────────────────────────────────────────────
print("\n[5/8] Cleaning Sellers...")
sellers = pd.read_csv(os.path.join(RAW_PATH, 'olist_sellers_dataset.csv'))

# String cleanup
sellers['seller_city'] = sellers['seller_city'].str.strip().str.title()
sellers['seller_state'] = sellers['seller_state'].str.strip().str.upper()

sellers.to_csv(os.path.join(STAGING_PATH, 'stg_sellers.csv'), index=False)
print(f"  -> Saved stg_sellers.csv: {sellers.shape[0]:,} rows x {sellers.shape[1]} cols")

# ── 6. PAYMENTS & ORDER-LEVEL AGGREGATION ────────────────────────────────────
print("\n[6/8] Cleaning & Aggregating Payments...")
payments = pd.read_csv(os.path.join(RAW_PATH, 'olist_order_payments_dataset.csv'))

# Clean types and invalid values
payments['payment_type'] = payments['payment_type'].str.strip().str.lower()
payments.loc[payments['payment_type'] == 'not_defined', 'payment_type'] = 'unknown'
payments['payment_value'] = pd.to_numeric(payments['payment_value'], errors='coerce').fillna(0).clip(lower=0)
payments['payment_installments'] = pd.to_numeric(payments['payment_installments'], errors='coerce').fillna(1).astype(int)

# Save line-item level payments
payments.to_csv(os.path.join(STAGING_PATH, 'stg_order_payments.csv'), index=False)
print(f"  -> Saved stg_order_payments.csv: {payments.shape[0]:,} rows x {payments.shape[1]} cols")

# Aggregate payments to order level (prevents cartesian explosion when joining with orders)
# Primary payment type is the one with highest payment value for that order
pay_sorted = payments.sort_values(['order_id', 'payment_value'], ascending=[True, False])
primary_pay = pay_sorted.groupby('order_id').first()[['payment_type']].rename(columns={'payment_type': 'primary_payment_type'})

pay_agg = payments.groupby('order_id').agg(
    payment_value_total=('payment_value', 'sum'),
    payment_installments_max=('payment_installments', 'max'),
    payment_record_count=('payment_sequential', 'count')
).reset_index()

pay_agg = pay_agg.merge(primary_pay, on='order_id', how='left')
pay_agg['multi_payment_flag'] = (pay_agg['payment_record_count'] > 1).astype(int)

pay_agg.to_csv(os.path.join(STAGING_PATH, 'stg_payments_order_agg.csv'), index=False)
print(f"  -> Saved stg_payments_order_agg.csv: {pay_agg.shape[0]:,} orders (Aggregated)")
print(f"     Multi-payment orders: {pay_agg['multi_payment_flag'].sum():,} ({pay_agg['multi_payment_flag'].mean()*100:.2f}%)")

# ── 7. REVIEWS & ORDER-LEVEL AGGREGATION ─────────────────────────────────────
print("\n[7/8] Cleaning & Aggregating Reviews...")
reviews = pd.read_csv(os.path.join(RAW_PATH, 'olist_order_reviews_dataset.csv'))

# Parse dates
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'], errors='coerce')
reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'], errors='coerce')

# Calculate review response time in hours
reviews['review_response_hours'] = (
    (reviews['review_answer_timestamp'] - reviews['review_creation_date']).dt.total_seconds() / 3600.0
).clip(lower=0)

# Deduplicate review_id: if same review_id exists multiple times, take the latest answer
reviews_clean = reviews.sort_values('review_answer_timestamp', ascending=False).drop_duplicates(subset=['review_id'])
reviews_clean.to_csv(os.path.join(STAGING_PATH, 'stg_order_reviews.csv'), index=False)
print(f"  -> Saved stg_order_reviews.csv: {reviews_clean.shape[0]:,} rows (deduplicated by review_id)")

# Has comment flag
reviews['has_comment_flag'] = (reviews['review_comment_message'].notna() | reviews['review_comment_title'].notna()).astype(int)

# Aggregate reviews to order level
rev_agg = reviews.groupby('order_id').agg(
    review_score_avg=('review_score', 'mean'),
    review_score_latest=('review_score', 'last'),
    review_count=('review_id', 'count'),
    review_comment_flag=('has_comment_flag', 'max'),
    review_response_hours=('review_response_hours', 'mean')
).reset_index()

rev_agg['review_score_avg'] = rev_agg['review_score_avg'].round(2)
rev_agg['review_response_hours'] = rev_agg['review_response_hours'].round(1)

rev_agg.to_csv(os.path.join(STAGING_PATH, 'stg_reviews_order_agg.csv'), index=False)
print(f"  -> Saved stg_reviews_order_agg.csv: {rev_agg.shape[0]:,} orders (Aggregated)")
print(f"     Average review score across all orders: {rev_agg['review_score_avg'].mean():.2f} / 5.00")

# ── 8. GEOLOCATION ───────────────────────────────────────────────────────────
print("\n[8/8] Cleaning & Aggregating Geolocation...")
geo = pd.read_csv(os.path.join(RAW_PATH, 'olist_geolocation_dataset.csv'))

# Drop exact duplicate rows
geo_dedup = geo.drop_duplicates()
print(f"  Raw geolocation rows: {geo.shape[0]:,} -> After dropping exact dupes: {geo_dedup.shape[0]:,}")

# Filter out obvious coordinate outliers (Brazil bounding box approx: Lat [-34.5, 5.5], Lng [-74.5, -34.0])
valid_coords = (
    (geo_dedup['geolocation_lat'] >= -35.0) & (geo_dedup['geolocation_lat'] <= 6.0) &
    (geo_dedup['geolocation_lng'] >= -75.0) & (geo_dedup['geolocation_lng'] <= -33.0)
)
geo_clean = geo_dedup[valid_coords].copy()
geo_clean['geolocation_city'] = geo_clean['geolocation_city'].str.strip().str.title()
geo_clean['geolocation_state'] = geo_clean['geolocation_state'].str.strip().str.upper()

# Aggregate to exactly 1 row per ZIP code prefix using median coordinate
geo_zip = (
    geo_clean.groupby('geolocation_zip_code_prefix', as_index=False)
    .agg(
        latitude=('geolocation_lat', 'median'),
        longitude=('geolocation_lng', 'median'),
        city=('geolocation_city', 'first'),
        state=('geolocation_state', 'first')
    )
)

geo_zip.to_csv(os.path.join(STAGING_PATH, 'stg_geolocation_zip.csv'), index=False)
print(f"  -> Saved stg_geolocation_zip.csv: {geo_zip.shape[0]:,} unique ZIP prefixes (Aggregated)")
print(f"     100% Unique ZIP prefix primary key verified: {geo_zip['geolocation_zip_code_prefix'].is_unique}")

print("\n" + "=" * 70)
print("PHASE 4 DATA CLEANING & STAGING COMPLETED SUCCESSFULLY!")
print("=" * 70)
