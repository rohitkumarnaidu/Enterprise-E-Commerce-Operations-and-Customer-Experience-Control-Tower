"""
Phase 5 - Data Integration and Feature Engineering Script
Integrates staged tables into Dimensional Model (Facts & Dimensions):
- fact_orders
- fact_order_items
- fact_payments
- fact_reviews
- dim_customers (customer summary)
- dim_sellers (seller scorecard)
- dim_products
- dim_geography
- dim_date
"""
import os
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

STAGING_PATH = 'data/staging/'
PROCESSED_PATH = 'data/processed/'
os.makedirs(PROCESSED_PATH, exist_ok=True)

print("=" * 70)
print("PHASE 5 — DATA INTEGRATION & FEATURE ENGINEERING")
print("=" * 70)

# ── Load Staged Datasets ─────────────────────────────────────────────────────
print("\n[1/7] Loading Staged Data...")
stg_orders = pd.read_csv(os.path.join(STAGING_PATH, 'stg_orders.csv'))
stg_items = pd.read_csv(os.path.join(STAGING_PATH, 'stg_order_items.csv'))
stg_customers = pd.read_csv(os.path.join(STAGING_PATH, 'stg_customers.csv'))
stg_products = pd.read_csv(os.path.join(STAGING_PATH, 'stg_products.csv'))
stg_sellers = pd.read_csv(os.path.join(STAGING_PATH, 'stg_sellers.csv'))
stg_payments_agg = pd.read_csv(os.path.join(STAGING_PATH, 'stg_payments_order_agg.csv'))
stg_payments_raw = pd.read_csv(os.path.join(STAGING_PATH, 'stg_order_payments.csv'))
stg_reviews_agg = pd.read_csv(os.path.join(STAGING_PATH, 'stg_reviews_order_agg.csv'))
stg_reviews_raw = pd.read_csv(os.path.join(STAGING_PATH, 'stg_order_reviews.csv'))
stg_geo = pd.read_csv(os.path.join(STAGING_PATH, 'stg_geolocation_zip.csv'))

# Parse dates in orders
date_cols = [
    'order_purchase_timestamp', 'order_approved_at',
    'order_delivered_carrier_date', 'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for c in date_cols:
    stg_orders[c] = pd.to_datetime(stg_orders[c], errors='coerce')

# ── 1. AGGREGATE ORDER ITEMS TO ORDER GRAIN ──────────────────────────────────
print("\n[2/7] Aggregating Order Items to Order Grain...")
items_agg = stg_items.groupby('order_id').agg(
    item_count=('order_item_id', 'count'),
    unique_product_count=('product_id', 'nunique'),
    unique_seller_count=('seller_id', 'nunique'),
    gmv=('price', 'sum'),
    freight_value=('freight_value', 'sum'),
    total_order_value=('item_total_value', 'sum'),
    average_item_price=('price', 'mean'),
    maximum_item_price=('price', 'max'),
    average_freight_to_price_ratio=('freight_to_price_ratio', 'mean')
).reset_index()

items_agg['average_item_price'] = items_agg['average_item_price'].round(2)
items_agg['average_freight_to_price_ratio'] = items_agg['average_freight_to_price_ratio'].round(4)

# ── 2. BUILD FACT_ORDERS ─────────────────────────────────────────────────────
print("\n[3/7] Building fact_orders...")
fact_orders = stg_orders.merge(stg_customers, on='customer_id', how='left')
fact_orders = fact_orders.merge(items_agg, on='order_id', how='left')
fact_orders = fact_orders.merge(stg_payments_agg, on='order_id', how='left')
fact_orders = fact_orders.merge(stg_reviews_agg, on='order_id', how='left')

# Fill missing numerical aggregates for orders with no items (e.g. cancelled before items created)
for col in ['item_count', 'unique_product_count', 'unique_seller_count', 'gmv', 'freight_value', 'total_order_value']:
    fact_orders[col] = fact_orders[col].fillna(0)

# Delivery Time Calculations
fact_orders['approval_hours'] = (
    (fact_orders['order_approved_at'] - fact_orders['order_purchase_timestamp']).dt.total_seconds() / 3600.0
).round(2)

fact_orders['handling_days'] = (
    (fact_orders['order_delivered_carrier_date'] - fact_orders['order_approved_at']).dt.total_seconds() / 86400.0
).round(2)

fact_orders['transit_days'] = (
    (fact_orders['order_delivered_customer_date'] - fact_orders['order_delivered_carrier_date']).dt.total_seconds() / 86400.0
).round(2)

fact_orders['delivery_days'] = (
    (fact_orders['order_delivered_customer_date'] - fact_orders['order_purchase_timestamp']).dt.total_seconds() / 86400.0
).round(2)

fact_orders['promised_delivery_days'] = (
    (fact_orders['order_estimated_delivery_date'] - fact_orders['order_purchase_timestamp']).dt.total_seconds() / 86400.0
).round(2)

fact_orders['delay_days'] = (
    (fact_orders['order_delivered_customer_date'] - fact_orders['order_estimated_delivery_date']).dt.total_seconds() / 86400.0
).round(2)

# Delivery Status & Flags
def get_delivery_status(row):
    if row['order_status'] != 'delivered' or pd.isna(row['order_delivered_customer_date']):
        if row['order_status'] == 'canceled':
            return 'Canceled'
        elif row['order_status'] == 'unavailable':
            return 'Unavailable'
        else:
            return 'In Transit / Processing'
    elif row['delay_days'] <= 0:
        return 'Early / On Time'
    else:
        return 'Late'

fact_orders['delivery_status'] = fact_orders.apply(get_delivery_status, axis=1)

is_delivered = (fact_orders['order_status'] == 'delivered') & fact_orders['order_delivered_customer_date'].notna()
fact_orders['late_delivery_flag'] = np.where(is_delivered & (fact_orders['delay_days'] > 0), 1, 0)
fact_orders['severe_delay_flag'] = np.where(is_delivered & (fact_orders['delay_days'] > 7), 1, 0)

def get_delay_band(row):
    if row['order_status'] != 'delivered' or pd.isna(row['order_delivered_customer_date']):
        return 'Not Delivered'
    elif row['delay_days'] <= 0:
        return 'Early or On Time'
    elif row['delay_days'] <= 3:
        return '1–3 Days Late'
    elif row['delay_days'] <= 7:
        return '4–7 Days Late'
    else:
        return '8+ Days Late'

fact_orders['delay_band'] = fact_orders.apply(get_delay_band, axis=1)

# Review Feature Engineering
def get_review_group(score):
    if pd.isna(score):
        return 'No Review'
    elif score >= 4:
        return 'Positive (4-5)'
    elif score == 3:
        return 'Neutral (3)'
    else:
        return 'Negative (1-2)'

fact_orders['review_group'] = fact_orders['review_score_avg'].apply(get_review_group)
fact_orders['low_review_flag'] = np.where(fact_orders['review_score_avg'] <= 2, 1, 0)
fact_orders['high_review_flag'] = np.where(fact_orders['review_score_avg'] >= 4, 1, 0)

fact_orders.to_csv(os.path.join(PROCESSED_PATH, 'fact_orders.csv'), index=False)
print(f"  -> Saved fact_orders.csv: {fact_orders.shape[0]:,} rows x {fact_orders.shape[1]} cols")
print(f"     GMV: R$ {fact_orders['gmv'].sum():,.2f} | On-Time Rate: {(fact_orders[is_delivered]['late_delivery_flag'] == 0).mean()*100:.2f}%")

# ── 3. BUILD FACT_ORDER_ITEMS WITH DISTANCE CALCULATION ───────────────────────
print("\n[4/7] Building fact_order_items with Haversine Distance...")

# Haversine distance function in km
def haversine_vectorized(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2.0) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

fact_items = stg_items.merge(
    fact_orders[['order_id', 'order_status', 'order_purchase_timestamp', 'order_delivered_customer_date',
                 'order_estimated_delivery_date', 'delivery_days', 'delay_days', 'delivery_status',
                 'late_delivery_flag', 'customer_id', 'customer_unique_id', 'customer_zip_code_prefix',
                 'customer_city', 'customer_state']],
    on='order_id', how='left'
)

fact_items = fact_items.merge(
    stg_products[['product_id', 'product_category_name', 'product_category_name_english',
                  'product_volume_cm3', 'product_size_band', 'product_weight_g', 'product_weight_band']],
    on='product_id', how='left'
)

fact_items = fact_items.merge(
    stg_sellers[['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state']],
    on='seller_id', how='left'
)

# Join Customer coordinates
fact_items = fact_items.merge(
    stg_geo.rename(columns={
        'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
        'latitude': 'cust_lat', 'longitude': 'cust_lng'
    })[['customer_zip_code_prefix', 'cust_lat', 'cust_lng']],
    on='customer_zip_code_prefix', how='left'
)

# Join Seller coordinates
fact_items = fact_items.merge(
    stg_geo.rename(columns={
        'geolocation_zip_code_prefix': 'seller_zip_code_prefix',
        'latitude': 'seller_lat', 'longitude': 'seller_lng'
    })[['seller_zip_code_prefix', 'seller_lat', 'seller_lng']],
    on='seller_zip_code_prefix', how='left'
)

# Calculate distance
fact_items['distance_km'] = haversine_vectorized(
    fact_items['seller_lat'], fact_items['seller_lng'],
    fact_items['cust_lat'], fact_items['cust_lng']
).round(1)

def get_distance_band(d):
    if pd.isna(d):
        return 'Unknown'
    elif d <= 100:
        return '0–100 km'
    elif d <= 500:
        return '101–500 km'
    elif d <= 1000:
        return '501–1,000 km'
    elif d <= 2000:
        return '1,001–2,000 km'
    else:
        return '2,000+ km'

fact_items['distance_band'] = fact_items['distance_km'].apply(get_distance_band)

# Clean up helper coordinate columns
fact_items = fact_items.drop(columns=['cust_lat', 'cust_lng', 'seller_lat', 'seller_lng'])

fact_items.to_csv(os.path.join(PROCESSED_PATH, 'fact_order_items.csv'), index=False)
print(f"  -> Saved fact_order_items.csv: {fact_items.shape[0]:,} rows x {fact_items.shape[1]} cols")
print(f"     Average shipment distance: {fact_items['distance_km'].mean():.1f} km")

# ── 4. SAVE FACT PAYMENTS & FACT REVIEWS ──────────────────────────────────────
stg_payments_raw.to_csv(os.path.join(PROCESSED_PATH, 'fact_payments.csv'), index=False)
stg_reviews_raw.to_csv(os.path.join(PROCESSED_PATH, 'fact_reviews.csv'), index=False)
print(f"  -> Saved fact_payments.csv ({stg_payments_raw.shape[0]:,} rows) and fact_reviews.csv ({stg_reviews_raw.shape[0]:,} rows)")

# ── 5. BUILD CUSTOMER SUMMARY DIMENSION ──────────────────────────────────────
print("\n[5/7] Building dim_customers (Customer Summary)...")
cust_summary = fact_orders.groupby('customer_unique_id').agg(
    first_purchase_date=('order_purchase_timestamp', 'min'),
    last_purchase_date=('order_purchase_timestamp', 'max'),
    total_orders=('order_id', 'count'),
    total_gmv=('gmv', 'sum'),
    total_freight=('freight_value', 'sum'),
    avg_review_score=('review_score_avg', 'mean'),
    avg_delivery_days=('delivery_days', 'mean'),
    late_order_count=('late_delivery_flag', 'sum'),
    primary_state=('customer_state', 'first'),
    primary_city=('customer_city', 'first'),
    primary_zip_prefix=('customer_zip_code_prefix', 'first')
).reset_index()

cust_summary['average_order_value'] = (cust_summary['total_gmv'] / cust_summary['total_orders']).round(2)
cust_summary['repeat_customer_flag'] = (cust_summary['total_orders'] > 1).astype(int)
cust_summary['avg_review_score'] = cust_summary['avg_review_score'].round(2)
cust_summary['avg_delivery_days'] = cust_summary['avg_delivery_days'].round(2)

cust_summary.to_csv(os.path.join(PROCESSED_PATH, 'dim_customers.csv'), index=False)
print(f"  -> Saved dim_customers.csv: {cust_summary.shape[0]:,} unique customers")
print(f"     Repeat Customers: {cust_summary['repeat_customer_flag'].sum():,} ({cust_summary['repeat_customer_flag'].mean()*100:.2f}%)")

# ── 6. BUILD SELLER SCORECARD DIMENSION ───────────────────────────────────────
print("\n[6/7] Building dim_sellers (Seller Scorecard)...")
seller_perf = fact_items.groupby('seller_id').agg(
    total_orders=('order_id', 'nunique'),
    items_sold=('order_item_id', 'count'),
    total_gmv=('price', 'sum'),
    total_freight=('freight_value', 'sum'),
    avg_delay_days=('delay_days', 'mean'),
    states_served_count=('customer_state', 'nunique'),
    categories_sold_count=('product_category_name_english', 'nunique'),
    seller_city=('seller_city', 'first'),
    seller_state=('seller_state', 'first'),
    seller_zip_code_prefix=('seller_zip_code_prefix', 'first')
).reset_index()

# Seller On-Time Rate calculation
delivered_items = fact_items[fact_items['order_status'] == 'delivered'].copy()
seller_deliv = delivered_items.groupby('seller_id').agg(
    delivered_items_count=('order_item_id', 'count'),
    late_items_count=('late_delivery_flag', 'sum')
).reset_index()

seller_perf = seller_perf.merge(seller_deliv, on='seller_id', how='left').fillna(0)
seller_perf['on_time_rate'] = np.where(
    seller_perf['delivered_items_count'] > 0,
    (1.0 - (seller_perf['late_items_count'] / seller_perf['delivered_items_count'])).clip(lower=0) * 100.0,
    100.0
).round(2)

seller_perf['late_delivery_rate'] = (100.0 - seller_perf['on_time_rate']).round(2)
seller_perf['freight_to_price_ratio'] = np.where(
    seller_perf['total_gmv'] > 0,
    (seller_perf['total_freight'] / seller_perf['total_gmv']).round(4),
    0.0
)

# Merge seller average review score from fact_orders
seller_rev = fact_items.groupby('seller_id')['order_id'].unique().reset_index()
# Map review scores
order_rev_map = fact_orders.set_index('order_id')['review_score_avg'].to_dict()
seller_rev['avg_review_score'] = seller_rev['order_id'].apply(
    lambda order_list: np.nanmean([order_rev_map.get(oid, np.nan) for oid in order_list])
).round(2)

seller_perf = seller_perf.merge(seller_rev[['seller_id', 'avg_review_score']], on='seller_id', how='left')

seller_perf.to_csv(os.path.join(PROCESSED_PATH, 'dim_sellers.csv'), index=False)
print(f"  -> Saved dim_sellers.csv: {seller_perf.shape[0]:,} sellers scored")

# ── 7. DIM_PRODUCTS, DIM_GEOGRAPHY, & DIM_DATE ───────────────────────────────
print("\n[7/7] Building Dimension Tables (Products, Geography, Calendar)...")

# Products
stg_products.to_csv(os.path.join(PROCESSED_PATH, 'dim_products.csv'), index=False)

# Geography
stg_geo.rename(columns={'geolocation_zip_code_prefix': 'zip_code_prefix'}).to_csv(
    os.path.join(PROCESSED_PATH, 'dim_geography.csv'), index=False
)

# Date Dimension (2016-01-01 to 2018-12-31)
date_range = pd.date_range(start='2016-01-01', end='2018-12-31', freq='D')
dim_date = pd.DataFrame({'date': date_range})
dim_date['date_key'] = dim_date['date'].dt.strftime('%Y%m%d').astype(int)
dim_date['year'] = dim_date['date'].dt.year
dim_date['quarter'] = dim_date['date'].dt.quarter
dim_date['quarter_name'] = 'Q' + dim_date['quarter'].astype(str)
dim_date['month'] = dim_date['date'].dt.month
dim_date['month_name'] = dim_date['date'].dt.strftime('%B')
dim_date['month_year'] = dim_date['date'].dt.strftime('%b %Y')
dim_date['day'] = dim_date['date'].dt.day
dim_date['day_name'] = dim_date['date'].dt.strftime('%A')
dim_date['day_of_week'] = dim_date['date'].dt.dayofweek + 1  # 1=Monday, 7=Sunday
dim_date['is_weekend'] = dim_date['day_of_week'].apply(lambda x: 1 if x in [6, 7] else 0)
dim_date['year_month'] = dim_date['date'].dt.strftime('%Y-%m')

dim_date.to_csv(os.path.join(PROCESSED_PATH, 'dim_date.csv'), index=False)

print(f"  -> Saved dim_products.csv: {stg_products.shape[0]:,} rows")
print(f"  -> Saved dim_geography.csv: {stg_geo.shape[0]:,} rows")
print(f"  -> Saved dim_date.csv: {dim_date.shape[0]:,} days (2016 to 2018)")

print("\n" + "=" * 70)
print("PHASE 5 INTEGRATION & FEATURE ENGINEERING COMPLETE!")
print("=" * 70)
