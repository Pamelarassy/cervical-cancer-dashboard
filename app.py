import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set layout
st.set_page_config(page_title="Cervical Cancer: Global Burden and Trends", layout="wide")

# Custom title with smaller font
st.markdown("<h1 style='font-size:26px;'>Cervical Cancer: Global Burden and Trends Dashboard</h1>", unsafe_allow_html=True)

# Define chart heights after reduction
CHART_HEIGHT_SMALL = 225           # ~10% reduction
CHART_HEIGHT_LARGE = 270           # ~10% reduction
CHART_HEIGHT_EXTRA_SMALL = 213     # 15% reduction (for HPV + Cancer)

# -------------------- SECTION 1: Summary Indicators --------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    col_inc, col_mort = st.columns(2)
    with col_inc:
        st.markdown("""
        <h2 style='color:#004B9B;'>Incidence</h2>
        <p style='color:#004B9B; font-size:20px;'>
        <b>Rank:</b> <span style='font-size:28px; font-weight:bold;'>8</span> &nbsp;&nbsp;&nbsp;&nbsp;
        <b>Cases:</b> <span style='font-size:28px; font-weight:bold;'>662,301</span>
        </p>
        """, unsafe_allow_html=True)

    with col_mort:
        st.markdown("""
        <h2 style='color:#D7191C;'>Mortality</h2>
        <p style='color:#D7191C; font-size:20px;'>
        <b>Rank:</b> <span style='font-size:28px; font-weight:bold;'>9</span> &nbsp;&nbsp;&nbsp;&nbsp;
        <b>Deaths:</b> <span style='font-size:28px; font-weight:bold;'>348,874</span>
        </p>
        """, unsafe_allow_html=True)

# -------------------- RIGHT COLUMN CHARTS --------------------
with right_col:
    pie_path = "dataset-absolute-numbers-inc-both-sexes-in-2022-cervix-uteri.csv"
    df_pie = pd.read_csv(pie_path)
    df_pie.columns = df_pie.columns.str.strip().str.lower()

    if "label" in df_pie.columns and "total" in df_pie.columns:
        fig_pie = px.pie(
            df_pie,
            names="label",
            values="total",
            hole=0.4
        )
        fig_pie.update_traces(textinfo="label+percent", textfont_size=12)
        fig_pie.update_layout(
            title_text="Cervical Cancer by Continent (2022)",
            showlegend=False,
            height=CHART_HEIGHT_SMALL,
            margin=dict(t=40, b=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    biopsy_path = "cleaned_cervical_cancer_dataset.csv"
    biopsy_df = pd.read_csv(biopsy_path)
    biopsy_df.columns = biopsy_df.columns.str.strip().str.lower()

    if "biopsy" in biopsy_df.columns:
        biopsy_df["biopsy"] = pd.to_numeric(biopsy_df["biopsy"], errors="coerce")
        bins = [10, 20, 30, 40, 50, 60]
        labels_age = ['10-19', '20-29', '30-39', '40-49', '50-59']
        biopsy_df['age group'] = pd.cut(biopsy_df['age'], bins=bins, labels=labels_age, right=False)
        age_group_trend = biopsy_df.groupby('age group')['biopsy'].mean().reset_index().dropna()

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
            height=CHART_HEIGHT_SMALL,
            plot_bgcolor='white',
            margin=dict(t=40, b=10)
        )
        st.plotly_chart(fig_biopsy, use_container_width=True)
    else:
        st.warning("Column 'biopsy' not found in the dataset.")

    df = pd.read_csv(biopsy_path)
    df.columns = df.columns.str.strip().str.lower()

    if "dx:hpv" in df.columns and "dx:cancer" in df.columns:
        hpv_positive = df[df['dx:hpv'] == 1]
        with_cancer = hpv_positive['dx:cancer'].sum()
        without_cancer = len(hpv_positive) - with_cancer

        data = pd.DataFrame({
            "Cancer Status": ['HPV & Cancer', 'HPV & No Cancer'],
            "Percentage": [with_cancer / len(hpv_positive) * 100,
                           without_cancer / len(hpv_positive) * 100]
        })

        fig = px.bar(
            data,
            x="Cancer Status",
            y="Percentage",
            color="Cancer Status",
            color_discrete_map={
                "HPV & Cancer": "crimson",
                "HPV & No Cancer": "steelblue"
            },
            text="Percentage",
            title="Cancer Diagnosis Among HPV-Positive Patients"
        )

        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(
            yaxis_title="Percentage",
            xaxis_title=None,
            showlegend=False,
            height=CHART_HEIGHT_EXTRA_SMALL,
            margin=dict(t=40, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Required columns 'dx:hpv' or 'dx:cancer' not found.")

# -------------------- LEFT COLUMN MAP + LINE CHART --------------------
with left_col:
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
        title="ASR per 100,000 - Cervix Uteri (2022)",
        projection="natural earth"
    )
    fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True), height=CHART_HEIGHT_LARGE, margin=dict(t=40, b=10))
    st.plotly_chart(fig_map, use_container_width=True)

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
        title="HPV Immunization Among Girls (9–14) by Region (%)",
        labels={
            'Period': 'Year',
            'FactValueNumeric': 'Coverage (%)',
            'ParentLocationCode': 'WHO Region'
        }
    )
    fig_line.update_layout(yaxis_range=[0, 100], height=CHART_HEIGHT_LARGE, margin=dict(t=40, b=10))
    st.plotly_chart(fig_line, use_container_width=True)
