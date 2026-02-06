import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('fake_category_data.csv')

# Basic info
print(df.shape)
print(df)
print(df.describe())

# Derived metrics
df['expected_time'] = df['incidence_rate'] * df['category_length_seconds']
df['respondents_needed'] = np.ceil(200 / df['incidence_rate']).astype(int)

# Key calculations
total_expected_time = df['expected_time'].sum()
naive_total = df['respondents_needed'].sum()
optimal_total = int(np.ceil(200 / df['incidence_rate'].min()))

print(f"\nTotal Expected Time: {total_expected_time:.1f}s / 480s")
print(f"Naive: {naive_total:,} | Optimal: {optimal_total:,} | Savings: {(1 - optimal_total/naive_total)*100:.1f}%")

# Correlation
corr = df[['incidence_rate', 'category_length_seconds', 'expected_time']].corr()
print(corr.round(3))

# Chart 1: Incidence Rate
plt.figure(figsize=(20,20))
plt.barh(df['category_name'], df['incidence_rate'], color='steelblue')
plt.xlabel('Incidence Rate')
plt.title('Incidence Rate by Category')
plt.tight_layout()
plt.savefig('chart1_incidence_rate.png')
plt.show()

# Chart 2: Survey Length
plt.figure(figsize=(20, 20))
plt.barh(df['category_name'], df['category_length_seconds'], color='coral')
plt.xlabel('Seconds')
plt.title('Survey Length by Category')
plt.tight_layout()
plt.savefig('chart2_survey_length.png')
plt.show()

# Chart 3: Expected Time
plt.figure(figsize=(20,20))
plt.barh(df['category_name'], df['expected_time'], color='green')
plt.xlabel('Seconds')
plt.title('Expected Time (incidence × length)')
plt.tight_layout()
plt.savefig('chart3_expected_time.png')
plt.show()

# Chart 4: Respondents Needed
plt.figure(figsize=(20,20))
plt.barh(df['category_name'], df['respondents_needed'], color='purple')
plt.xlabel('Respondents')
plt.title('Respondents Needed (standalone)')
plt.tight_layout()
plt.savefig('chart4_respondents_needed.png')
plt.show()

# Chart 5: Correlation Heatmap
plt.figure(figsize=(20,20))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig('chart5_correlation.png')
plt.show()
