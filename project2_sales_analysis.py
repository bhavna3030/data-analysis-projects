"""
PROJECT 2 — Sales Performance Analysis
Tools: Python, pandas, matplotlib
Dataset: Simulated 12-month retail sales data (no download needed)

What you'll learn:
  - Data cleaning (nulls, duplicates, type fixes)
  - GroupBy aggregations (like SQL GROUP BY)
  - Pivot tables in pandas
  - Month-over-month trend analysis
  - Writing a business summary from data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import random
from datetime import datetime, timedelta

random.seed(7)

# ─────────────────────────────────────────────
# STEP 1 — Create sample sales dataset
# ─────────────────────────────────────────────

categories  = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Sports']
regions     = ['North', 'South', 'East', 'West']
cat_prices  = {'Electronics': (150, 900), 'Clothing': (20, 120),
               'Home & Kitchen': (30, 250), 'Books': (8, 40), 'Sports': (25, 200)}

rows = []
start = datetime(2024, 1, 1)
for i in range(2000):
    date     = start + timedelta(days=random.randint(0, 364))
    category = random.choice(categories)
    region   = random.choice(regions)
    lo, hi   = cat_prices[category]
    price    = round(random.uniform(lo, hi), 2)
    qty      = random.randint(1, 10)
    revenue  = round(price * qty, 2)

    # Inject some dirty data to clean later
    if random.random() < 0.03:
        revenue = None          # 3% null revenues
    if random.random() < 0.015:
        rows.append(rows[-1])   # ~1.5% duplicate rows
        continue

    rows.append([date.strftime('%Y-%m-%d'), category, region, price, qty, revenue])

df = pd.DataFrame(rows, columns=['Date', 'Category', 'Region', 'UnitPrice', 'Quantity', 'Revenue'])
print(f"Raw dataset: {len(df)} rows")
print(df.head(5).to_string(index=False))


# ─────────────────────────────────────────────
# STEP 2 — Data Cleaning
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("STEP 2 — Data Cleaning")
print("="*60)

print(f"Nulls before cleaning:\n{df.isnull().sum()}")
print(f"Duplicates before cleaning: {df.duplicated().sum()}")

# Fix 1: Drop rows where Revenue is null
df.dropna(subset=['Revenue'], inplace=True)

# Fix 2: Remove duplicates
df.drop_duplicates(inplace=True)

# Fix 3: Convert Date to proper datetime
df['Date'] = pd.to_datetime(df['Date'])

# Fix 4: Extract Month and Month name for grouping
df['Month']     = df['Date'].dt.month
df['MonthName'] = df['Date'].dt.strftime('%b')

print(f"\nAfter cleaning: {len(df)} rows remaining")
print(f"Nulls after: {df.isnull().sum().sum()}")
print(f"Duplicates after: {df.duplicated().sum()}")


# ─────────────────────────────────────────────
# STEP 3 — Analysis
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("ANALYSIS 1 — Total revenue by Category")
print("="*60)
cat_summary = df.groupby('Category')['Revenue'].agg(
    total_revenue='sum',
    avg_order_value='mean',
    num_orders='count'
).round(2).sort_values('total_revenue', ascending=False)
cat_summary['revenue_share_pct'] = (
    cat_summary['total_revenue'] / cat_summary['total_revenue'].sum() * 100
).round(1)
print(cat_summary.to_string())


print("\n" + "="*60)
print("ANALYSIS 2 — Monthly revenue trend")
print("="*60)
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
monthly = df.groupby(['Month', 'MonthName'])['Revenue'].sum().reset_index()
monthly = monthly.sort_values('Month')
monthly['MoM_change_pct'] = monthly['Revenue'].pct_change().mul(100).round(1)
print(monthly[['MonthName', 'Revenue', 'MoM_change_pct']].to_string(index=False))


print("\n" + "="*60)
print("ANALYSIS 3 — Revenue by Region")
print("="*60)
region_summary = df.groupby('Region')['Revenue'].sum().sort_values(ascending=False).round(2)
print(region_summary.to_string())


print("\n" + "="*60)
print("ANALYSIS 4 — Pivot: Category vs Region")
print("="*60)
pivot = df.pivot_table(values='Revenue', index='Category', columns='Region', aggfunc='sum').round(0)
print(pivot.to_string())


# ─────────────────────────────────────────────
# STEP 4 — Charts
# ─────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Sales Performance Analysis — 2024', fontsize=14, fontweight='bold')

colors = ['#1F4E79', '#2E75B6', '#4FA3D1', '#7CC4E8', '#B8DFF5']

# Chart 1: Revenue by Category (bar)
axes[0, 0].bar(cat_summary.index, cat_summary['total_revenue'], color=colors)
axes[0, 0].set_title('Total Revenue by Category')
axes[0, 0].set_ylabel('Revenue (₹)')
axes[0, 0].tick_params(axis='x', rotation=15)
for i, v in enumerate(cat_summary['total_revenue']):
    axes[0, 0].text(i, v + 1000, f'₹{v:,.0f}', ha='center', fontsize=8)

# Chart 2: Revenue share pie
axes[0, 1].pie(cat_summary['total_revenue'], labels=cat_summary.index,
               autopct='%1.1f%%', colors=colors, startangle=90)
axes[0, 1].set_title('Revenue Share by Category')

# Chart 3: Monthly trend line
axes[1, 0].plot(monthly['MonthName'], monthly['Revenue'], marker='o',
                color='#1F4E79', linewidth=2)
axes[1, 0].set_title('Monthly Revenue Trend')
axes[1, 0].set_ylabel('Revenue (₹)')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].fill_between(range(len(monthly)), monthly['Revenue'], alpha=0.1, color='#1F4E79')

# Chart 4: Revenue by Region
reg_vals = region_summary.values
reg_keys = region_summary.index
axes[1, 1].barh(reg_keys, reg_vals, color='#2E75B6')
axes[1, 1].set_title('Revenue by Region')
axes[1, 1].set_xlabel('Revenue (₹)')
for i, v in enumerate(reg_vals):
    axes[1, 1].text(v + 500, i, f'₹{v:,.0f}', va='center', fontsize=9)

plt.tight_layout()
out = '/mnt/user-data/outputs/project2_sales_analysis.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f"\n✅ Charts saved to {out}")


# ─────────────────────────────────────────────
# STEP 5 — Business Summary
# ─────────────────────────────────────────────

top_cat   = cat_summary.index[0]
top_share = cat_summary['revenue_share_pct'].iloc[0]
top_month = monthly.loc[monthly['Revenue'].idxmax(), 'MonthName']
top_region = region_summary.index[0]

print("\n" + "="*60)
print("BUSINESS SUMMARY")
print("="*60)
print(f"""
Total revenue (2024): ₹{df['Revenue'].sum():,.0f}
Total orders: {len(df):,}

Key findings:
  1. {top_cat} is the top-performing category, contributing {top_share}% of total revenue.
     This is the single biggest driver — worth prioritizing in promotions.

  2. {top_month} is the strongest month for sales.
     Plan inventory and marketing campaigns to peak around this period.

  3. {top_region} region generates the most revenue.
     Consider whether other regions need different pricing or more sales rep coverage.

  4. Cleaning removed ~{int((2000 - len(df)) / 2000 * 100)}% of records (nulls + duplicates).
     Always clean before any analysis — dirty data = wrong conclusions.
""")

print("Done!")
