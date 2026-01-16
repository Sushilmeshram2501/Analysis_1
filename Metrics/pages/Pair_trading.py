import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Nifty BankNifty Pair Trading",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("Pair Trading")

st.markdown("""
pair trading opportunities:NIFTY-BANKNIFTY ratio,Z-Score, and Rolling Correlation.
""")

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Settings")

period = st.sidebar.selectbox(
    "Select Data Period",
    ["1y", "2y", "3y", "5y"],
    index=1
)

window = st.sidebar.slider(
    "Rolling Window (days)",
    min_value=20,
    max_value=120,
    value=63
)

# -----------------------------
# Data Download
# -----------------------------
@st.cache_data
def load_data(period):
    nifty = yf.download("^NSEI", period=period, auto_adjust=True, progress=False,multi_level_index=False)
    banknifty = yf.download("^NSEBANK", period=period, auto_adjust=True, progress=False,multi_level_index=False)

    df = pd.concat(
        [
            nifty["Close"].rename("NIFTY"),
            banknifty["Close"].rename("BANKNIFTY"),
        ],
        axis=1,
    )
    df.dropna(inplace=True)
    return df

combined_df = load_data(period)

# -----------------------------
# Calculations
# -----------------------------
combined_df["Ratio"] = (combined_df["NIFTY"] / combined_df["BANKNIFTY"]).round(3)
combined_df["Rolling_Mean"] = combined_df["Ratio"].rolling(window).mean()
combined_df["Rolling_Std"] = combined_df["Ratio"].rolling(window).std()
combined_df["Z_Score"] = (
    (combined_df["Ratio"] - combined_df["Rolling_Mean"])
    / combined_df["Rolling_Std"]
)

combined_df["Rolling_Corr"] = combined_df["NIFTY"].rolling(window).corr(
    combined_df["BANKNIFTY"]
)

# -----------------------------
# Z-Score Chart
# -----------------------------
st.subheader(" Z-Score of NIFTY / BANKNIFTY Ratio")

fig_z = go.Figure()

fig_z.add_trace(
    go.Scatter(
        x=combined_df.index,
        y=combined_df["Z_Score"],
        mode="lines",
        name="Z-Score",
    )
)

fig_z.add_hline(y=2, line_dash="dash", annotation_text="+2")
fig_z.add_hline(y=-2, line_dash="dash", annotation_text="-2")
fig_z.add_hline(y=0, line_dash="dot")

fig_z.update_layout(
    height=400,
    xaxis_title="Date",
    yaxis_title="Z-Score",
    template="plotly_white",
)

st.plotly_chart(fig_z, use_container_width=True)

# -----------------------------
# Rolling Correlation Chart
# -----------------------------
st.subheader("Rolling Correlation (NIFTY vs BANKNIFTY)")

fig_corr = go.Figure()

fig_corr.add_trace(
    go.Scatter(
        x=combined_df.index,
        y=combined_df["Rolling_Corr"],
        mode="lines",
        name="Rolling Correlation",
    )
)

fig_corr.add_hline(y=0, line_dash="dot")

fig_corr.update_layout(
    height=400,
    xaxis_title="Date",
    yaxis_title="Correlation",
    template="plotly_white",
)

st.plotly_chart(fig_corr, use_container_width=True)

# -----------------------------
# Data Table
# -----------------------------
with st.expander("📄 View Data"):
    st.dataframe(combined_df.tail(200))
