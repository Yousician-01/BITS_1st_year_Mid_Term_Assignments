from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parent/'Data_Visualization_and_Storytelling'
for name in ['notebooks','dashboard','output','reports','figures']:(root/name).mkdir(exist_ok=True)
cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s):cells.append(nbf.v4.new_code_cell(s.strip()))

md('''# From Raw Data to Business Decisions
**BITS Pilani Digital | Data Visualization and Storytelling | Assignment 1**

I examine the supplied retail transactions for 2024–2026 to explain sales, profitability,
regional and product differences, and the relationship with discounts. I use Python for a
reproducible preparation process and a Streamlit/Plotly dashboard to communicate the findings.
All results come from the supplied workbooks; the original files remain unchanged.

The student guide defines INR (₹), discounts as fractions, Unit_Cost per item and shipping
expense per transaction. Order_ID is a transaction identifier. In these supplied files, each
retained transaction contains one product, and Order_ID is unique after exact deduplication.
I do not import assumptions from the separate Data Preprocessing assignment.''')
md('''## Task 1 — Understanding the Business Questions

| Business question | Relevant measures | Required comparisons | Proposed visualization |
|---|---|---|---|
| Q1: How have sales changed, and are patterns seasonal? | Net sales, profit, annual sales growth | Full years; matching calendar months across three years | Annual grouped bars and monthly multi-series line |
| Q2: Which regions lead or lag, and does revenue imply profitability? | Net sales, profit, ratio-of-sums margin, sales share | Region rankings on sales, profit and margin | Grouped horizontal bars with a margin table |
| Q3: Which products contribute most and least? | Category/subcategory sales, profit, contributions and margins | Categories; category-qualified subcategories | Category grouped bars and a ranked subcategory-profit bar chart |
| Q4: How are discounts associated with sales and profitability? | Discount fraction, net sales, profit, margin | Transactions and documented discount bands; category context | Margin-versus-discount scatter and band-margin bars |
| Q5: Which two actions should management prioritize? | Evidence from Q1–Q4 | Size and practicality of opportunities; checks before action | Two evidence-linked recommendations beside the connected story |

Net sales describes revenue after discount, while profit subtracts product cost and shipping.
Considering both avoids treating sales growth as automatically beneficial. Comparable full-year
and calendar-month views help separate isolated peaks from patterns repeated across years.
The discount comparison is descriptive: product mix, quantity and costs can differ across bands.''')
md('''## Task 2 — Data preparation and integration
### Inspecting the files before combining them
I inspect every supplied sheet, including the student guide. The annual tables should share
the same schema; master tables have a different grain and must have unique keys for safe joins.''')
code('''from pathlib import Path
import sys
import numpy as np
import pandas as pd
from IPython.display import display

ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
sys.path.insert(0, str(ROOT))
from retail_metrics import derive_measures, summarize, annual_summary, monthly_sales
DATA = ROOT / 'Data'
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:,.3f}'.format)

guide = pd.read_excel(DATA / 'BITS_Retail_Student_Guide.xlsx', sheet_name=None)
for sheet, frame in guide.items():
    print(f'\\nStudent guide — {sheet}: field definitions and business conventions')
    display(frame)

annual = {}
source_rows = []
for year in [2024, 2025, 2026]:
    path = DATA / f'BITS_Retail_{year}.xlsx'
    workbook = pd.ExcelFile(path)
    print(f'\\n{path.name} — sheets: {workbook.sheet_names}')
    frame = pd.read_excel(path, sheet_name=workbook.sheet_names[0])
    annual[year] = frame
    source_rows.append([year, len(frame), frame.shape[1], int(frame.duplicated().sum())])
    print('Dimensions (rows, columns):', frame.shape, '| columns:', frame.columns.tolist())
    print('Inferred types and non-null counts:')
    frame.info()
    print('First five transaction records:')
    display(frame.head())
    print('Missing values by field:')
    display(frame.isna().sum().rename('Missing').to_frame())
    print('Descriptive statistics for numeric business fields:')
    display(frame[['Quantity','Unit_Price','Discount_Pct','Shipping_Cost']].describe())
source_summary = pd.DataFrame(source_rows, columns=['Source year','Rows','Columns','Exact duplicate copies'])
print('\\nAnnual source inventory: raw rows, schema size and exact duplicates')
display(source_summary)

masters = pd.read_excel(DATA / 'BITS_Retail_Master.xlsx', sheet_name=None)
products = masters['Product_Master'].copy()
customers = masters['Customer_Master'].copy()
for sheet, frame in masters.items():
    print(f'\\nMaster sheet {sheet}: shape {frame.shape}; columns {frame.columns.tolist()}')
    frame.info()
    print('First five master records:')
    display(frame.head())
    print('Missing values and exact duplicate copies:')
    display(frame.isna().sum().rename('Missing').to_frame())
    print('Exact duplicate copies:', frame.duplicated().sum())
    print('Master-field descriptive summary (keys treated as identifiers):')
    display(frame.describe(include='all'))
''')
md('''### Appending annual transactions and assessing quality
I preserve every column and record the source year. Repeated customer or product IDs represent
valid repeat activity; exact duplicate transactions are assessed separately. The date check
compares recorded transaction years with source files, without truncating the supplied 2026 data.''')
code('''transaction_columns = annual[2024].columns.tolist()
assert all(frame.columns.tolist() == transaction_columns for frame in annual.values())
orders = pd.concat([annual[year].assign(Source_Year=year) for year in [2024,2025,2026]], ignore_index=True)
print('Append operation: raw annual schemas agree; no columns discarded.')
print('Rows loaded by year:', {year: len(frame) for year,frame in annual.items()})
print('Rows after pd.concat:', len(orders))
assert len(orders) == sum(len(frame) for frame in annual.values())

orders['Order_Date'] = pd.to_datetime(orders.Order_Date, format='%Y-%m-%d', errors='coerce')
invalid_dates = orders.Order_Date.isna()
wrong_year = orders.Order_Date.dt.year.ne(orders.Source_Year)
duplicate_mask = orders.duplicated(subset=transaction_columns)
missing_required = orders[transaction_columns].isna().any(axis=1)
numeric = ['Quantity','Unit_Price','Discount_Pct','Shipping_Cost']
invalid_numeric = (~np.isfinite(orders[numeric])).any(axis=1) | orders.Quantity.le(0) | orders.Quantity.mod(1).ne(0) | orders.Unit_Price.le(0) | ~orders.Discount_Pct.between(0,1) | orders.Shipping_Cost.lt(0)
print('\\nTransaction-quality counts before cleaning (conditions can overlap)')
display(pd.Series({'Invalid dates':invalid_dates.sum(), 'Date/source-year mismatch':wrong_year.sum(),
                   'Rows with missing required fields':missing_required.sum(),
                   'Invalid numeric business values':invalid_numeric.sum(),
                   'Exact duplicate copies':duplicate_mask.sum()},name='Rows').to_frame())
print('Raw region labels:', sorted(orders.Region.unique()))
print('Raw product-category labels:', [repr(x) for x in products.Category.unique()])
print('Customer segments:', sorted(customers.Customer_Segment.unique()))
assert not (invalid_dates | wrong_year | missing_required | invalid_numeric).any()
''')
md('''### Normalizing labels and merging master data
I use a documented mapping for verified aliases, rather than fuzzy matching. Product and
customer keys must be unique in their respective masters. Left joins preserve transactions,
and `many_to_one` prevents duplicated master keys from multiplying their values.''')
code('''category_mapping = {'Tech':'Technology', 'Office Suply':'Office Supplies', 'Office Suppllies':'Office Supplies'}
before_category = products.Category.copy()
trimmed_category = before_category.str.strip()
products['Category'] = trimmed_category.replace(category_mapping)
category_changes = products.loc[before_category.ne(products.Category), ['Product_ID','Category']].copy()
category_changes.insert(1, 'Original category', before_category[before_category.ne(products.Category)])
print('Category corrections: original master labels and normalized categories')
display(category_changes)
print('Explicit alias mapping:', category_mapping)
assert set(products.Category) == {'Technology','Furniture','Office Supplies'}
assert products.Product_ID.is_unique and customers.Customer_ID.is_unique
assert products.notna().all().all() and customers.notna().all().all()
assert np.isfinite(products.Unit_Cost).all() and products.Unit_Cost.gt(0).all()

# Demonstrate separate merges with indicators and row-count/cardinality checks.
before_product_merge = len(orders)
integrated = orders.merge(products, on='Product_ID', how='left', validate='many_to_one', indicator=True)
product_matches = integrated['_merge'].eq('both').sum()
unmatched_products = integrated.loc[integrated['_merge'].eq('left_only'),'Product_ID'].unique().tolist()
integrated = integrated.drop(columns='_merge')
before_customer_merge = len(integrated)
integrated = integrated.merge(customers, on='Customer_ID', how='left', validate='many_to_one', indicator=True)
customer_matches = integrated['_merge'].eq('both').sum()
unmatched_customers = integrated.loc[integrated['_merge'].eq('left_only'),'Customer_ID'].unique().tolist()
integrated = integrated.drop(columns='_merge')
merge_audit = pd.DataFrame([
    ['Product master', before_product_merge, before_customer_merge, product_matches, len(unmatched_products), products.Product_ID.duplicated().sum()],
    ['Customer master', before_customer_merge, len(integrated), customer_matches, len(unmatched_customers), customers.Customer_ID.duplicated().sum()]],
    columns=['Merge','Rows before','Rows after','Matched rows','Unmatched keys','Duplicate master keys'])
print('\\nMaster-join audit: both joins must preserve transaction counts')
display(merge_audit)
print('Unmatched product keys:',unmatched_products,'| unmatched customer keys:',unmatched_customers)
assert len(integrated) == len(orders) and not unmatched_products and not unmatched_customers
''')
md('''### Cleaning policy and guide-based measures
I remove extra fully identical transaction copies, retaining the first. The guide defines
Order_ID as a unique transaction identifier; I verify that no conflicting repeated IDs remain.
Positive unusual quantities, prices and shipping expenses are retained when valid. I do not
remove transactions simply because they produce losses.

The financial definitions use the supplied guide's raw-field meanings:

| Measure | Calculation |
|---|---|
| GrossSales | Quantity × Unit_Price |
| DiscountAmount | GrossSales × Discount_Pct (a fraction) |
| NetSales | GrossSales − DiscountAmount |
| ProductCost | Quantity × Unit_Cost |
| Profit | NetSales − ProductCost − Shipping_Cost, with shipping subtracted once per transaction |
| ProfitMarginPct | 100 × Profit / NetSales |

For group margins I divide summed profit by summed net sales. A gross-sales-weighted discount
is summed DiscountAmount divided by summed GrossSales; it is not the simple transaction average.
The guide supplies field conventions rather than a prewritten profit equation, so this expense
definition is stated explicitly. No taxes, returns or other unavailable costs are invented.''')
code('''cleaned = integrated.drop_duplicates(subset=transaction_columns).copy()
assert cleaned.Order_ID.is_unique, 'Investigate conflicting non-identical records sharing Order_ID'
cleaned = derive_measures(cleaned)
print('Cleaning rows: appended / after exact deduplication:',len(integrated),'/',len(cleaned))
print('Financial preview: raw inputs and each derived monetary component (INR)')
display(cleaned[['Order_ID','Quantity','Unit_Price','Discount_Pct','Unit_Cost','Shipping_Cost',
                 'GrossSales','DiscountAmount','NetSales','ProductCost','Profit','ProfitMarginPct']].head())

outlier_rows = []
for field in ['Quantity','Unit_Price','Shipping_Cost']:
    q1,q3 = cleaned[field].quantile([.25,.75]); iqr=q3-q1
    lower,upper = q1-1.5*iqr,q3+1.5*iqr
    flagged = ((cleaned[field]<lower)|(cleaned[field]>upper)).sum()
    outlier_rows.append([field,lower,upper,int(flagged),'Retained; valid positive values, not proven errors'])
outliers = pd.DataFrame(outlier_rows,columns=['Field','Lower IQR fence','Upper IQR fence','Flagged rows','Decision'])
print('\\nUnusual-value assessment on retained transactions; these are flags, not errors')
display(outliers)
print('Product-price context: price ranges differ by category')
display(cleaned.groupby('Category').Unit_Price.agg(['min','median','max']))
print('Loss-making transactions retained:',int(cleaned.Profit.lt(0).sum()))
print('Date coverage:',cleaned.Order_Date.min().date(),'through',cleaned.Order_Date.max().date())
print('Transactions after 15 November 2026:',int(cleaned.Order_Date.gt('2026-11-15').sum()))
''')
md('''The supplied academic dataset covers the complete 2024–2026 scope, including dates after
15 November 2026. I retain these supplied records rather than truncating 2026 or claiming that
they represent verified real-world sales already completed. The IQR table documents unusually
large valid purchases; product-price differences provide a reason not to cap prices globally.''')
code('''cleaning_log = pd.DataFrame([
    ['Exact duplicate copies','Annual transactions',int(duplicate_mask.sum()),'Removed extra copies; retained first','Guide identifies Order_ID as a unique transaction','Order_ID unique after cleaning'],
    ['Category spelling/aliases','Product_Master.Category',int(trimmed_category.ne(products.Category).sum()),'Mapped Tech, Office Suply and Office Suppllies to documented categories','Genuine aliases of supplied business categories','Exactly three normalized categories'],
    ['Outer category whitespace','Product_Master.Category',int(before_category.ne(trimmed_category).sum()),'Trimmed outer whitespace','Formatting does not define a new category','No outer category whitespace remains'],
    ['Missing required transaction values','Transaction fields',int(missing_required.sum()),'No records removed','No missing inputs to required measures','All required fields present'],
    ['Unmatched master keys','Product_ID / Customer_ID',len(unmatched_products)+len(unmatched_customers),'Retained all matched transactions; no attributes invented','No unmatched keys found','Both joins preserve row counts'],
    ['Invalid dates or source-year mismatch','Order_Date',int((invalid_dates|wrong_year).sum()),'Parsed dates; no records removed','Scope must agree with source year','All dates valid and agree with source year'],
    ['Invalid numeric values','Quantity, prices, discount, shipping',int(invalid_numeric.sum()),'No correction or removal needed','Positive quantities/prices; discounts 0-1; nonnegative shipping','All numeric validity assertions pass'],
    *[['IQR statistical extremes',row['Field'],row['Flagged rows'],'Retained without capping','Unusual but valid values are not necessarily errors','No extra rows removed'] for row in outliers.to_dict('records')],
    ['Negative calculated profit','Profit',int(cleaned.Profit.lt(0).sum()),'Retained losses','A valid transaction may lose money','Losses remain visible in all summaries']
],columns=['Issue','Field','Records affected','Action taken','Justification','Validation outcome'])
print('Cleaning log: records removed, labels corrected and valid unusual records retained')
display(cleaning_log)

# Independent arithmetic checks on representative first, middle and last records.
for row in cleaned.iloc[[0,len(cleaned)//2,-1]].itertuples():
    expected_net = row.Quantity*row.Unit_Price*(1-row.Discount_Pct)
    expected_profit = expected_net-row.Quantity*row.Unit_Cost-row.Shipping_Cost
    assert np.isclose(row.NetSales,expected_net) and np.isclose(row.Profit,expected_profit)
assert np.isfinite(cleaned[['NetSales','ProductCost','Profit','ProfitMarginPct']]).all().all()
assert cleaned.DiscountBand.notna().all() and cleaned.Order_ID.is_unique
assert (cleaned.Year==cleaned.Source_Year).all()
for field in ['Year','Region','Category']:
    assert np.isclose(cleaned.groupby(field).NetSales.sum().sum(),cleaned.NetSales.sum())
    assert np.isclose(cleaned.groupby(field).Profit.sum().sum(),cleaned.Profit.sum())

cleaned.to_csv(ROOT / 'output/BITS_Retail_Cleaned_Integrated.csv',index=False,date_format='%Y-%m-%d')
cleaning_log.to_csv(ROOT / 'output/Data_Cleaning_Log.csv',index=False)
reloaded = pd.read_csv(ROOT / 'output/BITS_Retail_Cleaned_Integrated.csv')
assert len(reloaded)==len(cleaned) and reloaded.Order_ID.is_unique
assert np.allclose(reloaded.NetSales,cleaned.NetSales) and np.allclose(reloaded.Profit,cleaned.Profit)
print('All preparation checks passed. Exported transaction-level rows:',len(reloaded))
print('The cleaned CSV preserves original transaction inputs, master attributes and derived measures.')
''')
md('''## Task 3 — Business analysis and visualization selection
### Q1: Sales and profit across years and months
I compare full-year totals and consecutive-year growth, then align monthly net sales on the
same January–December axis. Annual bars show scale; monthly lines help assess whether peaks
repeat. A single high month is insufficient evidence of seasonality.''')
code('''annual_results = annual_summary(cleaned)
monthly_results = monthly_sales(cleaned)
print('Annual performance: INR totals, ratio-of-sums margin and consecutive-year sales growth')
display(annual_results)
print('Monthly net sales: comparable calendar months, columns are years (INR)')
display(monthly_results.pivot(index='Month',columns='Year',values='NetSales'))
print('Peak net-sales month in each supplied year')
display(monthly_results.loc[monthly_results.groupby('Year').NetSales.idxmax()])
print('Fourth-quarter net-sales share within each year (%)')
display((monthly_results[monthly_results.Month.ge(10)].groupby('Year').NetSales.sum()/cleaned.groupby('Year').NetSales.sum()*100).rename('Q4 sales share').to_frame())
''')
md('''### Q2: Regional sales and profitability
I compare net sales, absolute profit and the ratio-of-sums margin. Grouped horizontal bars
support ranking on a common INR scale, while the accompanying table makes margins explicit.
Contributions always use the total within the same filter scope.''')
code('''regional_results = summarize(cleaned,'Region').sort_values('NetSales',ascending=False)
print('Regional performance ranked by net sales: profit, margin and contribution remain separate measures')
display(regional_results)
print('Regional performance by year: does a pooled ranking hide a change?')
display(summarize(cleaned,['Year','Region'])[['Year','Region','NetSales','Profit','ProfitMarginPct']])
''')
md('''### Q3: Category and subcategory contribution
I use normalized categories and consider sales alongside profit. A category-qualified subcategory
label keeps Furniture/Storage distinct from Office Supplies/Storage. The dashboard ranks
subcategory profit with a visible zero line, so losses cannot be hidden by positive revenue.''')
code('''category_results = summarize(cleaned,'Category').sort_values('NetSales',ascending=False)
subcategory_results = summarize(cleaned,['Category','Subcategory']).sort_values('Profit',ascending=False)
print('Category contribution: net sales, profit, margin, and shares of the matching totals')
display(category_results)
print('Category/subcategory performance ranked by profit')
display(subcategory_results)
''')
md('''### Q4: Discounting, sales and profitability
I compare transaction margins against discount rates and aggregate discount bands. Marker area
shows net sales in the scatter plot; category color supplies context. The band chart summarizes
margin as total profit / total net sales. Boundaries are 0%, (0,10%], (10%,20%], and >20%.
Rounding the grouping key avoids floating-point artifacts at boundaries; monetary calculations
retain the supplied discount fractions. These comparisons describe associations, not causal effects.''')
code('''discount_results = summarize(cleaned,'DiscountBand')
discount_by_category = summarize(cleaned,['Category','DiscountBand'])
print('Discount-band performance: boundaries are documented above; all transactions are included')
display(discount_results)
print('Discount-band margins within categories: product-mix context')
display(discount_by_category[['Category','DiscountBand','Transactions','NetSales','Profit','ProfitMarginPct']])
print('Unweighted mean transaction discount (%):',round(cleaned.Discount_Pct.mean()*100,3))
print('Gross-sales-weighted discount (%):',round(cleaned.DiscountAmount.sum()/cleaned.GrossSales.sum()*100,3))
print('Descriptive Pearson correlation: discount fraction vs transaction profit margin:',round(cleaned.Discount_Pct.corr(cleaned.ProfitMarginPct),3))
''')
md('''## Task 4 — Visualization design
The dashboard uses blue for net sales, teal for profit and red for negative profit. Ordinary bars
include zero; margins are percentages on separate axes rather than sharing an INR axis. Years
have consistent colors and line styles. Sorted categories and clear units support comparison;
hover text provides exact values and context without crowding labels. I use four coordinated
filter controls (year, region, category and segment), a reset button and an explicit empty-state
message. Insights tied to current filters are recalculated; management priorities derived from
the full dataset are labeled as such. There are seven visuals, each serving Q1–Q4 rather than
adding decorative charts. Q5 is answered through two actions supported by the resulting story.''')
md('''## Task 5 — Connected business insights
The evidence-based narrative is added after inspecting the computed results above.''')
md('''## Task 6 — Two management recommendations
The final two priorities are selected from the measured findings, with expected direction of
benefit and checks before action. No unsupported financial uplift is forecast.''')
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
nbf.write(nb,root/'notebooks/Retail_Data_Preparation_and_Analysis.ipynb')
print('Notebook created:',len(cells),'cells')
