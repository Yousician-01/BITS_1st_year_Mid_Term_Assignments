"""Small shared set of guide-based measures and dashboard summaries (INR)."""
import numpy as np
import pandas as pd


def derive_measures(data):
    """Keep transaction grain; shipping is subtracted once, not per unit."""
    result=data.copy()
    result['Order_Date']=pd.to_datetime(result.Order_Date,format='%Y-%m-%d',errors='raise')
    result['GrossSales']=result.Quantity*result.Unit_Price
    result['DiscountAmount']=result.GrossSales*result.Discount_Pct
    result['NetSales']=result.GrossSales-result.DiscountAmount
    result['ProductCost']=result.Quantity*result.Unit_Cost
    result['Profit']=result.NetSales-result.ProductCost-result.Shipping_Cost
    result['ProfitMarginPct']=100*result.Profit/result.NetSales
    result['DiscountPercent']=100*result.Discount_Pct
    result['Year']=result.Order_Date.dt.year
    result['Month']=result.Order_Date.dt.month
    result['YearMonth']=result.Order_Date.dt.strftime('%Y-%m')
    # Round only the grouping key to avoid float artifacts at 10% and 20% boundaries.
    # The supplied discount fractions are preserved for monetary calculations.
    result['DiscountBand']=pd.cut(result.Discount_Pct.round(6),[-1e-9,0,.10,.20,1],
                                 labels=['0%','>0-10%','>10-20%','>20%'],right=True)
    return result


def summarize(data,by):
    """Ratios of matching sums, never averages of transaction margins."""
    columns=[by] if isinstance(by,str) else list(by)
    table=data.groupby(columns,observed=True).agg(
        NetSales=('NetSales','sum'),Profit=('Profit','sum'),GrossSales=('GrossSales','sum'),
        DiscountAmount=('DiscountAmount','sum'),Orders=('Order_ID','nunique'),
        Transactions=('Order_ID','size')).reset_index()
    table['ProfitMarginPct']=100*table.Profit/table.NetSales
    table['GrossWeightedDiscountPct']=100*table.DiscountAmount/table.GrossSales
    total_sales=table.NetSales.sum()
    total_profit=table.Profit.sum()
    table['SalesSharePct']=100*table.NetSales/total_sales if total_sales else np.nan
    table['ProfitSharePct']=100*table.Profit/total_profit if total_profit else np.nan
    return table


def annual_summary(data):
    table=summarize(data,'Year').sort_values('Year')
    table['YoYSalesPct']=table.NetSales.pct_change()*100
    # If the user selects 2024 and 2026, do not call the two-year change "YoY".
    table.loc[table.Year.diff().ne(1),'YoYSalesPct']=np.nan
    return table


def monthly_sales(data):
    table=data.groupby(['Year','Month']).NetSales.sum()
    grid=pd.MultiIndex.from_product([sorted(data.Year.unique()),range(1,13)],names=['Year','Month'])
    return table.reindex(grid,fill_value=0).rename('NetSales').reset_index()
