# -*- coding: utf-8 -*-
"""Streamlit App: Malaysia Parliament Socioeconomic & Poverty Visualisation
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Malaysia Parliament Poverty & Income Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("🇲🇾 Malaysia Socioeconomic & Poverty Trajectory Dashboard (2020–2024)")
st.markdown(
    "This dashboard analyzes household income, absolute poverty rates, and population demographics across Malaysian parliamentary constituencies using official DOSM data."
)


# --- 2. DATA LOADING & CACHING ---
@st.cache_data
def load_and_process_data():
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


# Load data with a spinner loader
with st.spinner('Loading data from DOSM repository...'):
  df_final = load_and_process_data()

st.success('Data successfully loaded and merged!')

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header('Dashboard Filters')
available_states = sorted(df_final['state'].unique())
selected_state = st.sidebar.selectbox(
    'Select State for Bubble Chart', available_states, index=0
)

# --- 4. VISUALIZATION 1: Scatter Plot (Poverty vs Median Income) ---
st.subheader('📈 Poverty Rate vs. Median Income (All Constituencies)')
fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=df_final,
    x='income_median',
    y='poverty_absolute',
    alpha=0.7,
    hue='state',
    ax=ax1,
)
ax1.set_title(
    'Poverty Rate vs. Median Income (by Parliament, 2020-2024)',
    weight='bold',
)
ax1.set_xlabel('Median Income (RM)')
ax1.set_ylabel('Absolute Poverty Rate (%)')
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='State')
fig1.tight_layout()
st.pyplot(fig1)

# --- 5. VISUALIZATION 2: State-Specific Bubble Chart ---
st.subheader(f'🫧 Socioeconomic Bubble Map for {selected_state} (2024)')

df_state_2024 = df_final[
    (df_final['state'] == selected_state) & (df_final['date'].dt.year == 2024)
].copy()

if not df_state_2024.empty:
  fig2, ax2 = plt.subplots(figsize=(12, 7))
  scatter = ax2.scatter(
      data=df_state_2024,
      x='income_median',
      y='poverty_absolute',
      s=df_state_2024['population'] * 6,
      alpha=0.6,
      c='coral',
      edgecolors='black',
  )

  for idx, row in df_state_2024.iterrows():
    label = (
        row['parlimen'].split(' ', 1)[1]
        if ' ' in row['parlimen']
        else row['parlimen']
    )
    ax2.annotate(
        label,
        (row['income_median'], row['poverty_absolute']),
        textcoords='offset points',
        xytext=(0, 10),
        ha='center',
        fontsize=9,
        weight='bold',
    )

  ax2.set_title(
      f"Socioeconomic Map of {selected_state}'s Parliments (2024)\nBubble Size Represents Population Size",
      fontsize=14,
      weight='bold',
  )
  ax2.set_xlabel('Monthly Household Median Income (RM)', fontsize=11)
  ax2.set_ylabel('Absolute Poverty Incidence (%)', fontsize=11)
  ax2.grid(True, linestyle='--', alpha=0.5)

  ax2.set_xlim(
      df_state_2024['income_median'].min() - 300,
      df_state_2024['income_median'].max() + 300,
  )
  ax2.set_ylim(-1, df_state_2024['poverty_absolute'].max() + 2)

  for pop in [100, 150, 200]:
    ax2.scatter(
        [],
        [],
        s=pop * 6,
        c='coral',
        alpha=0.6,
        edgecolors='black',
        label=f'{pop}k pop',
    )
  ax2.legend(
      scatterpoints=1, labelspacing=1.2, title='Population Size', loc='upper right'
  )

  fig2.tight_layout()
  st.pyplot(fig2)
else:
  st.warning(f'No 2024 data available for {selected_state}.')

# --- 6. DATA PREPARATION FOR TRAJECTORY (2022 vs 2024) ---
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

# --- 7. VISUALIZATION 3: Distribution of Shifts ---
st.subheader(
    '📊 Distribution of Shifts in Absolute Poverty Rates (2022 to 2024)'
)
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

mean_shift = df_trajectory['poverty_shift'].mean()
ax3.axvline(
    mean_shift,
    color='blue',
    linestyle='-.',
    linewidth=1.5,
    label=f'Average Shift ({mean_shift:.2f}%)',
)

ax3.set_title(
    'Distribution of Shifts in Absolute Poverty Rates by Constituency (2022 to 2024)',
    fontsize=14,
    weight='bold',
)
ax3.set_xlabel('Change in Absolute Poverty Rate (% Points)', fontsize=11)
ax3.set_ylabel('Number of Constituencies', fontsize=11)
ax3.legend()
ax3.grid(True, linestyle='--', alpha=0.5)
fig3.tight_layout()
st.pyplot(fig3)

# --- 8. VISUALIZATION 4: Trajectory Slope Chart ---
st.subheader('📈 Post-Pandemic Poverty Trajectory (Top Recovering Constituencies)')
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
      2019.95,
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
    'Post-Pandemic Poverty Trajectory by Constituency (2022 vs. 2024)\nHighlighting Top 10 Recovering Constituencies',
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
