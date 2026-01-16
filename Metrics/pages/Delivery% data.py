import streamlit as st
import nsepython
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="% Delivery Data",
    layout="wide"
)

st.title("NSE Delivery % Analysis")

# ------------------ Load Symbols ------------------
@st.cache_data(show_spinner=True)
def load_eq_symbols():
    bhav = nsepython.get_bhavcopy("31-12-2025")
    bhav = bhav[bhav[" SERIES"] == " EQ"]
    bhav.columns = bhav.columns.str.strip()
    return sorted(bhav["SYMBOL"].unique().tolist())

symbols = load_eq_symbols()

# ------------------ Reduced Width Selectbox ------------------
col1, col2, col3 = st.columns([2, 3, 7])

with col2:
    symbol = st.selectbox(
        "🔍 Search Symbol",
        symbols
    )

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
                bhav = bhav[bhav[" SERIES"] == " EQ"]
                bhav.columns = bhav.columns.str.strip()
                bhav["BHAV_DATE"] = current_date
                all_data.append(bhav)

        except:
            pass

        current_date += timedelta(days=1)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)

# ------------------ Symbol Delivery % ------------------
def get_symbol_delivery_per(symbol):
    df = get_1_month_eq_bhavcopy()

    symbol_df = df[df["SYMBOL"] == symbol].copy()
    symbol_df = symbol_df[["BHAV_DATE", "SYMBOL", "DELIV_PER"]]

    symbol_df["DELIV_PER"] = pd.to_numeric(
        symbol_df["DELIV_PER"], errors="coerce"
    )

    symbol_df.sort_values("BHAV_DATE", inplace=True)

    return symbol_df

# ------------------ Plot ------------------
if symbol:
    data = get_symbol_delivery_per(symbol)

    if data.empty:
        st.warning("No data available for selected symbol.")
    else:
        fig = px.line(
            data,
            x="BHAV_DATE",
            y="DELIV_PER",
            title=f"{symbol} – Delivery % (Last 1 Month)",
            markers=True
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Delivery %",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander(" View Data"):
            st.dataframe(data, use_container_width=True)

