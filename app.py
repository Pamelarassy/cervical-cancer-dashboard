import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit Config
st.set_page_config(page_title="Cervical Cancer Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<h3 style='text-align:center;'>Cervical Cancer: Global Snapshot (2022)</h3>", unsafe_allow_html=True)

# Summary Row
col_inc, col_mort = st.columns(2)
with col_inc:
    st.markdown(
        "<div style='color:#004B9B; font-size:14px;'><b>Incidence Rank:</b> 8<br><b>Cases:</b> 662,301</div>",
        unsafe_allow_html=True)
with col_mort:
    st.markdown(
        "<div style='color:#D7191C; font-size:14px;'><b>Mortality Rank:</b> 9<br><b>Deaths:</b> 348,874</div>",
        unsafe_allow_html=True)

# 2x2 Grid
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# Choropleth Map
with row1_col1:
    df_map = pd.read_csv("dataset-asr-inc-both-sexes-in-2022-cervix-uteri.csv")
    df_map.columns = df_map.columns.str.strip()
    fig_map = px.choropleth(
        df_map,
        locations="Population",
        locationmode="country names",
        color="ASR (World) per 100 000",
        color_continuous_scale="YlOrRd",
    )
    fig_map.update_layout(height=180, margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig_map, use_container_width=True)

# HPV Vaccine Coverage Line Chart
with row1_col2:
    df_line = pd.read_csv("data.csv")
    df_line.columns = df_line.columns.str.strip()
    df_line = df_line[['ParentLocationCode', 'Period', 'FactValueNumeric']].dropna()
    df_group = df_line.groupby(['ParentLocationCode', 'Period'], as_index=False)['FactValueNumeric'].mean()
    fig_line = px.line(df_group, x='Period', y='FactValueNumeric', color='ParentLocationCode', markers=True)
    fig_line.update_layout(height=180, yaxis_range=[0, 100], margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_line, use_container_width=True)

# Pie Chart: Distribution by Continent
with row2_col1:
    df_pie = pd.read_csv("dataset-absolute-numbers-inc-both-sexes-in-2022-cervix-uteri.csv")
    df_pie.columns = df_pie.columns.str.strip().str.lower()
    fig_pie = px.pie(df_pie, names="label", values="total", hole=0.4)
    fig_pie.update_layout(height=180, margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# Biopsy & Cancer Among HPV-Positive
with row2_col2:
    df = pd.read_csv("cleaned_cervical_cancer_dataset.csv")
    df.columns = df.columns.str.strip().str.lower()

    # Biopsy rate by age group
    bins = [10, 20, 30, 40, 50, 60]
    labels_age = ['10-19', '20-29', '30-39', '40-49', '50-59']
    df['age group'] = pd.cut(df['age'], bins=bins, labels=labels_age, right=False)
    trend = df.groupby('age group')['biopsy'].mean().reset_index().dropna()
    fig_biopsy = px.bar(trend, x='biopsy', y='age group', orientation='h', color_discrete_sequence=['#1f77b4'])
    fig_biopsy.update_layout(
        height=180,
        margin=dict(t=10, b=10),
        xaxis_range=[0, 1],
        xaxis_tickformat=".0%",
        showlegend=False
    )
    st.plotly_chart(fig_biopsy, use_container_width=True)
