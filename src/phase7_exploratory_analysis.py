"""
Phase 7 - Exploratory Business, Operations & Customer Experience Analysis
Generates analytical charts and deep-dive business insights across 6 core pillars:
1. Executive & Revenue Dynamics
2. Delivery Logistics & SLA Performance
3. Customer Experience & CSAT Drivers
4. Seller Performance Quadrant & Scorecards
5. Category Economics & Freight Friction
6. Payment Methods & Customer Retention
"""
import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['axes.titlesize'] = 12

DB_PATH = 'data/processed/ecommerce_control_tower.db'
FIGURES_PATH = 'reports/figures/'
os.makedirs(FIGURES_PATH, exist_ok=True)

print("=" * 75)
print("PHASE 7 — EXPLORATORY DATA ANALYSIS & DEEP-DIVE BUSINESS INSIGHTS")
print("=" * 75)

conn = sqlite3.connect(DB_PATH)

# Load fact and dimension tables
fact_orders = pd.read_sql_query("SELECT * FROM fact_orders;", conn)
fact_items = pd.read_sql_query("SELECT * FROM fact_order_items;", conn)
dim_customers = pd.read_sql_query("SELECT * FROM dim_customers;", conn)
dim_sellers = pd.read_sql_query("SELECT * FROM dim_sellers;", conn)
dim_products = pd.read_sql_query("SELECT * FROM dim_products;", conn)
fact_payments = pd.read_sql_query("SELECT * FROM fact_payments;", conn)

fact_orders['order_purchase_timestamp'] = pd.to_datetime(fact_orders['order_purchase_timestamp'])

# ── 1. EXECUTIVE REVENUE & ORDER TRAJECTORY ──────────────────────────────────
print("\n[1/6] Analyzing Executive Revenue & Order Trajectories...")
monthly_rev = fact_orders.set_index('order_purchase_timestamp').resample('ME').agg(
    orders=('order_id', 'count'),
    gmv=('gmv', 'sum')
).reset_index()

# Filter full operating months (Jan 2017 to Aug 2018)
monthly_rev = monthly_rev[(monthly_rev['order_purchase_timestamp'] >= '2017-01-01') & 
                          (monthly_rev['order_purchase_timestamp'] <= '2018-08-31')]
monthly_rev['month_year'] = monthly_rev['order_purchase_timestamp'].dt.strftime('%b %Y')

fig, ax1 = plt.subplots(figsize=(12, 6))
color = '#1f77b4'
ax1.set_xlabel('Month-Year', fontweight='bold')
ax1.set_ylabel('Monthly GMV (R$)', color=color, fontweight='bold')
ax1.plot(monthly_rev['month_year'], monthly_rev['gmv'], color=color, marker='o', linewidth=2.5, label='GMV (R$)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(range(len(monthly_rev['month_year'])))
ax1.set_xticklabels(monthly_rev['month_year'], rotation=45, ha='right')

ax2 = ax1.twinx()
color = '#ff7f0e'
ax2.set_ylabel('Order Count', color=color, fontweight='bold')
ax2.bar(monthly_rev['month_year'], monthly_rev['orders'], color=color, alpha=0.3, width=0.4, label='Orders')
ax2.tick_params(axis='y', labelcolor=color)
ax2.grid(False)

plt.title('Monthly GMV and Order Volume Trajectory (2017 - 2018)', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
fig_path = os.path.join(FIGURES_PATH, '01_monthly_gmv_orders_trend.png')
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  ✓ Saved {fig_path}")

# ── 2. DELIVERY SLA & DELAY DISTRIBUTION ─────────────────────────────────────
print("\n[2/6] Analyzing Delivery SLA Performance & Lead Times...")
delivered_orders = fact_orders[(fact_orders['order_status'] == 'delivered') & (fact_orders['delivery_days'].notna())]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Subplot 1: Delivery Duration Histogram
ax1.hist(delivered_orders['delivery_days'].clip(upper=60), bins=40, color='#2ca02c', edgecolor='white', alpha=0.8)
ax1.axvline(delivered_orders['delivery_days'].median(), color='red', linestyle='--', linewidth=2,
            label=f'Median: {delivered_orders["delivery_days"].median():.1f} days')
ax1.set_title('Distribution of Total Delivery Days (Purchase to Doorstep)', fontweight='bold')
ax1.set_xlabel('Delivery Days')
ax1.set_ylabel('Order Count')
ax1.legend()

# Subplot 2: Delay Days Distribution (Actual vs Promised)
ax2.hist(delivered_orders['delay_days'].clip(lower=-30, upper=30), bins=50, color='#d62728', edgecolor='white', alpha=0.8)
ax2.axvline(0, color='black', linestyle='-', linewidth=2, label='Promised Delivery SLA (Day 0)')
ax2.axvline(delivered_orders['delay_days'].median(), color='blue', linestyle='--', linewidth=2,
            label=f'Median Delay: {delivered_orders["delay_days"].median():.1f} days')
ax2.set_title('Delivery Variance vs Promised SLA (Delay Days)', fontweight='bold')
ax2.set_xlabel('Delay Days (Negative = Early, Positive = Late)')
ax2.set_ylabel('Order Count')
ax2.legend()

plt.tight_layout()
fig_path = os.path.join(FIGURES_PATH, '02_delivery_duration_and_delays.png')
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  ✓ Saved {fig_path}")

# ── 3. CUSTOMER SATISFACTION VS DELIVERY SLA & DELAYS ─────────────────────────
print("\n[3/6] Analyzing Customer CSAT Correlation with Delivery Delays...")
csat_delay = fact_orders[fact_orders['review_score_avg'].notna()].groupby('delay_band').agg(
    avg_csat=('review_score_avg', 'mean'),
    order_count=('order_id', 'count'),
    negative_rate=('low_review_flag', 'mean')
).reindex(['Early or On Time', '1–3 Days Late', '4–7 Days Late', '8+ Days Late', 'Not Delivered']).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 5))
palette = ['#2ca02c', '#ffbb78', '#ff7f0e', '#d62728', '#7f7f7f']
bars = ax1.bar(csat_delay['delay_band'], csat_delay['avg_csat'], color=palette, width=0.55, edgecolor='black', linewidth=0.8)

for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.08, f'{yval:.2f} ★', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax1.set_ylim(0, 5.0)
ax1.set_title('Customer Review Score (CSAT) by Delivery Delay Severity Band', fontsize=13, fontweight='bold', pad=15)
ax1.set_xlabel('Delivery Performance Band', fontweight='bold')
ax1.set_ylabel('Average Review Score (1 to 5 Stars)', fontweight='bold')

plt.tight_layout()
fig_path = os.path.join(FIGURES_PATH, '03_csat_vs_delivery_delay_bands.png')
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  ✓ Saved {fig_path}")

# ── 4. SELLER PERFORMANCE 4-QUADRANT MATRIX ──────────────────────────────────
print("\n[4/6] Constructing Seller Performance 4-Quadrant Matrix...")
active_sellers = dim_sellers[dim_sellers['total_orders'] >= 10].copy()

gmv_median = active_sellers['total_gmv'].median()
csat_benchmark = 4.0

def assign_quadrant(row):
    if row['total_gmv'] >= gmv_median and row['avg_review_score'] >= csat_benchmark:
        return 'Q1: Star Performers (High GMV / High CSAT)'
    elif row['total_gmv'] >= gmv_median and row['avg_review_score'] < csat_benchmark:
        return 'Q2: Operational Risk (High GMV / Low CSAT)'
    elif row['total_gmv'] < gmv_median and row['avg_review_score'] >= csat_benchmark:
        return 'Q3: Niche Champions (Low GMV / High CSAT)'
    else:
        return 'Q4: Underperformers (Low GMV / Low CSAT)'

active_sellers['seller_quadrant'] = active_sellers.apply(assign_quadrant, axis=1)

fig, ax = plt.subplots(figsize=(11, 7))
colors = {
    'Q1: Star Performers (High GMV / High CSAT)': '#2ca02c',
    'Q2: Operational Risk (High GMV / Low CSAT)': '#d62728',
    'Q3: Niche Champions (Low GMV / High CSAT)': '#1f77b4',
    'Q4: Underperformers (Low GMV / Low CSAT)': '#7f7f7f'
}

for q_name, group in active_sellers.groupby('seller_quadrant'):
    ax.scatter(group['total_gmv'], group['avg_review_score'], label=f"{q_name} (n={len(group):,})",
               color=colors[q_name], alpha=0.6, edgecolors='none', s=group['total_orders']*0.8 + 20)

ax.axvline(gmv_median, color='black', linestyle=':', linewidth=1.2)
ax.axhline(csat_benchmark, color='black', linestyle=':', linewidth=1.2)
ax.set_xscale('log')
ax.set_title('Seller Strategic 4-Quadrant Matrix (GMV vs Customer CSAT)', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Total Seller GMV (R$, Log Scale)', fontweight='bold')
ax.set_ylabel('Average Review Score (1 to 5 Stars)', fontweight='bold')
ax.legend(loc='lower left', frameon=True)

plt.tight_layout()
fig_path = os.path.join(FIGURES_PATH, '04_seller_strategic_quadrant_matrix.png')
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  ✓ Saved {fig_path}")

# ── 5. GEOGRAPHIC DISTANCE BAND DEGRADATION ──────────────────────────────────
print("\n[5/6] Analyzing Geospatial Distance Band Logistics Impact...")
dist_perf = fact_items[fact_items['order_status'] == 'delivered'].groupby('distance_band').agg(
    avg_delivery_days=('delivery_days', 'mean'),
    avg_freight=('freight_value', 'mean'),
    late_rate=('late_delivery_flag', lambda x: np.mean(x) * 100),
    total_items=('order_item_id', 'count')
).reindex(['0–100 km', '101–500 km', '501–1,000 km', '1,001–2,000 km', '2,000+ km']).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.bar(dist_perf['distance_band'], dist_perf['avg_delivery_days'], color='#3182bd', width=0.5, label='Avg Delivery Days')
ax1.set_xlabel('Shipping Distance Band (Haversine km)', fontweight='bold')
ax1.set_ylabel('Average Delivery Days', color='#3182bd', fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#3182bd')

ax2 = ax1.twinx()
ax2.plot(dist_perf['distance_band'], dist_perf['avg_freight'], color='#e6550d', marker='s', linewidth=2.5, label='Avg Freight Cost (R$)')
ax2.set_ylabel('Average Freight Cost (R$)', color='#e6550d', fontweight='bold')
ax2.tick_params(axis='y', labelcolor='#e6550d')
ax2.grid(False)

plt.title('Impact of Shipping Distance on Delivery Duration & Freight Cost', fontsize=13, fontweight='bold', pad=15)
fig.tight_layout()
fig_path = os.path.join(FIGURES_PATH, '05_distance_band_logistics_impact.png')
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  ✓ Saved {fig_path}")

# ── 6. PAYMENT INSTRUMENT & REPEAT CUSTOMER ECONOMICS ────────────────────────
print("\n[6/6] Analyzing Payment Mix & Customer Retention Economics...")
pay_mix = fact_payments.groupby('payment_type').agg(
    total_value=('payment_value', 'sum'),
    transaction_count=('order_id', 'count')
).reset_index()
pay_mix['value_pct'] = (pay_mix['total_value'] / pay_mix['total_value'].sum()) * 100

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Payment Methods Donut Chart
colors_donut = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
wedges, texts, autotexts = ax1.pie(pay_mix['total_value'], labels=pay_mix['payment_type'], autopct='%1.1f%%',
                                    startangle=140, colors=colors_donut, wedgeprops=dict(width=0.4, edgecolor='w'))
ax1.set_title('Payment Method Breakdown by Value (GMV)', fontweight='bold')

# Repeat vs One-Time Customer GMV & AOV
cust_cohort = dim_customers.groupby('repeat_customer_flag').agg(
    customer_count=('customer_unique_id', 'count'),
    total_gmv=('total_gmv', 'sum'),
    avg_aov=('average_order_value', 'mean')
).reset_index()
cust_cohort['customer_type'] = cust_cohort['repeat_customer_flag'].map({0: 'One-Time Buyers\n(96.9%)', 1: 'Repeat Buyers\n(3.1%)'})

bars = ax2.bar(cust_cohort['customer_type'], cust_cohort['avg_aov'], color=['#9ecae1', '#3182bd'], width=0.5)
for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 3.0, f'R$ {yval:.2f}', ha='center', va='bottom', fontweight='bold')
ax2.set_title('Average Order Value (AOV): One-Time vs Repeat Buyers', fontweight='bold')
ax2.set_ylabel('Average Order Value (R$)')
ax2.set_ylim(0, cust_cohort['avg_aov'].max() * 1.2)

plt.tight_layout()
fig_path = os.path.join(FIGURES_PATH, '06_payment_mix_and_customer_cohorts.png')
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  ✓ Saved {fig_path}")

print("\n" + "=" * 75)
print("PHASE 7 EXPLORATORY ANALYSIS & VISUALIZATIONS COMPLETE!")
print(f"All 6 high-resolution charts saved to '{FIGURES_PATH}'")
print("=" * 75)

conn.close()
