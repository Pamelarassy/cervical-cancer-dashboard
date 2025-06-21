import streamlit as st
import pandas as pd
import plotly.express as px

# Layout config
st.set_page_config(page_title="Cervical Cancer Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<h4 style='text-align:center;'>Cervical Cancer: Global Snapshot (2022)</h4>", unsafe_allow_html=True)

# Split the page into left and right columns
col_left, col_right = st.columns([1.5, 1])

# ---------------- LEFT COLUMN ----------------
with col_left:
    # Incidence + Mortality summary
    st.markdown(
        """
        <div style='font-size:14px;'>
            <b style='color:#004B9B;'>Incidence Rank:</b> 8 &nbsp;&nbsp;&nbsp;&nbsp;
            <b>Cases:</b> 662,301<br>
            <b style='color:#D7191C;'>Mortality Rank:</b> 9 &nbsp;&nbsp;&nbsp;&nbsp;
            <b>Deaths:</b> 348,874
        </div>
        """,
        unsafe_allow_html=True
    )

    # Choropleth Map
    df_map = pd.read_csv("dataset-asr-inc-both-sexes-in-2022-cervix-uteri.csv")
    df_map.columns = df_map.columns.str.strip()
    fig_map = px.choropleth(
        df_map,
        locations="Population",
        locationmode="country names",
        color="ASR (World) per 100 000",
        color_continuous_scale="YlOrRd"
    )
    fig_map.update_layout(height=240, margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig_map, use_container_width=True)

    # HPV Vaccine Line Chart
    df_line = pd.read_csv("data.csv")
    df_line.columns = df_line.columns.str.strip()
    df_line = df_line[['ParentLocationCode', 'Period', 'FactValueNumeric']].dropna()
    df_group = df_line.groupby(['ParentLocationCode', 'Period'], as_index=False)['FactValueNumeric'].mean()
    fig_line = px.line(df_group, x='Period', y='FactValueNumeric', color='ParentLocationCode', markers=True)
    fig_line.update_layout(height=240, yaxis_range=[0, 100], margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_line, use_container_width=True)

# ---------------- RIGHT COLUMN ----------------
with col_right:
    # Pie Chart
    df_pie = pd.read_csv("dataset-absolute-numbers-inc-both-sexes-in-2022-cervix-uteri.csv")
    df_pie.columns = df_pie.columns.str.strip().str.lower()
    fig_pie = px.pie(df_pie, names="label", values="total", hole=0.4)
    fig_pie.update_layout(height=200, margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Biopsy Chart
    df = pd.read_csv("cleaned_cervical_cancer_dataset.csv")
    df.columns = df.columns.str.strip().str.lower()
    bins = [10, 20, 30, 40, 50, 60]
    labels_age = ['10-19', '20-29', '30-39', '40-49', '50-59']
    df['age group'] = pd.cut(df['age'], bins=bins, labels=labels_age, right=False)
    trend = df.groupby('age group')['biopsy'].mean().reset_index().dropna()
    fig_biopsy = px.bar(trend, x='biopsy', y='age group', orientation='h', color_discrete_sequence=['#1f77b4'])
    fig_biopsy.update_layout(height=200, xaxis_range=[0, 1], xaxis_tickformat=".0%", margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_biopsy, use_container_width=True)

    # HPV & Cancer Status
    df.columns = df.columns.str.strip()
    hpv_positive = df[df['Dx:HPV'] == 1]
    with_cancer = hpv_positive['Dx:Cancer'].sum()
    without_cancer = len(hpv_positive) - with_cancer
    df_status = pd.DataFrame({
        "Status": ['HPV & Cancer', 'HPV & No Cancer'],
        "Percentage": [with_cancer / len(hpv_positive) * 100,
                       without_cancer / len(hpv_positive) * 100]
    })
    fig_status = px.bar(df_status, x="Status", y="Percentage", text="Percentage",
                        color="Status", color_discrete_map={"HPV & Cancer": "crimson", "HPV & No Cancer": "steelblue"})
    fig_status.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_status.update_layout(height=200, margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_status, use_container_width=True)
