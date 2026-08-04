import pandas as pd

orders = pd.read_csv('data/raw/olist_orders_dataset.csv')
items = pd.read_csv('data/raw/olist_order_items_dataset.csv')
customers = pd.read_csv('data/raw/olist_customers_dataset.csv')
products = pd.read_csv('data/raw/olist_products_dataset.csv')
sellers = pd.read_csv('data/raw/olist_sellers_dataset.csv')
payments = pd.read_csv('data/raw/olist_order_payments_dataset.csv')
reviews = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')
geo = pd.read_csv('data/raw/olist_geolocation_dataset.csv')

print('=== KEY UNIQUENESS ===')
print('orders - order_id unique:', orders['order_id'].nunique(), '/', len(orders), 'rows')
print('items - order_id+order_item_id dupes:', items.duplicated(['order_id','order_item_id']).sum())
print('customers - customer_id unique:', customers['customer_id'].nunique(), '/', len(customers), 'rows')
print('customers - customer_unique_id unique:', customers['customer_unique_id'].nunique(), '(repeat customers exist)')
print('products - product_id unique:', products['product_id'].nunique(), '/', len(products), 'rows')
print('sellers - seller_id unique:', sellers['seller_id'].nunique(), '/', len(sellers), 'rows')
print('payments - order_id+payment_sequential dupes:', payments.duplicated(['order_id','payment_sequential']).sum())
print('payments - orders with multiple payment rows:', payments.groupby('order_id').size().gt(1).sum())
print('reviews - review_id unique:', reviews['review_id'].nunique(), '/', len(reviews), 'rows')
print('reviews - orders with multiple reviews:', reviews.groupby('order_id').size().gt(1).sum())
print('geo - zip prefixes total:', len(geo), 'rows, unique:', geo['geolocation_zip_code_prefix'].nunique())

print()
print('=== DATE RANGES ===')
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
print('orders purchase date range:', orders['order_purchase_timestamp'].min(), 'to', orders['order_purchase_timestamp'].max())

print()
print('=== ORDER STATUS DISTRIBUTION ===')
print(orders['order_status'].value_counts().to_string())

print()
print('=== REVIEW SCORE DISTRIBUTION ===')
print(reviews['review_score'].value_counts().sort_index().to_string())

print()
print('=== SELLERS PER STATE ===')
print(sellers['seller_state'].value_counts().head(10).to_string())

print()
print('=== PAYMENT TYPE DISTRIBUTION ===')
print(payments['payment_type'].value_counts().to_string())
