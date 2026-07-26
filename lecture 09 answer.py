

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Global Well-Being Analytics Dashboard", page_icon="🌍", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / 'data'
df = pd.read_csv(DATA_DIR / 'happiness_data_2023.csv')

df.columns = ['Nation', 'Continent', 'Happiness_Index', 'Economic_Index', 'Community_Support',
              'Healthy_Life', 'Personal_Freedom', 'Kindness', 'Trust']

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    regions = ['All'] + sorted(df['Continent'].unique().tolist())
    selected_region = st.selectbox("Continent", regions)
    top_n = st.slider("Show top N countries", 5, 30, 15)


# ── Filtered data ─────────────────────────────────────────────────────────────
filtered = df if selected_region == 'All' else df[df['Continent'] == selected_region]
top = filtered.nlargest(top_n, 'Happiness_Index').sort_values('Happiness_Index')

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🌍 Global Well-Being Analytics Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
k1.metric("Countries", len(filtered))
k2.metric("Avg Happiness Happiness_Index", f"{filtered['Happiness_Index'].mean():.2f}",
          f"{filtered['Happiness_Index'].mean() - df['Happiness_Index'].mean():+.2f} vs global")
k3.metric("Happiest in selection",
          filtered.nlargest(1, 'Happiness_Index')['Nation'].values[0],
          f"Happiness_Index: {filtered['Happiness_Index'].max():.2f}")

st.divider()

# ── Row 1: Rankings + Scatter ─────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Happiness Rankings")
    # BBD COLOUR TYPE: sequential — ordered bars, one direction (light→dark)
    fig1 = px.bar(
        top, x='Happiness_Index', y='Nation', orientation='h',
        color='Happiness_Index',
        color_continuous_scale='Blues',
        range_color=[4.5, 8.5],
        labels={'Happiness_Index': 'Happiness Happiness_Index (0–10)', 'Nation': ''},
    )
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(range=[0, 8.5], gridcolor='#EEEEEE'),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False,
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=5, b=10),
    )
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Happiness_Index vs Economic_Index")
    # BBD COLOUR TYPE: highlight — single colour, focus on the pattern
    fig2 = px.scatter(
        filtered, x='Economic_Index', y='Happiness_Index', hover_name='Nation',
        color_discrete_sequence=['#2E75B6'],
        labels={'Economic_Index': 'Log Economic_Index per Capita', 'Happiness_Index': 'Happiness Happiness_Index'},
    )
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(gridcolor='#EEEEEE'),
        yaxis=dict(gridcolor='#EEEEEE'),
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=5, b=10),
    )
    fig2.update_traces(marker=dict(size=9, opacity=0.8))
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Factor breakdown ───────────────────────────────────────────────────
st.subheader("Factor breakdown for top countries")

factors = ['Economic_Index', 'Community_Support', 'Healthy_Life', 'Personal_Freedom']
top10 = filtered.nlargest(10, 'Happiness_Index')

# BBD COLOUR TYPE: categorical — each factor is an unordered distinct category
fig3 = px.bar(
    top10.melt(id_vars='Nation', value_vars=factors),
    x='value', y='Nation', color='variable', orientation='h',
    barmode='stack',
    # BBD CVD: no red-green; blue-green-yellow-grey palette
    color_discrete_sequence=['#2E75B6', '#70AD47', '#FFC000', '#AAAAAA'],
    labels={'value': 'Contribution', 'variable': 'Factor', 'Nation': ''},
)
fig3.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    xaxis=dict(gridcolor='#EEEEEE'),
    legend=dict(orientation='h', y=1.2),
    margin=dict(l=10, r=10, t=40, b=10),
)
fig3.update_traces(marker_line_width=0)
st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.caption("Built with Streamlit + Plotly")