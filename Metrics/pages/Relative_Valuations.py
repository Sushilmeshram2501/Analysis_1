import streamlit as st
import datetime
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(page_title="Relative Valuation",layout='wide')
col1,col2,col3=st.columns(3)

sector_list={'BANKNIFTY':'^NSEBANK','AUTO':'^CNXAUTO','IT':'^CNXIT','FMCG':'^CNXFMCG','METAL':'^CNXMETAL','PHARMA':'^CNXPHARMA','ENERGY':'^CNXENERGY','MEDIA':'^CNXMEDIA',
             'COMMODITY':'^CNXCMDT','MNC':'^CNXMNC','PUBLIC_SECTOR':'NIFTY_CPSE.NS','PSU_BANK':'^CNXPSUBANK','FINIFTY':'NIFTY_FIN_SERVICE.NS','CONSUMPTION':'^CNXCONSUM',
             'SMALLCAP':'NIFTYSMLCAP250.NS','MIDCAP':'NIFTYMIDCAP150.NS'}

periods=['3y','5y']

with col1:
    nifty50=st.selectbox('selected','NIFTY_50')

with col2:
    symbol_sector=st.selectbox('select_index',sector_list.values())
    # 
with col3:
    per=st.selectbox('select_period',periods)


def load_data(symbol,period):
    df=yf.download(symbol,period=period,multi_level_index=False,auto_adjust=True,progress=False)
    df.dropna(inplace=True)
    return df


nifty_df=load_data('^NSEI',per)
# print(nifty_df)
sector_df=load_data(symbol_sector,per)
# print(sector_df)

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=nifty_df.index,
    y=nifty_df['Close'],
    name='NIFTY 50',
    yaxis='y1',
    line=dict(width=2),
    line_color='Blue'
))

fig1.add_trace(go.Scatter(
    x=sector_df.index,
    y=sector_df['Close'],
    name=symbol_sector,
    yaxis='y2',
    line=dict(width=2),
    line_color='red'
))

fig1.update_layout(
    title="Closing Price Comparison",
    xaxis_title="Date",
    yaxis=dict(title="NIFTY 50"),
    yaxis2=dict(
        title=symbol_sector,
        overlaying='y',
        side='right'
    ),
    height=550
)

st.plotly_chart(fig1, use_container_width=True)

