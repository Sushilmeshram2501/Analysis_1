import streamlit as st
import yfinance as yf
import plotly.express as px
import datetime


st.set_page_config(page_title='Volatility_Matrix',layout='wide')
st.sidebar.title("Volatility to identify market condition for option sellers/option buyers",)

col1,col2,col3=st.columns(3)

with col1:
    symbol=st.selectbox('select',['^INDIAVIX'])

with col2:
    start_date=st.date_input('start date',min_value=datetime.date(2010,1,1),max_value=datetime.date(2014,1,1), value=datetime.date(2010,2,1))
with col3:
    end_date=st.date_input('end date',datetime.date.today())


def volatility(symbol,start_date, end_date):
    df=yf.download(symbol,start_date,end_date,multi_level_index=False,progress=False)
    return df

data=volatility(symbol,start_date,end_date)


data.drop('Volume',axis=1,inplace=True)
data['Ratio']=(data['High']-data['Low'])/data['Open']
data['Avg']=data['Ratio'].rolling(43).mean()
# print(data)

vol_mean=data['Avg'].mean()
vol_std=data['Avg'].std()


fig_vol = px.line(data, x=data.index, y=data['Avg'], title='Volatility Ratio',labels={'date':'Date','y':'Vol'})
fig_vol.add_hline(y=vol_mean, line_dash="dash", line_color="red",line_width=0.5)
fig_vol.add_hline(y=vol_mean+vol_std,line_dash='dash',line_width=0.5)
fig_vol.add_hline(y=vol_mean-vol_std,line_dash='dash',line_width=0.5)
fig_vol.add_hline(y=vol_mean+2*vol_std,line_dash='dash',line_width=0.5)
fig_vol.add_hline(y=vol_mean-2*vol_std,line_dash='dash',line_width=0.5)
fig_vol.update_xaxes(showgrid=False)
fig_vol.update_yaxes(showgrid=False)

fig_vol.add_hrect(
    y0=vol_mean+vol_std, y1=vol_mean+2*vol_std,
    fillcolor="red", opacity=0.1, line_width=0,
    annotation_text="Look For Option selling Setups",
    annotation_position="top right"
)

fig_vol.add_hrect(
    y0=vol_mean-vol_std, y1=vol_mean-2*vol_std,
    fillcolor='green',opacity=0.2,line_width=0,
    annotation_text="Look For Option Buying Setups",
    annotation_position="bottom right"

)
st.plotly_chart(fig_vol, use_container_width=True)