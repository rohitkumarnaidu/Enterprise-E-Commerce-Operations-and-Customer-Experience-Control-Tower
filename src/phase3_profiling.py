"""
Phase 3 - Data Profiling Script
Generates all profiling outputs needed for the Jupyter notebook
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("PHASE 3 — DATA PROFILING REPORT")
print("Brazilian E-Commerce (Olist) Dataset")
print("=" * 70)

# ── Load all datasets ────────────────────────────────────────────────────────
orders     = pd.read_csv('data/raw/olist_orders_dataset.csv')
items      = pd.read_csv('data/raw/olist_order_items_dataset.csv')
customers  = pd.read_csv('data/raw/olist_customers_dataset.csv')
products   = pd.read_csv('data/raw/olist_products_dataset.csv')
sellers    = pd.read_csv('data/raw/olist_sellers_dataset.csv')
payments   = pd.read_csv('data/raw/olist_order_payments_dataset.csv')
reviews    = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')
geo        = pd.read_csv('data/raw/olist_geolocation_dataset.csv')
cat_trans  = pd.read_csv('data/raw/product_category_name_translation.csv')

# Parse dates
date_cols = ['order_purchase_timestamp','order_approved_at',
             'order_delivered_carrier_date','order_delivered_customer_date',
             'order_estimated_delivery_date']
for c in date_cols:
    orders[c] = pd.to_datetime(orders[c], errors='coerce')

reviews['review_creation_date']   = pd.to_datetime(reviews['review_creation_date'], errors='coerce')
reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'], errors='coerce')

# ── ORDERS ───────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("1. ORDERS TABLE")
print("─" * 70)
print(f"Shape                    : {orders.shape}")
print(f"Unique order_id          : {orders['order_id'].nunique()}")
print(f"Duplicate order_id       : {orders.duplicated('order_id').sum()}")
print(f"\nNull counts:")
print(orders.isnull().sum().to_string())

# Timestamp sequence errors
delivered = orders[orders['order_status'] == 'delivered'].copy()
ts_err = (delivered['order_delivered_customer_date'] < delivered['order_purchase_timestamp']).sum()
est_before_purchase = (orders['order_estimated_delivery_date'] < orders['order_purchase_timestamp']).sum()
delivered_no_date = ((orders['order_status'] == 'delivered') & orders['order_delivered_customer_date'].isnull()).sum()

print(f"\nDelivery before purchase (sequence error) : {ts_err}")
print(f"Estimated delivery before purchase        : {est_before_purchase}")
print(f"Status=delivered but no delivery date     : {delivered_no_date}")
print(f"\nOrder status distribution:")
print(orders['order_status'].value_counts().to_string())
print(f"\nDate ranges:")
print(f"  Purchase : {orders['order_purchase_timestamp'].min()}  to  {orders['order_purchase_timestamp'].max()}")

# ── ORDER ITEMS ──────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("2. ORDER ITEMS TABLE")
print("─" * 70)
print(f"Shape                           : {items.shape}")
print(f"Duplicate order_id+order_item_id: {items.duplicated(['order_id','order_item_id']).sum()}")
print(f"Missing product_id              : {items['product_id'].isnull().sum()}")
print(f"Missing seller_id               : {items['seller_id'].isnull().sum()}")
print(f"Price <= 0                      : {(items['price'] <= 0).sum()}")
print(f"Freight < 0                     : {(items['freight_value'] < 0).sum()}")
items_per_order = items.groupby('order_id').size()
print(f"Items per order - max           : {items_per_order.max()}")
print(f"Items per order - mean          : {round(items_per_order.mean(), 2)}")
print(f"Orders with 5+ items            : {(items_per_order >= 5).sum()}")
print(f"GMV (sum of price)              : R$ {items['price'].sum():,.2f}")
print(f"Total freight                   : R$ {items['freight_value'].sum():,.2f}")

# ── CUSTOMERS ────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("3. CUSTOMERS TABLE")
print("─" * 70)
print(f"Shape                    : {customers.shape}")
print(f"Unique customer_id       : {customers['customer_id'].nunique()}")
print(f"Unique customer_unique_id: {customers['customer_unique_id'].nunique()}")
print(f"Repeat customers         : {customers.shape[0] - customers['customer_unique_id'].nunique()}")
print(f"Missing fields           : {customers.isnull().sum().to_string()}")
print(f"\nTop 5 states by customer count:")
print(customers['customer_state'].value_counts().head(5).to_string())

# ── PRODUCTS ─────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("4. PRODUCTS TABLE")
print("─" * 70)
print(f"Shape                   : {products.shape}")
print(f"Unique product_id       : {products['product_id'].nunique()}")
print(f"\nNull counts:")
print(products.isnull().sum().to_string())
cat_coverage = products['product_category_name'].notna().sum()
print(f"\nCategory coverage: {cat_coverage} / {len(products)} ({round(cat_coverage/len(products)*100,1)}%)")
trans_cats = set(cat_trans['product_category_name'].tolist())
prod_cats  = set(products['product_category_name'].dropna().tolist())
untranslated = prod_cats - trans_cats
print(f"Categories without English translation: {len(untranslated)}")
invalid_weight = (products['product_weight_g'] <= 0).sum()
print(f"Products with weight <= 0: {invalid_weight}")

# ── SELLERS ──────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("5. SELLERS TABLE")
print("─" * 70)
print(f"Shape              : {sellers.shape}")
print(f"Unique seller_id   : {sellers['seller_id'].nunique()}")
print(f"Null counts        : {sellers.isnull().sum().to_string()}")
print(f"\nTop 5 seller states:")
print(sellers['seller_state'].value_counts().head(5).to_string())

# ── PAYMENTS ─────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("6. PAYMENTS TABLE")
print("─" * 70)
print(f"Shape                              : {payments.shape}")
print(f"Unique order_id in payments        : {payments['order_id'].nunique()}")
print(f"Duplicate order+payment_sequential : {payments.duplicated(['order_id','payment_sequential']).sum()}")
print(f"Negative payment_value             : {(payments['payment_value'] < 0).sum()}")
print(f"Zero payment_value                 : {(payments['payment_value'] == 0).sum()}")
multi_pay = payments.groupby('order_id').size()
print(f"Orders with multiple payment rows  : {(multi_pay > 1).sum()}")
print(f"Max payment rows for one order     : {multi_pay.max()}")
print(f"\nPayment type distribution:")
print(payments['payment_type'].value_counts().to_string())
print(f"\nInstallment distribution:")
print(payments['payment_installments'].describe())

# ── REVIEWS ──────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("7. REVIEWS TABLE")
print("─" * 70)
print(f"Shape                         : {reviews.shape}")
print(f"Unique review_id              : {reviews['review_id'].nunique()}")
print(f"Duplicate review_id           : {reviews.duplicated('review_id').sum()}")
print(f"Unique order_id in reviews    : {reviews['order_id'].nunique()}")
multi_rev = reviews.groupby('order_id').size()
print(f"Orders with multiple reviews  : {(multi_rev > 1).sum()}")
print(f"\nNull counts:")
print(reviews.isnull().sum().to_string())
print(f"\nReview score distribution:")
print(reviews['review_score'].value_counts().sort_index().to_string())
pos  = (reviews['review_score'] >= 4).sum()
neu  = (reviews['review_score'] == 3).sum()
neg  = (reviews['review_score'] <= 2).sum()
tot  = len(reviews)
print(f"\nPositive (4-5): {pos} ({round(pos/tot*100,1)}%)")
print(f"Neutral  (3)  : {neu} ({round(neu/tot*100,1)}%)")
print(f"Negative (1-2): {neg} ({round(neg/tot*100,1)}%)")
reviews['response_hours'] = (reviews['review_answer_timestamp'] - reviews['review_creation_date']).dt.total_seconds() / 3600
print(f"Avg response hours: {round(reviews['response_hours'].mean(), 1)}")

# ── GEOLOCATION ──────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("8. GEOLOCATION TABLE")
print("─" * 70)
print(f"Shape                          : {geo.shape}")
print(f"Unique ZIP prefixes            : {geo['geolocation_zip_code_prefix'].nunique()}")
print(f"Full row duplicates            : {geo.duplicated().sum()}")
print(f"Null counts                    : {geo.isnull().sum().to_string()}")
invalid_lat = ((geo['geolocation_lat'] < -35) | (geo['geolocation_lat'] > 5)).sum()
invalid_lng = ((geo['geolocation_lng'] < -74) | (geo['geolocation_lng'] > -28)).sum()
print(f"Invalid latitude (outside Brazil): {invalid_lat}")
print(f"Invalid longitude (outside Brazil): {invalid_lng}")
coords_per_zip = geo.groupby('geolocation_zip_code_prefix').size()
print(f"Avg coordinates per ZIP prefix : {round(coords_per_zip.mean(), 1)}")
print(f"Max coordinates per ZIP prefix : {coords_per_zip.max()}")

# ── DATA QUALITY REPORT ──────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("DATA QUALITY REPORT SUMMARY")
print("=" * 70)

dq_records = [
    {'Table': 'orders',      'Rule': 'Missing order_approved_at',              'Count': 160,    'Pct': round(160/99441*100,2),    'Severity': 'Medium', 'Treatment': 'Flag as missing_approval_flag'},
    {'Table': 'orders',      'Rule': 'Missing order_delivered_carrier_date',   'Count': 1783,   'Pct': round(1783/99441*100,2),   'Severity': 'Medium', 'Treatment': 'Flag as missing_carrier_flag'},
    {'Table': 'orders',      'Rule': 'Missing order_delivered_customer_date',  'Count': 2965,   'Pct': round(2965/99441*100,2),   'Severity': 'High',   'Treatment': 'Flag; exclude from delivery calcs'},
    {'Table': 'orders',      'Rule': 'Status=delivered but no delivery date',  'Count': delivered_no_date, 'Pct': round(delivered_no_date/99441*100,2), 'Severity': 'High', 'Treatment': 'Flag as delivered_status_mismatch_flag'},
    {'Table': 'order_items', 'Rule': 'Price <= 0',                             'Count': int((items['price']<=0).sum()), 'Pct': round((items['price']<=0).sum()/len(items)*100,2), 'Severity': 'High', 'Treatment': 'Exclude from GMV; flag'},
    {'Table': 'order_items', 'Rule': 'Freight < 0',                            'Count': int((items['freight_value']<0).sum()), 'Pct': 0.0, 'Severity': 'Low', 'Treatment': 'Clip to 0'},
    {'Table': 'products',    'Rule': 'Missing product_category_name',          'Count': 610,    'Pct': round(610/32951*100,2),    'Severity': 'Medium', 'Treatment': 'Label as unknown_category'},
    {'Table': 'products',    'Rule': 'Missing physical dimensions/weight',      'Count': 2,      'Pct': round(2/32951*100,2),      'Severity': 'Low',    'Treatment': 'Flag; exclude from volume calc'},
    {'Table': 'payments',    'Rule': 'Multiple payment rows per order',         'Count': 2961,   'Pct': round(2961/99441*100,2),   'Severity': 'High',   'Treatment': 'Aggregate to order level'},
    {'Table': 'payments',    'Rule': 'payment_type = not_defined',             'Count': 3,      'Pct': round(3/103886*100,4),     'Severity': 'Low',    'Treatment': 'Label as unknown'},
    {'Table': 'reviews',     'Rule': 'Duplicate review_id values',             'Count': 814,    'Pct': round(814/99224*100,2),    'Severity': 'Medium', 'Treatment': 'Deduplicate; keep latest'},
    {'Table': 'reviews',     'Rule': 'Multiple reviews per order',             'Count': 547,    'Pct': round(547/99224*100,2),    'Severity': 'Medium', 'Treatment': 'Aggregate to order level'},
    {'Table': 'reviews',     'Rule': 'Missing review_comment_title',           'Count': 87656,  'Pct': round(87656/99224*100,2),  'Severity': 'Low',    'Treatment': 'Expected — flag review_comment_flag'},
    {'Table': 'reviews',     'Rule': 'Missing review_comment_message',         'Count': 58247,  'Pct': round(58247/99224*100,2),  'Severity': 'Low',    'Treatment': 'Expected — flag review_comment_flag'},
    {'Table': 'geolocation', 'Rule': 'Full row duplicates',                    'Count': 261831, 'Pct': round(261831/1000163*100,2),'Severity': 'High',  'Treatment': 'Drop exact duplicates first'},
    {'Table': 'geolocation', 'Rule': 'Multiple coords per ZIP prefix',         'Count': 1000163,'Pct': 100.0,                    'Severity': 'High',   'Treatment': 'Aggregate: median lat/lng per ZIP'},
    {'Table': 'geolocation', 'Rule': 'Invalid latitude (outside Brazil bbox)', 'Count': invalid_lat, 'Pct': round(invalid_lat/1000163*100,4), 'Severity': 'Medium', 'Treatment': 'Flag and exclude from distance calc'},
]

dq = pd.DataFrame(dq_records)
print(dq.to_string(index=False))

# Save
dq.to_csv('data/processed/data_quality_report.csv', index=False)
print("\n✅ Data quality report saved to data/processed/data_quality_report.csv")
print("\n✅ Phase 3 profiling complete.")
