import streamlit as st
import nsepython
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="% Delivery Data",
    layout="wide"
)

st.title("Delivery Analysis")

# ------------------ Load Symbols ------------------
@st.cache_data(show_spinner=True)
def load_eq_symbols():
    bhav = nsepython.get_bhavcopy("30-01-2026")
    bhav.columns = bhav.columns.str.strip()
    bhav = bhav[bhav["SERIES"] == " EQ"]
    return sorted(bhav["SYMBOL"].unique().tolist())

symbols = load_eq_symbols()

# ------------------ UI ------------------
col1, col2, col3 = st.columns([2, 3, 7])

with col2:
    symbol = st.selectbox("Search Symbol", symbols)

# ------------------ Float Shares (Optimized) ------------------
@st.cache_data(show_spinner=False)
def get_float_map(symbols):
    data = {}
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym + ".NS")
            info = ticker.info
            data[sym] = info.get("floatShares", None)
        except:
            data[sym] = None
    return data

# ------------------ Get 1 Month Bhavcopy ------------------
@st.cache_data(show_spinner=True)
def get_1_month_eq_bhavcopy(end_date=None):
    if end_date is None:
        end_date = datetime.today()

    start_date = end_date - timedelta(days=40)
    all_data = []

    current_date = start_date
    while current_date <= end_date:
        try:
            bhav = nsepython.get_bhavcopy(
                current_date.strftime("%d-%m-%Y")
            )

            if bhav is not None and not bhav.empty:
                bhav.columns = bhav.columns.str.strip()

                # Filter EQ
                bhav = bhav[bhav["SERIES"] == " EQ"]

                # Required columns
                bhav = bhav[
                    ["SYMBOL", "OPEN_PRICE", "CLOSE_PRICE", "DELIV_QTY", "DELIV_PER"]
                ]

                bhav["BHAV_DATE"] = current_date

                all_data.append(bhav)

        except:
            pass

        current_date += timedelta(days=1)

    if not all_data:
        return pd.DataFrame()

    df = pd.concat(all_data, ignore_index=True)

    # ------------------ Cleaning ------------------
    df["OPEN_PRICE"] = pd.to_numeric(df["OPEN_PRICE"], errors="coerce")
    df["CLOSE_PRICE"] = pd.to_numeric(df["CLOSE_PRICE"], errors="coerce")
    df["DELIV_QTY"] = pd.to_numeric(df["DELIV_QTY"], errors="coerce")
    df["DELIV_PER"] = pd.to_numeric(df["DELIV_PER"], errors="coerce")

    # Bullish / Bearish
    df["day"] = np.where(
        df["OPEN_PRICE"] < df["CLOSE_PRICE"], "Bullish", "Bearish"
    )

    return df

# ------------------ Symbol Data ------------------
def get_symbol_delivery_per(symbol):
    df = get_1_month_eq_bhavcopy()

    symbol_df = df[df["SYMBOL"] == symbol].copy()

    if symbol_df.empty:
        return symbol_df

    # Float shares (optimized)
    float_map = get_float_map([symbol])
    symbol_df["float_share"] = symbol_df["SYMBOL"].map(float_map)

    # Custom Delivery % (optional)
    symbol_df["Del%_calc"] = (
        symbol_df["DELIV_QTY"] / symbol_df["float_share"]
    ) * 100

    # ------------------ Apply Filters ------------------
    symbol_df = symbol_df[
        (symbol_df["DELIV_PER"] > 3) &
        (symbol_df["day"] == "Bullish")
    ]

    symbol_df.sort_values("BHAV_DATE", inplace=True)

    return symbol_df

# ------------------ Plot ------------------
if symbol:
    data = get_symbol_delivery_per(symbol)

    if data.empty:
        st.warning("No data available after applying filters.")
    else:
        fig = px.line(
            data,
            x="BHAV_DATE",
            y="DELIV_PER",  # Change to "Del%_calc" if needed
            title=f"{symbol} – Delivery % (Bullish & >3%)",
            markers=True
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Delivery %",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View Data"):
            st.dataframe(data, use_container_width=True)
```
