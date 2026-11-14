# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title='State Bubble Map', page_icon='🫧', layout='wide')

st.title('🫧 Socioeconomic Bubble Map by State (2024)')
st.markdown(
    'Explore parliamentary constituencies filtered by state. Bubble size'
    ' represents population size.'
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

available_states = sorted(df_final['state'].unique())
selected_state = st.selectbox(
    'Select State for Bubble Chart', available_states, index=0
)

df_state_2024 = df_final[
    (df_final['state'] == selected_state) & (df_final['date'].dt.year == 2024)
].copy()

if not df_state_2024.empty:
  fig2, ax2 = plt.subplots(figsize=(12, 7))
  ax2.scatter(
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
      f"Socioeconomic Map of {selected_state}'s Parliments (2024)\nBubble Size"
      ' Represents Population Size',
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
