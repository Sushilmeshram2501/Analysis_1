import streamlit as st
import nsepython
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# ------------------ Page Config ------------------
st.set_page_config(page_title="Delivery % Analysis", layout="wide")
st.title("📊 NSE Delivery % vs Float Shares")

# ------------------ Functions ------------------

@st.cache_data(show_spinner=False)
def get_float_value(symbol):
    try:
        stock = yf.Ticker(symbol + ".NS")
        return stock.info.get("floatShares")
    except:
        return None


@st.cache_data(show_spinner=True)
def get_bhav_data(date_input):
    try:
        date_str = date_input.strftime("%d-%m-%Y")
        bhav = nsepython.get_bhavcopy(date_str)

        # Clean columns
        bhav.columns = bhav.columns.str.strip()

        # Filter EQ series
        bhav = bhav[bhav["SERIES"].str.strip() == "EQ"]

        # Date formatting
        bhav["DATE1"] = pd.to_datetime(bhav["DATE1"])
        bhav.set_index("DATE1", inplace=True)

        # Select required columns
        bhav = bhav[["SYMBOL", "OPEN_PRICE", "CLOSE_PRICE", "DELIV_QTY"]]

        # Convert numeric
        bhav["DELIV_QTY"] = pd.to_numeric(bhav["DELIV_QTY"], errors="coerce")

        # View logic
        bhav["VIEW"] = np.where(
            bhav["OPEN_PRICE"] < bhav["CLOSE_PRICE"],
            "BULLISH",
            "BEARISH"
        )

        # Float shares
        bhav["FLOAT_SHARES"] = bhav["SYMBOL"].apply(get_float_value)

        # Drop missing
        bhav.dropna(inplace=True)

        bhav["FLOAT_SHARES"] = pd.to_numeric(bhav["FLOAT_SHARES"], errors="coerce")

        # Delivery %
        bhav["DEL%"] = (bhav["DELIV_QTY"] / bhav["FLOAT_SHARES"] * 100).round(2)

        # Filter
        bhav = bhav[bhav["DEL%"] > 3]

        # Sort
        bhav = bhav.sort_values("DEL%", ascending=False)

        return bhav

    except Exception as e:
        return pd.DataFrame(), str(e)


# ------------------ UI ------------------

selected_date = st.date_input(
    "📅 Select Date",
    value=datetime.today()
)

if st.button("Fetch Data"):
    with st.spinner("Fetching data..."):
        result = get_bhav_data(selected_date)

    if isinstance(result, tuple):
        st.error(f"Error: {result[1]}")
    else:
        st.success(f"Data fetched for {selected_date.strftime('%d-%m-%Y')}")
        st.dataframe(result, use_container_width=True)

        # Optional download
        csv = result.to_csv().encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            csv,
            "delivery_analysis.csv",
            "text/csv"
        )
