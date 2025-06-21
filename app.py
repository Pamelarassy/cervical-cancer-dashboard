import streamlit as st
import pandas as pd
import plotly.express as px

# Config
st.set_page_config(page_title="Cervical Cancer Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.title("Cervical Cancer: Global Burden and Trends")

# Columns for summary
left_col, right_col = st.columns([2, 1])

with left_col:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "<h5 style='color:#004B9B;'>Incidence</h5><p style='font-size:16px;'><b>Rank:</b> 8<br><b>Cases:</b> 662,301</p>",
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            "<h5 style='color:#D7191C;'>Mortality</h5><p style='font-size:16px;'><b>Rank:</b> 9<br><b>Deaths:</b> 348,874</p>",
            unsafe_allow_html=True)

# Tab layout
tab1, tab2 = st.tabs(["🌍 Global", "📊 Risk & Diagnosis"])

# -------------------- TAB 1 --------------------
with tab1:
    col_map, col_line = st.columns(2)

    with col_map:
        df_asr = pd.read_csv("dataset-asr-inc-both-sexes-in-2022-cervix-uteri.csv")
        df_asr.columns = df_asr.columns.str.strip()
        fig_map = px.choropleth(
            df_asr,
            locations="Population",
            locationmode="country names",
            color="ASR (World) per 100 000",
            color_continuous_scale="YlOrRd",
            title="ASR per 100k",
        )
        fig_map.update_layout(height=200, margin=dict(t=20, b=10))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_line:
        df_line = pd.read_csv("data.csv")
        df_line.columns = df_line.columns.str.strip()
        df_clean = df_line[['ParentLocationCode', 'Period', 'FactValueNumeric']].dropna()
        df_grouped = df_clean.groupby(['ParentLocationCode', 'Period'], as_index=False)['FactValueNumeric'].mean()
        fig_line = px.line(
            df_grouped, x='Period', y='FactValueNumeric', color='ParentLocationCode', markers=True,
            labels={'FactValueNumeric': 'Coverage (%)'}, title="HPV Vaccine Coverage"
        )
        fig_line.update_layout(height=200, yaxis_range=[0, 100], margin=dict(t=20, b=10))
        st.plotly_chart(fig_line, use_container_width=True)

# -------------------- TAB 2 --------------------
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        df_pie = pd.read_csv("dataset-absolute-numbers-inc-both-sexes-in-2022-cervix-uteri.csv")
        df_pie.columns = df_pie.columns.str.strip().str.lower()
        fig_pie = px.pie(df_pie, names="label", values="total", hole=0.4)
        fig_pie.update_layout(height=200, margin=dict(t=20, b=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        biopsy_df = pd.read_csv("cleaned_cervical_cancer_dataset.csv")
        biopsy_df.columns = biopsy_df.columns.str.strip().str.lower()
        bins = [10, 20, 30, 40, 50, 60]
        labels_age = ['10-19', '20-29', '30-39', '40-49', '50-59']
        biopsy_df['age group'] = pd.cut(biopsy_df['age'], bins=bins, labels=labels_age, right=False)
        age_group_trend = biopsy_df.groupby('age group')['biopsy'].mean().reset_index().dropna()
        fig_biopsy = px.bar(age_group_trend, x='biopsy', y='age group', orientation='h', color_discrete_sequence=['#1f77b4'])
        fig_biopsy.update_layout(height=200, xaxis_range=[0, 1], xaxis_tickformat=".0%", margin=dict(t=20, b=10))
        st.plotly_chart(fig_biopsy, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        df = pd.read_csv("cleaned_cervical_cancer_dataset.csv")
        df.columns = df.columns.str.strip()
        hpv_positive = df[df['Dx:HPV'] == 1]
        with_cancer = hpv_positive['Dx:Cancer'].sum()
        without_cancer = len(hpv_positive) - with_cancer
        data = pd.DataFrame({
            "Status": ['HPV & Cancer', 'HPV & No Cancer'],
            "Percentage": [with_cancer / len(hpv_positive) * 100,
                           without_cancer / len(hpv_positive) * 100]
        })
        fig_cancer = px.bar(data, x="Status", y="Percentage", text="Percentage",
                            color="Status", color_discrete_map={"HPV & Cancer": "crimson", "HPV & No Cancer": "steelblue"})
        fig_cancer.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_cancer.update_layout(height=200, margin=dict(t=20, b=10), showlegend=False)
        st.plotly_chart(fig_cancer, use_container_width=True)
