"""
PROJECT 1 — HR Attrition Study
Tools: Python, SQLite (SQL), pandas, matplotlib
Dataset: Simulated IBM-style HR data (no download needed)

What you'll learn:
  - Creating a SQLite database from a CSV-style dataset
  - Writing SQL queries with WHERE, GROUP BY, JOIN, CASE
  - Attrition analysis by department and tenure
  - Building a simple pivot-style summary
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import random
import os

random.seed(42)

# ─────────────────────────────────────────────
# STEP 1 — Create sample HR dataset
# ─────────────────────────────────────────────

departments   = ['Sales', 'Engineering', 'HR', 'Finance', 'Marketing']
roles         = ['Analyst', 'Manager', 'Executive', 'Director', 'Specialist']
dept_weights  = [0.30, 0.25, 0.15, 0.15, 0.15]

rows = []
for emp_id in range(1, 1001):
    dept       = random.choices(departments, weights=dept_weights)[0]
    role       = random.choice(roles)
    tenure     = random.randint(0, 15)            # years at company
    age        = random.randint(22, 55)
    salary     = random.randint(30000, 120000)
    perf_score = random.randint(1, 5)             # 1=low, 5=high

    # Attrition logic: Sales + short tenure = higher chance of leaving
    base_chance = 0.12
    if dept == 'Sales':
        base_chance += 0.18
    if tenure < 2:
        base_chance += 0.20
    if perf_score <= 2:
        base_chance += 0.10

    attrition = 'Yes' if random.random() < base_chance else 'No'

    rows.append([emp_id, dept, role, tenure, age, salary, perf_score, attrition])

df = pd.DataFrame(rows, columns=[
    'EmployeeID', 'Department', 'Role', 'YearsAtCompany',
    'Age', 'MonthlySalary', 'PerformanceScore', 'Attrition'
])

print(f"Dataset created: {len(df)} employees")
print(df.head(5).to_string(index=False))


# ─────────────────────────────────────────────
# STEP 2 — Load into SQLite database
# ─────────────────────────────────────────────

conn = sqlite3.connect(':memory:')   # in-memory DB, no file needed
df.to_sql('employees', conn, index=False, if_exists='replace')
print("\n✅ Data loaded into SQLite table: employees")


# ─────────────────────────────────────────────
# STEP 3 — SQL Queries
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("QUERY 1 — Overall attrition rate")
print("="*60)
q1 = """
SELECT
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_company,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS attrition_rate_pct
FROM employees;
"""
print(pd.read_sql_query(q1, conn).to_string(index=False))


print("\n" + "="*60)
print("QUERY 2 — Attrition rate by Department")
print("="*60)
q2 = """
SELECT
    Department,
    COUNT(*) AS total,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_company,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS attrition_pct
FROM employees
GROUP BY Department
ORDER BY attrition_pct DESC;
"""
dept_df = pd.read_sql_query(q2, conn)
print(dept_df.to_string(index=False))


print("\n" + "="*60)
print("QUERY 3 — Attrition by Tenure bucket (new vs experienced)")
print("="*60)
q3 = """
SELECT
    CASE
        WHEN YearsAtCompany < 2  THEN '0-1 years'
        WHEN YearsAtCompany < 5  THEN '2-4 years'
        WHEN YearsAtCompany < 10 THEN '5-9 years'
        ELSE '10+ years'
    END AS tenure_group,
    COUNT(*) AS total,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_company,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS attrition_pct
FROM employees
GROUP BY tenure_group
ORDER BY attrition_pct DESC;
"""
tenure_df = pd.read_sql_query(q3, conn)
print(tenure_df.to_string(index=False))


print("\n" + "="*60)
print("QUERY 4 — High-risk group: Sales dept + tenure < 2 years")
print("="*60)
q4 = """
SELECT
    Department,
    Role,
    COUNT(*) AS headcount,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_company,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS attrition_pct
FROM employees
WHERE Department = 'Sales' AND YearsAtCompany < 2
GROUP BY Department, Role
ORDER BY attrition_pct DESC;
"""
print(pd.read_sql_query(q4, conn).to_string(index=False))


print("\n" + "="*60)
print("QUERY 5 — Average salary of employees who left vs stayed")
print("="*60)
q5 = """
SELECT
    Attrition,
    ROUND(AVG(MonthlySalary), 0) AS avg_salary,
    ROUND(AVG(YearsAtCompany), 1) AS avg_tenure,
    ROUND(AVG(PerformanceScore), 2) AS avg_perf_score
FROM employees
GROUP BY Attrition;
"""
print(pd.read_sql_query(q5, conn).to_string(index=False))


# ─────────────────────────────────────────────
# STEP 4 — Charts
# ─────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('HR Attrition Analysis', fontsize=14, fontweight='bold')

# Chart 1: Attrition % by department
axes[0].barh(dept_df['Department'], dept_df['attrition_pct'], color='#1F4E79')
axes[0].set_xlabel('Attrition Rate (%)')
axes[0].set_title('Attrition Rate by Department')
for i, v in enumerate(dept_df['attrition_pct']):
    axes[0].text(v + 0.3, i, f'{v}%', va='center', fontsize=9)

# Chart 2: Attrition % by tenure group
axes[1].bar(tenure_df['tenure_group'], tenure_df['attrition_pct'], color='#2E75B6')
axes[1].set_xlabel('Tenure Group')
axes[1].set_ylabel('Attrition Rate (%)')
axes[1].set_title('Attrition Rate by Tenure')
for i, v in enumerate(tenure_df['attrition_pct']):
    axes[1].text(i, v + 0.3, f'{v}%', ha='center', fontsize=9)

plt.tight_layout()
out = '/mnt/user-data/outputs/project1_hr_attrition.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f"\n✅ Chart saved to {out}")


# ─────────────────────────────────────────────
# STEP 5 — Business Summary (like a BA would write)
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("BUSINESS SUMMARY")
print("="*60)
overall = pd.read_sql_query(q1, conn)
rate = overall['attrition_rate_pct'].values[0]
top_dept = dept_df.iloc[0]
top_tenure = tenure_df.iloc[0]

print(f"""
Overall attrition rate: {rate}%

Key findings:
  1. {top_dept['Department']} has the highest attrition at {top_dept['attrition_pct']}% —
     significantly above the company average.

  2. Employees in their first {top_tenure['tenure_group']} are leaving at {top_tenure['attrition_pct']}%,
     the highest of any tenure group. This suggests an onboarding or early engagement problem.

  3. Employees who left had a lower average salary than those who stayed,
     indicating compensation may be a factor worth investigating further.

Recommendation:
  Focus retention efforts on Sales new-joiners in their first 2 years.
  Consider stay interviews at the 6-month and 1-year marks for that group.
""")

conn.close()
print("Done!")
