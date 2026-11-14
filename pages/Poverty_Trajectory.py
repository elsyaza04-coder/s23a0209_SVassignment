# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title='Poverty Trajectory', page_icon='📈', layout='wide'
)

st.title('📈 Post-Pandemic Poverty Trajectory (2022 vs. 2024)')
st.markdown(
    'Analyzing shifts and recovery slopes in absolute poverty rates from the'
    ' pandemic-impacted baseline (2022) to the recovery phase (2024).'
)


@st.cache_data
def load_data():
  URL_POVERTY = 'https://storage.dosm.gov.my/hies/hh_poverty_parlimen.parquet'
  URL_INCOME = 'https://storage.dosm.gov.my/hies/hh_income_parlimen.parquet'
  URL_POP = 'https://storage.dosm.gov.my/population/population_parlimen.parquet'

  df_poverty = pd.read_parquet(URL_POVERTY)
  df_income = pd.read_parquet(URL_INCOME)
  df_pop = pd.read_parquet(URL_POP)

  df_poverty['date'] = pd.to_datetime(df_poverty['date'])
  df_income['date'] = pd.to_datetime(df_income['date'])
  df_pop['date'] = pd.to_datetime(df_pop['date'])

  df_poverty_filtered = df_poverty[
      (df_poverty['date'] >= '2020-01-01')
      & (df_poverty['date'] <= '2024-12-31')
  ]
  df_income_filtered = df_income[
      (df_income['date'] >= '2020-01-01')
      & (df_income['date'] <= '2024-12-31')
  ]
  df_pop_filtered = df_pop[
      (df_pop['date'] >= '2020-01-01') & (df_pop['date'] <= '2024-12-31')
  ]

  df_pop_subset = df_pop_filtered[
      (df_pop_filtered['sex'] == 'both')
      & (df_pop_filtered['age'] == 'overall')
      & (df_pop_filtered['ethnicity'] == 'overall')
  ]

  df_merged = pd.merge(
      df_poverty_filtered,
      df_income_filtered,
      on=['date', 'state', 'parlimen'],
      how='inner',
  )
  df_final = pd.merge(
      df_merged,
      df_pop_subset[['date', 'state', 'parlimen', 'population']],
      on=['date', 'state', 'parlimen'],
      how='inner',
  )
  return df_final


with st.spinner('Loading data...'):
  df_final = load_data()

df_trajectory = (
    df_final[df_final['date'].dt.year.isin([2022, 2024])]
    .pivot(index=['state', 'parlimen'], columns='date', values='poverty_absolute')
    .reset_index()
)
df_trajectory.columns = ['state', 'parlimen', 'poverty_2022', 'poverty_2024']
df_trajectory = df_trajectory.dropna()
df_trajectory['poverty_shift'] = (
    df_trajectory['poverty_2024'] - df_trajectory['poverty_2022']
)
mean_shift = df_trajectory['poverty_shift'].mean()

# --- Plot 1: Distribution of Shifts ---
st.subheader('📊 Distribution of Shifts in Absolute Poverty Rates')
fig3, ax3 = plt.subplots(figsize=(12, 5))
sns.histplot(
    data=df_trajectory,
    x='poverty_shift',
    kde=True,
    color='purple',
    bins=30,
    ax=ax3,
)
ax3.axvline(
    0, color='red', linestyle='--', linewidth=1.5, label='No Change'
)
ax3.axvline(
    mean_shift,
    color='blue',
    linestyle='-.',
    linewidth=1.5,
    label=f'Average Shift ({mean_shift:.2f}%)',
)
ax3.set_title(
    'Distribution of Shifts in Absolute Poverty Rates by Constituency (2022 to'
    ' 2024)',
    fontsize=14,
    weight='bold',
)
ax3.set_xlabel('Change in Absolute Poverty Rate (% Points)', fontsize=11)
ax3.set_ylabel('Number of Constituencies', fontsize=11)
ax3.legend()
ax3.grid(True, linestyle='--', alpha=0.5)
fig3.tight_layout()
st.pyplot(fig3)

st.markdown('---')

# --- Plot 2: Trajectory Slope Chart ---
st.subheader('📈 Top Recovering Constituencies Slope Chart')
top_improvers = df_trajectory.sort_values(by='poverty_shift').head(10)

fig4, ax4 = plt.subplots(figsize=(14, 7))
sns.set_theme(style='whitegrid')

for idx, row in df_trajectory.iterrows():
  ax4.plot(
      [2022, 2024],
      [row['poverty_2022'], row['poverty_2024']],
      color='lightgray',
      alpha=0.5,
      linewidth=1,
  )

for idx, row in top_improvers.iterrows():
  ax4.plot(
      [2022, 2024],
      [row['poverty_2022'], row['poverty_2024']],
      color='teal',
      alpha=0.9,
      linewidth=2.5,
  )
  clean_name = (
      row['parlimen'].split(' ', 1)[1]
      if ' ' in row['parlimen']
      else row['parlimen']
  )
  ax4.text(
      2021.95,
      row['poverty_2022'],
      f"{clean_name} ({row['poverty_2022']:.1f}%)",
      ha='right',
      va='center',
      fontsize=9,
      color='darkslategray',
      weight='bold',
  )
  ax4.text(
      2024.05,
      row['poverty_2024'],
      f"{row['poverty_2024']:.1f}%",
      ha='left',
      va='center',
      fontsize=9,
      color='darkslategray',
      weight='bold',
  )

mean_2022 = df_trajectory['poverty_2022'].mean()
mean_2024 = df_trajectory['poverty_2024'].mean()
ax4.plot(
    [2022, 2024],
    [mean_2022, mean_2024],
    color='red',
    linestyle='--',
    linewidth=4,
    marker='o',
    label=f'National Average Trend ({mean_shift:.2f}% shift)',
)
ax4.text(
    2021.90,
    mean_2022,
    f'Avg: {mean_2022:.2f}%',
    ha='right',
    va='center',
    fontsize=11,
    color='red',
    weight='bold',
)
ax4.text(
    2024.10,
    mean_2024,
    f'Avg: {mean_2024:.2f}%',
    ha='left',
    va='center',
    fontsize=11,
    color='red',
    weight='bold',
)

ax4.set_title(
    'Post-Pandemic Poverty Trajectory by Constituency (2022 vs. 2024)\nHighlighting'
    ' Top 10 Recovering Constituencies',
    fontsize=14,
    weight='bold',
)
ax4.set_ylabel('Absolute Poverty Rate (%)', fontsize=11)
ax4.set_xticks([2022, 2024])
ax4.set_xticklabels(
    ['2022 (Pandemic Shock)', '2024 (Recovery Phase)'],
    fontsize=12,
    weight='bold',
)
ax4.set_xlim(2021.2, 2024.8)
ax4.grid(True, axis='y', linestyle='--', alpha=0.7)
ax4.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='none')
fig4.tight_layout()
st.pyplot(fig4)
