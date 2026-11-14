# -*- coding: utf-8 -*-
"""Streamlit Multi-Page App: Home / Overview Page (app.py)
"""

import pandas as pd
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title='Malaysia Parliament Socioeconomic Dashboard',
    page_icon='🇲🇾',
    layout='wide',
)

# --- MAIN TITLE & INTRODUCTION ---
st.title('🇲🇾 Malaysia Parliament Socioeconomic & Poverty Dashboard')
st.markdown(
    """
    Welcome to the **Malaysia Parliament Socioeconomic & Poverty Trajectory Dashboard**. 
    This application utilizes official open data from the Department of Statistics Malaysia (DOSM) 
    to analyze household income, absolute poverty rates, and population demographics across 
    all 222 parliamentary constituencies.
    """
)

st.markdown('---')

# --- QUICK NAVIGATION GUIDE ---
st.header('📂 Explore the Dashboard Pages')
st.markdown(
    'Use the **sidebar navigation menu on the left** to explore the different visualization pages:'
)

col1, col2, col3 = st.columns(3)

with col1:
  st.subheader('📈 1. Poverty vs. Income')
  st.write(
      'Examines the macro-level relationship between median household income'
      ' and absolute poverty rates across all states.'
  )

with col2:
  st.subheader('🫧 2. State Bubble Map')
  st.write(
      'An interactive state-level breakdown where bubble sizes reflect the'
      ' population scale of each parliamentary constituency.'
  )

with col3:
  st.subheader('📉 3. Poverty Trajectory')
  st.write(
      'Traces post-pandemic economic recovery and shifts in poverty rates from'
      ' the 2022 baseline to 2024.'
  )

st.markdown('---')

# --- DATA SOURCE INFO ---
st.info(
    '💡 **Data Sources:** Official DOSM Open Data Portals (Household Income & '
    'Basic Amenities Survey / HIES, and Parliamentary Population Demographics Parquet datasets).'
)
