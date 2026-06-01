import streamlit as st
import datetime
from nsepython import index_pe_pb_div, index_total_returns
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NIFTY 50 VALUATION", page_icon="🌐", layout="wide")
st.title("Valuation matrix for NIFTY 50")

col1, col2, col3 = st.columns(3)

with col2:
    start_date = st.date_input(
        "Start date",
        min_value=datetime.date(2001, 1, 1),
        max_value=datetime.date.today(),
        value=datetime.date(2001, 1, 1),
    ).strftime("%Y-%m-%d")

with col3:
    end_date = st.date_input("End date", datetime.date.today()).strftime("%Y-%m-%d")

with col1:
    option = st.selectbox("Select index", ["NIFTY 50"])


@st.cache_data
def nifty_val(symbol, start_date, end_date):
    return index_pe_pb_div(symbol, start_date, end_date)


@st.cache_data
def returns(symbol, start_date, end_date):
    return index_total_returns(symbol, start_date, end_date)


# ---------------- DATA ----------------
data = nifty_val(option, start_date, end_date)

if data is None or data.empty:
    st.error("No valuation data returned from NSE API")
    st.stop()

data.DATE = pd.to_datetime(data.DATE, format='mixed')
data.set_index("DATE", inplace=True)
data.sort_index(inplace=True)

filter_data = data[["pe", "pb"]].astype(float)

mean_pe, std_pe = filter_data["pe"].mean(), filter_data["pe"].std()
mean_pb, std_pb = filter_data["pb"].mean(), filter_data["pb"].std()

# ---------------- PE CHART ----------------
fig_pe = px.line(
    data,
    x=data.index,
    y="pe",
    title="NIFTY PE Ratio",
)

for lvl in [0, 1, 2]:
    fig_pe.add_hline(y=mean_pe + lvl * std_pe, line_dash="dash", line_width=0.7)
    fig_pe.add_hline(y=mean_pe - lvl * std_pe, line_dash="dash", line_width=0.7)

st.plotly_chart(fig_pe, use_container_width=True)

# ---------------- PB CHART ----------------
fig_pb = px.line(
    data,
    x=data.index,
    y="pb",
    title="NIFTY PB Ratio",
)

for lvl in [0, 1, 2]:
    fig_pb.add_hline(y=mean_pb + lvl * std_pb, line_dash="dash", line_width=0.7)
    fig_pb.add_hline(y=mean_pb - lvl * std_pb, line_dash="dash", line_width=0.7)

st.plotly_chart(fig_pb, use_container_width=True)

# ---------------- RETURNS ----------------
yearly_returns = returns(option, start_date, end_date)

if yearly_returns is None or yearly_returns.empty:
    st.error("No return data returned from NSE API")
    st.stop()

yearly_returns["Date"] = pd.to_datetime(yearly_returns["Date"], format="mixed")
yearly_returns.set_index("Date", inplace=True)

yearly_ret = yearly_returns["TotalReturnsIndex"].astype(float).resample("Y").last()
nifty_returns = yearly_ret.pct_change().dropna() * 100

fig_ret = px.bar(
    x=nifty_returns.index.year,
    y=nifty_returns.values,
    title="NIFTY Yearly Returns (%)",
    color=nifty_returns.values,
    color_continuous_scale=["red", "lightgreen", "green"],
)

st.plotly_chart(fig_ret, use_container_width=True)
