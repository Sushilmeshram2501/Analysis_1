import streamlit as st
import datetime
from nsepython import index_pe_pb_div,index_total_returns
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(page_title="NIFTY 50 VALUATION", page_icon="🌐",layout='wide')

st.title("Valuation matrix for nifty 50")
col1,col2, col3=st.columns(3)

with col2:
    start_date=st.date_input('start date',min_value=datetime.date(2000,1,1),max_value=datetime.date.today(),value=datetime.date(2001,1,1))

    start_date=start_date.strftime("%Y-%m-%d")
    # print(start_date)
with col3:
    end_date=st.date_input('end date',datetime.date.today())
    end_date=end_date.strftime("%Y-%m-%d")
    # print(end_date)

with col1:
    # st.title('select symbol')
    option=st.selectbox('select index',["NIFTY 50"])
    # print(option)


def nifty_val(symbol,start_date,end_date):
    df= index_pe_pb_div(symbol,start_date,end_date)
    return df


data=nifty_val(option,start_date,end_date)
data['DATE']=pd.to_datetime(data['DATE'])
data.set_index('DATE',inplace=True)
data.sort_values(by='DATE',ascending=True,inplace=True)
# print(data)
filter_data=data[['pe','pb']].astype(float)
mean_pe=filter_data['pe'].mean()
std_pe=filter_data['pe'].std()

def returns(symbol,start_date,end_date):
    ret=index_total_returns(symbol,start_date,end_date)
    return ret

yearly_returns=returns(option,start_date,end_date)
yearly_returns['Date']=pd.to_datetime(yearly_returns['Date'],format='mixed')
yearly_returns=yearly_returns.set_index('Date')
yearly_returns.sort_values(by='Date',ascending=True,inplace=True)

yearly_ret=yearly_returns['TotalReturnsIndex'].resample('YE').last().astype(float)
nifty_returns=yearly_ret.pct_change()*100
nifty_returns.dropna(inplace=True)



fig_pe = px.line(data, x=data.index, y=data['pe'], title='Nifty Price to Earning',labels={'date':'DATE','pe':'PE Ratio'})
fig_pe.add_hline(y=mean_pe, line_dash="dash", line_color="red")
fig_pe.add_hline(y=mean_pe+std_pe,line_dash='dash',line_width=0.5)
fig_pe.add_hline(y=mean_pe-std_pe,line_dash='dash',line_width=0.5)
fig_pe.add_hline(y=mean_pe+2*std_pe,line_dash='dash',line_width=0.5)
fig_pe.add_hline(y=mean_pe-2*std_pe,line_dash='dash',line_width=0.5)
fig_pe.update_xaxes(showgrid=False)
fig_pe.update_yaxes(showgrid=False)
st.plotly_chart(fig_pe, use_container_width=True)

mean_pb=filter_data['pb'].mean()
std_pb=filter_data['pb'].std()


fig_pb = px.line(data, x=data.index, y=data['pb'], title='Nifty Price to Book Value',labels={'date':'DATE','pb':'PB Ratio'})
fig_pb.add_hline(y=mean_pb, line_dash="dash", line_color="red")
fig_pb.add_hline(y=mean_pb+std_pb,line_dash='dash',line_width=0.5)
fig_pb.add_hline(y=mean_pb-std_pb,line_dash='dash',line_width=0.5)
fig_pb.add_hline(y=mean_pb+2*std_pb,line_dash='dash',line_width=0.5)
fig_pb.add_hline(y=mean_pb-2*std_pb,line_dash='dash',line_width=0.5)
fig_pb.update_xaxes(showgrid=False)
fig_pb.update_yaxes(showgrid=False)
st.plotly_chart(fig_pb, use_container_width=True)

custom_scale = [
        [-0.0, "red"],         # lowest returns
        [0.5, "lightgreen"],  # around 0%
        [1.0, "green"]        # highest returns
    ]

fig_ret=px.bar(nifty_returns,x=nifty_returns.index,y=nifty_returns,labels={'TotalReturnsIndex':'Yearly Returns','Date':'Year'},title='Nifty Yearly Returns',
               color=nifty_returns,color_continuous_scale=custom_scale)
st.plotly_chart(fig_ret, use_container_width=True)







