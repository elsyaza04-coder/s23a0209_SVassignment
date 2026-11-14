# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title='Poverty vs Income', page_icon='📊', layout='wide'
)

st.title('📈 Poverty Rate vs. Median Income')
st.markdown(
    'Comparing absolute poverty rates against monthly household median incomes'
    ' across all parliamentary constituencies (2020–2024).'
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
    'Poverty Rate vs. Median Income (by Parliament, 2020-2024)', weight='bold'
)
ax1.set_xlabel('Median Income (RM)')
ax1.set_ylabel('Absolute Poverty Rate (%)')
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='State')
fig1.tight_layout()
st.pyplot(fig1)
