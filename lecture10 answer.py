
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌍", layout="wide")

@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / "data" / "co2_emissions.csv"
    data = pd.read_csv(path)
    data["Date"] = pd.to_datetime(data["Year"].astype(str) + "-01-01")
    return data

df = load_data()

st.title("🌍 Global CO₂ Emissions Dashboard")
st.caption("Interactive dashboard using Streamlit and Plotly")

with st.sidebar:
    st.header("Dashboard Filters")

    regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
    region = st.selectbox("Region", regions)

    temp = df if region == "All" else df[df["Region"] == region]
    countries = sorted(temp["Country"].unique())
    selected = st.multiselect("Countries", countries, default=countries[:min(5,len(countries))])

    if not selected:
        st.warning("Please select at least one country.")
        st.stop()

    start = df["Date"].min().date()
    end = df["Date"].max().date()
    dates = st.date_input("Date Range",(start,end))
    if len(dates)!=2:
        st.warning("Please choose both start and end dates.")
        st.stop()

    start_date,end_date = map(pd.Timestamp,dates)

    metric = st.radio("Metric",["Total CO2 (Mt)","CO2 per capita"])
    highlight = st.checkbox("Show only top emitter highlighted")

metric_col = "CO2 per capita" if "CO2 per capita" in df.columns and metric=="CO2 per capita" else ("Annual CO₂ emissions" if "Annual CO₂ emissions" in df.columns else df.columns[3])

if metric=="Total CO2 (Mt)":
    if "Total CO2 (Mt)" in df.columns:
        metric_col="Total CO2 (Mt)"
    elif "CO2" in df.columns:
        metric_col="CO2"

filtered=temp[temp["Country"].isin(selected)]
filtered=filtered[(filtered["Date"]>=start_date)&(filtered["Date"]<=end_date)]

st.caption(f"{filtered['Country'].nunique()} countries | {region} | {start_date.date()} to {end_date.date()} | {metric}")

last_year=filtered["Year"].max()
last_df=filtered[filtered["Year"]==last_year]
first_year=filtered["Year"].min()
first_df=filtered[filtered["Year"]==first_year]

k1,k2,k3=st.columns(3)
total_last=last_df[metric_col].sum()
total_first=first_df[metric_col].sum()
change=((total_last-total_first)/total_first*100) if total_first else 0
top_country=last_df.sort_values(metric_col,ascending=False)["Country"].iloc[0]
k1.metric("Total Emissions",f"{total_last:,.2f}")
k2.metric("% Change",f"{change:.1f}%")
k3.metric("Top Emitter",top_country)

left,right=st.columns([2,1])

with left:
    st.subheader("CO₂ Trend Over Time")
    # Highlight colour type
    if highlight:
        top=top_country
        filtered["Highlight"]=filtered["Country"].apply(lambda x: top if x==top else "Other")
        fig=px.line(filtered,x="Year",y=metric_col,color="Highlight",line_group="Country",hover_name="Country",
                    color_discrete_map={top:"#d62728","Other":"#BBBBBB"})
    else:
        fig=px.line(filtered,x="Year",y=metric_col,color="Country")
    fig.update_layout(plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True)

with right:
    st.subheader(f"Ranking ({last_year})")
    # Sequential colour type
    rank=last_df.sort_values(metric_col,ascending=False)
    fig2=px.bar(rank,x=metric_col,y="Country",orientation="h",color=metric_col,color_continuous_scale="Blues")
    fig2.update_layout(plot_bgcolor="white",paper_bgcolor="white",yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(fig2,use_container_width=True)
