import streamlit as st
import pandas as pd
import plotly.express as px

# Set wide layout
st.set_page_config(page_title="Cervical Cancer: Global Burden and Trends", layout="wide", initial_sidebar_state="collapsed")
st.title("Cervical Cancer: Global Burden and Trends Dashboard")

# -------------------- SECTION 1: Summary Indicators --------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    col_inc, col_mort = st.columns(2)
    with col_inc:
        st.markdown("""
        <h4 style='color:#004B9B;'>Incidence</h4>
        <p style='color:#004B9B; font-size:18px;'>
        <b>Rank:</b> <span style='font-size:24px;'>8</span> &nbsp;&nbsp;&nbsp;&nbsp;
        <b>Cases:</b> <span style='font-size:24px;'>662,301</span>
        </p>
        """, unsafe_allow_html=True)

    with col_mort:
        st.markdown("""
        <h4 style='color:#D7191C;'>Mortality</h4>
        <p style='color:#D7191C; font-size:18px;'>
        <b>Rank:</b> <span style='font-size:24px;'>9</span> &nbsp;&nbsp;&nbsp;&nbsp;
        <b>Deaths:</b> <span style='font-size:24px;'>348,874</span>
        </p>
        """, unsafe_allow_html=True)

# -------------------- TABS FOR VISUALS --------------------
tab1, tab2 = st.tabs(["🌍 Global Overview", "📊 Risk & Diagnosis"])

# -------------------- TAB 1: GLOBAL OVERVIEW --------------------
with tab1:
    # Choropleth map
    asr_path = "dataset-asr-inc-both-sexes-in-2022-cervix-uteri.csv"
    df_asr = pd.read_csv(asr_path)
    df_asr.columns = df_asr.columns.str.strip()

    fig_map = px.choropleth(
        df_asr,
        locations="Population",
        locationmode="country names",
        color="ASR (World) per 100 000",
        color_continuous_scale="YlOrRd",
        range_color=(0, df_asr["ASR (World) per 100 000"].max()),
        labels={"ASR (World) per 100 000": "ASR per 100k"},
        title="Age-Standardized Incidence Rate (ASR) per 100,000 - Cervix Uteri (2022)",
        projection="natural earth"
    )
    fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True), height=350, margin=dict(t=30, b=20))
    st.plotly_chart(fig_map, use_container_width=True)

    # Line chart: HPV immunization
    df_line = pd.read_csv("data.csv")
    df_line.columns = df_line.columns.str.strip()
    df_clean = df_line[['ParentLocationCode', 'Period', 'FactValueNumeric']].dropna()
    df_grouped = df_clean.groupby(['ParentLocationCode', 'Period'], as_index=False)['FactValueNumeric'].mean()

    fig_line = px.line(
        df_grouped,
        x='Period',
        y='FactValueNumeric',
        color='ParentLocationCode',
        markers=True,
        title="HPV Immunization Coverage Among 9–14 Year Old Girls by WHO Region (%)",
        labels={'Period': 'Year', 'FactValueNumeric': 'Coverage (%)', 'ParentLocationCode': 'WHO Region'}
    )
    fig_line.update_layout(yaxis_range=[0, 100], height=300, margin=dict(t=30, b=20))
    st.plotly_chart(fig_line, use_container_width=True)

# -------------------- TAB 2: RISK & DIAGNOSIS --------------------
with tab2:
    # Pie chart: cases by continent
    pie_path = "dataset-absolute-numbers-inc-both-sexes-in-2022-cervix-uteri.csv"
    df_pie = pd.read_csv(pie_path)
    df_pie.columns = df_pie.columns.str.strip().str.lower()

    if "label" in df_pie.columns and "total" in df_pie.columns:
        fig_pie = px.pie(
            df_pie,
            names="label",
            values="total",
            title="Distribution of Cervical Cancer Cases by Continent (2022)",
            hole=0.4
        )
        fig_pie.update_traces(textinfo="label+percent", textfont_size=14)
        fig_pie.update_layout(showlegend=False, height=300, margin=dict(t=30, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Biopsy rate by age group
    biopsy_path = "cleaned_cervical_cancer_dataset.csv"
    biopsy_df = pd.read_csv(biopsy_path)
    biopsy_df.columns = biopsy_df.columns.str.strip().str.lower()
    bins = [10, 20, 30, 40, 50, 60]
    labels_age = ['10-19', '20-29', '30-39', '40-49', '50-59']
    biopsy_df['age group'] = pd.cut(biopsy_df['age'], bins=bins, labels=labels_age, right=False)
    age_group_trend = biopsy_df.groupby('age group')['biopsy'].mean().reset_index().dropna()

    with st.expander("Biopsy-Positive Rate by Age Group", expanded=False):
        fig_biopsy = px.bar(
            age_group_trend,
            x='biopsy',
            y='age group',
            orientation='h',
            color_discrete_sequence=['steelblue'],
            title="Biopsy-Positive Rate by Age Group"
        )
        fig_biopsy.update_layout(
            xaxis_title='Percentage with Cancer',
            yaxis_title='Age Group',
            xaxis_range=[0, 1],
            xaxis_tickformat=".0%",
            plot_bgcolor='white',
            height=300,
            margin=dict(t=30, b=20)
        )
        st.plotly_chart(fig_biopsy, use_container_width=True)

    # HPV & Cancer correlation
    df = pd.read_csv(biopsy_path)
    df.columns = df.columns.str.strip()
    hpv_positive = df[df['Dx:HPV'] == 1]
    with_cancer = hpv_positive['Dx:Cancer'].sum()
    without_cancer = len(hpv_positive) - with_cancer

    data = pd.DataFrame({
        "Cancer Status": ['HPV & Cancer', 'HPV & No Cancer'],
        "Percentage": [with_cancer / len(hpv_positive) * 100, without_cancer / len(hpv_positive) * 100]
    })

    with st.expander("Cancer Diagnosis Among HPV-Positive Patients", expanded=False):
        fig = px.bar(
            data,
            x="Cancer Status",
            y="Percentage",
            color="Cancer Status",
            color_discrete_map={"HPV & Cancer": "crimson", "HPV & No Cancer": "steelblue"},
            text="Percentage",
            title="Cancer Diagnosis Among HPV-Positive Patients"
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(
            yaxis_title="Percentage",
            xaxis_title=None,
            showlegend=False,
            height=300,
            margin=dict(t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
