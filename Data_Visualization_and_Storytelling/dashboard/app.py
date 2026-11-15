from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from retail_metrics import summarize, annual_summary, monthly_sales

st.set_page_config(page_title='Retail sales and profitability',layout='wide')
st.title('Retail Sales & Profitability | 2024–2026')
st.caption('Sales trends, regional performance, product contribution and discount analysis. All monetary values are INR (₹).')
full=pd.read_csv(ROOT/'output/BITS_Retail_Cleaned_Integrated.csv')
fields=['Year','Region','Category','Customer_Segment']
options={f:sorted(full[f].unique().tolist()) for f in fields}
def reset():
    for f in fields:st.session_state[f]=options[f]
st.sidebar.header('Filter the analysis')
st.sidebar.button('Reset all filters',on_click=reset)
selections={f:st.sidebar.multiselect(f.replace('_',' '),options[f],default=options[f],key=f) for f in fields}
d=full.copy()
for f in fields:d=d[d[f].isin(selections[f])]
st.sidebar.caption('Full supplied academic years are used, including dates through December 2026. These are not verified real-time sales.')
if d.empty:
    st.warning('No transactions match these selections. Select values or reset all filters.')
    st.stop()
sales=d.NetSales.sum();profit=d.Profit.sum()
for col,label,value in zip(st.columns(4),['Net sales','Profit','Profit margin','Distinct orders'],
                           [f'₹{sales:,.0f}',f'₹{profit:,.0f}',f'{profit/sales*100:.2f}%',f'{d.Order_ID.nunique():,}']):col.metric(label,value)
st.caption(f'Active selection: {len(d):,} transactions. Profit subtracts product cost and shipping once per transaction. Orders count distinct Order_ID.')

def draw(fig):
    fig.update_layout(template='plotly_white',font_size=15,height=390,margin=dict(l=20,r=20,t=55,b=30),legend_title_text='')
    st.plotly_chart(fig,width='stretch')
def bars(table,field,title):
    long=table.melt(id_vars=field,value_vars=['NetSales','Profit'],var_name='Measure',value_name='INR')
    fig=px.bar(long,x=field,y='INR',color='Measure',barmode='group',title=title,
               color_discrete_map={'NetSales':'#245b8a','Profit':'#188477'})
    fig.update_yaxes(title='INR (₹)',rangemode='tozero')
    return fig

a,b,c,e=st.tabs(['Sales trends','Regions','Products','Discounts and actions'])
with a:
    st.header('Q1. Growth and monthly patterns')
    annual=annual_summary(d)
    draw(bars(annual.assign(Year=annual.Year.astype(str)),'Year','Annual net sales and profit'))
    monthly=monthly_sales(d);monthly['Year']=monthly.Year.astype(str)
    fig=px.line(monthly,x='Month',y='NetSales',color='Year',line_dash='Year',markers=True,title='Monthly net sales by supplied year')
    fig.update_xaxes(tickmode='array',tickvals=list(range(1,13)),ticktext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    fig.update_yaxes(title='Net sales (₹)',rangemode='tozero');draw(fig)
    st.dataframe(annual[['Year','NetSales','Profit','ProfitMarginPct','YoYSalesPct']],hide_index=True)
    st.caption('YoY is available only when consecutive years are selected. Peaks in one year do not establish seasonality.')
with b:
    st.header('Q2. Revenue and profitability differ')
    regions=summarize(d,'Region').sort_values('NetSales',ascending=False)
    long=regions.melt(id_vars='Region',value_vars=['NetSales','Profit'],var_name='Measure',value_name='INR')
    fig=px.bar(long,y='Region',x='INR',color='Measure',barmode='group',orientation='h',title='Regional net sales and profit',color_discrete_map={'NetSales':'#245b8a','Profit':'#188477'})
    fig.update_xaxes(title='INR (₹)',rangemode='tozero');draw(fig)
    st.dataframe(regions[['Region','NetSales','Profit','ProfitMarginPct','SalesSharePct']],hide_index=True)
    best=regions.iloc[0];margin=regions.loc[regions.ProfitMarginPct.idxmax()]
    st.write(f'Within the active filters, {best.Region} leads sales (₹{best.NetSales:,.0f}); {margin.Region} has the highest margin ({margin.ProfitMarginPct:.2f}%).')
with c:
    st.header('Q3. Product contribution and profitability')
    categories=summarize(d,'Category').sort_values('NetSales',ascending=False)
    draw(bars(categories,'Category','Category net sales and profit'))
    sub=summarize(d,['Category','Subcategory']).sort_values('Profit')
    sub['Product group']=sub.Category+' / '+sub.Subcategory
    sub['Result']=sub.Profit.map(lambda x:'Loss' if x<0 else 'Profit')
    fig=px.bar(sub,y='Product group',x='Profit',color='Result',orientation='h',hover_data=['NetSales','ProfitMarginPct'],title='Subcategory profit: strongest and weakest contributors',color_discrete_map={'Profit':'#188477','Loss':'#b53939'})
    fig.update_xaxes(title='Profit (₹)',rangemode='tozero');draw(fig)
    st.dataframe(categories[['Category','NetSales','Profit','ProfitMarginPct','SalesSharePct','ProfitSharePct']],hide_index=True)
with e:
    st.header('Q4. Discounts and profitability')
    fig=px.scatter(d,x='DiscountPercent',y='ProfitMarginPct',size='NetSales',color='Category',size_max=28,hover_data=['Order_ID','Region','NetSales','Profit'],title='Transaction margin versus discount; marker area represents net sales',color_discrete_map={'Technology':'#245b8a','Furniture':'#b37836','Office Supplies':'#716096'})
    fig.add_hline(y=0,line_color='#b53939');fig.update_xaxes(title='Discount (%)');fig.update_yaxes(title='Transaction profit margin (%)');draw(fig)
    bands=summarize(d,'DiscountBand').set_index('DiscountBand').reindex(['0%','>0-10%','>10-20%','>20%']).dropna().reset_index()
    bands['Result']=bands.Profit.map(lambda x:'Loss' if x<0 else 'Profit')
    fig=px.bar(bands,x='DiscountBand',y='ProfitMarginPct',color='Result',hover_data=['NetSales','Profit','Transactions'],title='Discount-band margin: ratio of summed profit to summed net sales',color_discrete_map={'Profit':'#188477','Loss':'#b53939'})
    fig.update_yaxes(title='Profit margin (%)',rangemode='tozero');draw(fig)
    st.dataframe(bands[['DiscountBand','Transactions','NetSales','Profit','ProfitMarginPct','GrossWeightedDiscountPct']],hide_index=True)
    st.caption('Bands: exactly 0%, (0,10%], (10%,20%], and >20%. Association is not causation; product mix and costs may differ.')
    st.subheader('Q5. Two priorities from the complete 2024–2026 dataset')
    st.write('1. Introduce approval and margin checks for discounts above 20%. Across all data, 64 transactions in this band lose ₹7,422.04 at −0.71% margin. Pilot within comparable products and regions before changing policy; no causal uplift is assumed.')
    st.write('2. Protect availability of Technology/Computers, while testing accessories attachment. Computers account for 39.73% of all sales at 13.75% margin; Technology/Accessories earns 28.29%. Validate stock constraints and customer demand before a small bundle pilot; do not assume cross-selling will succeed.')
    st.subheader('Connected story — complete dataset, unaffected by filters')
    st.write('Sales rise from ₹7.79m to ₹15.81m while margin improves from 12.14% to 19.09%. That growth is concentrated: Technology supplies 78.28% of sales, and West leads revenue while North has the stronger margin. Discount bands then expose a specific risk: the >20% band loses money overall. These descriptive findings support controlled margin safeguards and a product-mix pilot, rather than indiscriminate expansion or discounting.')
