"""
PROJECT 3 — Student Score Tracker
Tools: Python, pandas, matplotlib
Dataset: Generated student marks (no download needed)

What you'll learn:
  - Reading/generating structured CSV-style data
  - Conditional logic (pass/fail flags)
  - Aggregations per student and per subject
  - Reusable report function (swap CSV = fresh report)
  - Simple visualizations for a classroom report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import random
import io

random.seed(21)

# ─────────────────────────────────────────────
# STEP 1 — Generate student marks dataset
# ─────────────────────────────────────────────

subjects  = ['Maths', 'Science', 'English', 'History', 'Computer Science']
classes   = ['10A', '10B', '10C']
names     = [
    'Aarav', 'Bhavna', 'Chitra', 'Deepak', 'Esha',
    'Farhan', 'Geetha', 'Harish', 'Isha', 'Jayesh',
    'Kavya', 'Lakshmi', 'Mohan', 'Nisha', 'Omkar',
    'Priya', 'Rahul', 'Sneha', 'Tanvi', 'Uday',
    'Vani', 'Waqar', 'Xena', 'Yash', 'Zara'
]

rows = []
for i, name in enumerate(names):
    cls = classes[i % 3]
    for subject in subjects:
        # Vary marks: some students consistently low, some high
        base = random.randint(30, 95)
        mark = max(0, min(100, base + random.randint(-10, 10)))
        rows.append([name, cls, subject, mark])

df = pd.DataFrame(rows, columns=['StudentName', 'Class', 'Subject', 'Marks'])

# ─────────────────────────────────────────────
# STEP 2 — Add calculated columns
# ─────────────────────────────────────────────

PASS_MARK = 40

df['Grade'] = pd.cut(
    df['Marks'],
    bins=[0, 39, 49, 59, 74, 100],
    labels=['F', 'D', 'C', 'B', 'A'],
    right=True
)
df['Pass'] = df['Marks'] >= PASS_MARK

print("Sample data:")
print(df.head(10).to_string(index=False))


# ─────────────────────────────────────────────
# STEP 3 — Analysis
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("ANALYSIS 1 — Student average and pass/fail summary")
print("="*60)
student_summary = df.groupby('StudentName').agg(
    Average=('Marks', 'mean'),
    Highest=('Marks', 'max'),
    Lowest=('Marks', 'min'),
    Subjects_Failed=('Pass', lambda x: (~x).sum())
).round(1).sort_values('Average', ascending=False)
print(student_summary.to_string())


print("\n" + "="*60)
print("ANALYSIS 2 — Subject-wise class average and pass rate")
print("="*60)
subject_summary = df.groupby('Subject').agg(
    Class_Average=('Marks', 'mean'),
    Pass_Rate_Pct=('Pass', lambda x: round(x.mean() * 100, 1)),
    Highest_Mark=('Marks', 'max'),
    Lowest_Mark=('Marks', 'min')
).round(1).sort_values('Class_Average', ascending=False)
print(subject_summary.to_string())


print("\n" + "="*60)
print("ANALYSIS 3 — Students who need attention (failed 2+ subjects)")
print("="*60)
at_risk = student_summary[student_summary['Subjects_Failed'] >= 2][['Average', 'Subjects_Failed']]
if len(at_risk) > 0:
    print(at_risk.to_string())
else:
    print("No students failed 2+ subjects.")


print("\n" + "="*60)
print("ANALYSIS 4 — Grade distribution across all students")
print("="*60)
grade_dist = df['Grade'].value_counts().sort_index()
print(grade_dist.to_string())


# ─────────────────────────────────────────────
# STEP 4 — Charts
# ─────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Student Score Report — Class 10', fontsize=14, fontweight='bold')

# Chart 1: Average marks per subject
subj_avg = subject_summary['Class_Average'].sort_values()
axes[0, 0].barh(subj_avg.index, subj_avg.values, color='#2E75B6')
axes[0, 0].set_title('Average Marks by Subject')
axes[0, 0].set_xlabel('Average Marks')
axes[0, 0].axvline(x=PASS_MARK, color='red', linestyle='--', label=f'Pass mark ({PASS_MARK})')
axes[0, 0].legend(fontsize=8)
for i, v in enumerate(subj_avg.values):
    axes[0, 0].text(v + 0.3, i, f'{v:.1f}', va='center', fontsize=9)

# Chart 2: Pass rate per subject
pass_rate = subject_summary['Pass_Rate_Pct'].sort_values()
colors_pass = ['#d9534f' if v < 70 else '#1F4E79' for v in pass_rate.values]
axes[0, 1].barh(pass_rate.index, pass_rate.values, color=colors_pass)
axes[0, 1].set_title('Pass Rate by Subject (%)')
axes[0, 1].set_xlabel('Pass Rate (%)')
axes[0, 1].axvline(x=70, color='orange', linestyle='--', label='70% target')
axes[0, 1].legend(fontsize=8)

# Chart 3: Top 10 students by average
top10 = student_summary['Average'].head(10).sort_values()
axes[1, 0].barh(top10.index, top10.values, color='#1F4E79')
axes[1, 0].set_title('Top 10 Students by Average')
axes[1, 0].set_xlabel('Average Marks')

# Chart 4: Grade distribution
grade_colors = {'A': '#1F4E79', 'B': '#2E75B6', 'C': '#4FA3D1', 'D': '#F0A500', 'F': '#d9534f'}
gc = [grade_colors.get(str(g), '#aaa') for g in grade_dist.index]
axes[1, 1].bar(grade_dist.index.astype(str), grade_dist.values, color=gc)
axes[1, 1].set_title('Overall Grade Distribution')
axes[1, 1].set_xlabel('Grade')
axes[1, 1].set_ylabel('Number of Records')
for i, v in enumerate(grade_dist.values):
    axes[1, 1].text(i, v + 0.2, str(v), ha='center', fontsize=9)

plt.tight_layout()
out = '/mnt/user-data/outputs/project3_student_tracker.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f"\n✅ Charts saved to {out}")


# ─────────────────────────────────────────────
# STEP 5 — Reusable report function
# ─────────────────────────────────────────────

def generate_report(dataframe, pass_mark=40):
    """
    Pass any student marks DataFrame with columns:
    [StudentName, Class, Subject, Marks]
    → Returns a printed summary report.

    To use with your own CSV:
        df = pd.read_csv('your_marks.csv')
        generate_report(df)
    """
    total     = len(dataframe['StudentName'].unique())
    avg_score = dataframe['Marks'].mean()
    failed    = (dataframe['Marks'] < pass_mark).sum()
    top_sub   = dataframe.groupby('Subject')['Marks'].mean().idxmax()
    weak_sub  = dataframe.groupby('Subject')['Marks'].mean().idxmin()

    print("\n" + "="*60)
    print("AUTOMATED CLASS REPORT")
    print("="*60)
    print(f"""
  Total students     : {total}
  Overall average    : {avg_score:.1f} / 100
  Pass mark          : {pass_mark}
  Total failed marks : {failed} (across all subjects)

  Strongest subject  : {top_sub}
  Weakest subject    : {weak_sub}  ← needs extra attention

  Students needing support (2+ subject fails):
    {', '.join(at_risk.index.tolist()) if len(at_risk) > 0 else 'None — great class!'}
""")

generate_report(df)
print("Done!")
