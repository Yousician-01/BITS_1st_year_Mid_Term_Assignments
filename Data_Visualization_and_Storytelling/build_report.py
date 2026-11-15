"""Reproduce the report from the validated CSV and genuine dashboard captures."""
from pathlib import Path
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from retail_metrics import annual_summary,summarize

R=Path(__file__).resolve().parent
d=pd.read_csv(R/'output/BITS_Retail_Cleaned_Integrated.csv')
annual=annual_summary(d)
pdfmetrics.registerFont(TTFont('Academic','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('AcademicBold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Academic',normal='Academic',bold='AcademicBold',italic='Academic',boldItalic='AcademicBold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyA',fontName='Academic',fontSize=10.5,leading=14,spaceAfter=8))
styles.add(ParagraphStyle(name='HeadA',fontName='AcademicBold',fontSize=15,leading=19,spaceAfter=10,keepWithNext=True))
styles.add(ParagraphStyle(name='CellA',fontName='Academic',fontSize=9,leading=11))
story=[]; W=A4[0]-90
def p(s):story.append(Paragraph(s,styles['BodyA']))
def h(s):story.append(Paragraph(s,styles['HeadA']))
def table(headers,rows,widths):
 t=Table([[Paragraph(str(x),styles['CellA']) for x in row] for row in [headers,*rows]],colWidths=widths,repeatRows=1)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eff4')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,colors.grey)]))
 story.extend([t,Spacer(1,10)])
def shot(index,caption,width=W):
 from PIL import Image as PIL
 path=R/f'figures/chart_{index}.png'
 with PIL.open(path) as im:height=width*im.height/im.width
 story.append(Image(str(path),width=width,height=height));p(caption)
def page():story.append(PageBreak())

h('From Raw Data to Business Decisions')
p('<b>BITS Pilani Digital · Data Visualization and Storytelling · Assignment 1</b>')
p('The retailer sells technology, furniture and office supplies across five regions. Management needs to understand whether growth translates into profit, where performance is concentrated and which actions are justified. I integrate the supplied 2024–2026 records, derive financial measures under the student guide and use an interactive dashboard to connect the evidence to two management priorities.')
h('1. Understanding the management questions')
table(['Question','Measures and comparisons','Visual evidence'],[
 ['Q1: Sales change and seasonal patterns','Annual net sales, profit, consecutive-year growth and matching calendar months','Annual bars and monthly lines'],
 ['Q2: Regional performance','Sales, profit, ratio-of-sums margin and contribution','Grouped regional bars and margin table'],
 ['Q3: Product contribution','Category and category-qualified subcategory sales, profit, shares and margins','Category bars and ranked subcategory profit'],
 ['Q4: Discount relationship','Transaction margins and band totals; product-category context','Scatter and discount-band margin bars'],
 ['Q5: Two priorities','Measured opportunities, expected benefits and checks before action','Evidence-linked recommendations in Section 6']], [125,235,W-360])
p('The measures separate scale from profitability. All monetary figures are Indian rupees (₹); “sales” means net sales after discount. Orders are distinct Order_ID values, which the guide defines as transaction identifiers. After deduplication these records each contain one product. Repeated customer or product keys are valid repeat activity, not duplicates.')
h('Dashboard design and access')
p('Seven Plotly visuals are arranged in four tabs. Year, region, category and customer-segment multiselect filters affect every chart and KPI. A reset button restores the full dataset; empty selections receive a clear message. Current-scope regional findings are recalculated, while the full-dataset story and priorities are explicitly labeled. Net sales use blue and profit teal; negative profit uses red and remains visible. Bars include zero, and percentages are not mixed onto currency axes.')
p('The editable local application runs with <b>streamlit run dashboard/app.py</b>. It reads the included cleaned CSV and needs no credentials or hosted service. Figures in this report are screenshots of the functioning dashboard, captured in Chrome with all filters selected; interface captures showing controls and KPIs are also included in figures/. This is a local application, not a claimed hosted deployment.')
page()
h('2. Preparation, integration and validation')
p('The annual workbooks share nine transaction columns. The product master contains 15 records and five attributes; the customer master contains 220 records and two attributes. I inspected all sheets, missingness, types, duplicate copies and financial ranges before integration. The student guide supplies the field meanings and currency.')
table(['Operation','Input rows','Output rows','Validation'],[
 ['Append 2024 / 2025 / 2026','362 / 442 / 512','1,316','Compatible schemas; no columns discarded'],
 ['Product master left join','1,316','1,316','All matched; unique Product_ID; many-to-one'],
 ['Customer master left join','1,316','1,316','All matched; unique Customer_ID; many-to-one'],
 ['Exact deduplication','1,316','1,310','Six extra copies removed; Order_ID unique']], [150,85,85,W-320])
p('Two duplicate copies were removed from each annual source, leaving 360, 440 and 510 transactions. Product/customer keys matched completely and neither join multiplied or lost rows. Category aliases Tech, Office Suply and Office Suppllies were mapped to Technology and Office Supplies, with genuine outer whitespace trimmed. Furniture was retained as a distinct category. Category-qualified subcategories prevent Storage or Accessories in different categories from being combined accidentally.')
p('No missing required transaction fields, malformed dates, date/source-year mismatches or invalid numeric business values were found. Quantity and unit price were positive, discounts lay within 0–1, shipping was nonnegative, and master unit costs were valid. Statistical IQR extremes in quantity, price and shipping were documented and retained: a costly computer or bulk purchase is not automatically erroneous. Loss-making transactions remain in the analysis. The separate cleaning log records affected counts, actions, reasons and validation outcomes, including checks finding zero issues.')
table(['Measure','Guide-based calculation'],[
 ['Gross sales','Quantity × Unit_Price'],['Discount amount','Gross sales × Discount_Pct (fraction)'],
 ['Net sales','Gross sales − discount amount'],['Product cost','Quantity × Unit_Cost'],
 ['Profit','Net sales − product cost − Shipping_Cost'],['Aggregated margin','100 × summed profit / summed net sales']], [140,W-140])
p('Shipping is an expense for the entire transaction and is subtracted once, not multiplied by quantity. The guide gives raw-field conventions; the above profit definition explicitly combines the supplied costs without inventing tax or other expenses. Gross-sales-weighted discount is summed discount amount divided by summed gross sales, distinct from an unweighted transaction average. Annual, regional and category totals reconcile to transaction totals; first, middle and last records were independently checked arithmetically. The notebook executes from a clean kernel and exports both CSV files.')
page()
h('3. Growth and regional differences — Q1 and Q2')
table(['Year','Net sales (₹)','Profit (₹)','Margin','Sales growth'],[[str(int(x.Year)),f'{x.NetSales:,.2f}',f'{x.Profit:,.2f}',f'{x.ProfitMarginPct:.2f}%', '—' if pd.isna(x.YoYSalesPct) else f'{x.YoYSalesPct:.2f}%'] for x in annual.itertuples()],[45,125,115,85,W-370])
p('Net sales grow 49.04% in 2025 and 36.13% in 2026. Margin improves from 12.14% to 19.09%, so profit grows faster than revenue across the supplied years. The monthly dashboard view peaks in October in 2024 and 2026, but June in 2025. This is insufficient evidence of a stable recurring seasonal mechanism; promotions or product mix are possible hypotheses, not established explanations.')
shot(2,'Figure 1. Actual dashboard screenshot: monthly comparisons use the same January–December axis for all years.')
shot(3,'Figure 2. Actual regional dashboard screenshot: common INR units preserve the difference between revenue scale and profit.')
p('West leads sales (₹10.56m) and profit (₹1.77m), whereas Central is lowest (₹3.88m and ₹0.52m). North has the highest regional margin at 17.33%, ahead of West at 16.76%; Central earns 13.28%. Thus the revenue leader is not the margin leader, and expanding a high-sales region alone does not establish the best marginal investment.')
page()
h('4. Product performance — Q3')
shot(4,'Figure 3. Actual dashboard screenshot: category revenue and profit use the same currency scale.')
p('Technology contributes 78.28% of sales and 74.84% of profit, making it the principal source of scale. Its 15.75% margin is below Furniture (18.79%) and Office Supplies (22.01%). Office Supplies has the strongest category margin but only 1.95% of revenue, so margin leadership alone does not make it the largest absolute profit opportunity.')
shot(5,'Figure 4. Actual dashboard screenshot: subcategory labels retain category context, and the zero origin supports honest comparisons.')
p('Computers lead both subcategory sales (₹13.99m) and profit (₹1.92m), yet margin is 13.75%. Office Supplies/Writing is lowest in sales (₹60,791.98) and profit (₹10,359.85). Technology/Accessories earns 28.29% margin on ₹1.55m sales. This supports protecting the core Computers business while investigating a complementary-product pilot; it does not establish that existing customers would buy additional accessories.')
page()
h('5. Discount relationships and the business story — Q4')
shot(6,'Figure 5. Actual dashboard scatter: marker area represents net sales; category color provides product-mix context. The horizontal zero line keeps losses visible.')
shot(7,'Figure 6. Actual dashboard screenshot: each band margin is summed profit divided by summed net sales, not an average of transaction margins.')
p('The zero-discount band earns 23.80% margin. Margins fall to 17.93% for (0,10%], 10.74% for (10%,20%], and −0.71% above 20%. The final band contains 64 transactions and ₹1.05m net sales but loses ₹7,422.04 overall. Boundaries are explicit and all retained records are assigned; float artifacts are rounded only for band assignment, not monetary calculations. These associations do not isolate a causal discount effect: product mix, quantities, regions and shipping expenses also vary.')
p('Three findings connect the story. First, growing sales accompany improving profit margins. Second, the gains are concentrated in Technology and high-revenue regions, while margin rankings differ from revenue rankings. Third, high-discount activity exposes a specific loss-making pocket despite healthy overall growth. Management should therefore protect the core revenue stream and test targeted margin safeguards, rather than treating every region, product or promotion as equally attractive.')
page()
h('6. Management priorities — Q5')
p('<b>Priority 1: require approval and a contribution-margin check for discounts above 20%.</b> The 64 transactions in this band lose ₹7,422.04 despite ₹1.05m in sales. Check product cost and shipping before approving the promotion, then pilot the policy within comparable product/region groups. The intended benefit is fewer loss-making promotions. Demand and volume responses must be monitored; the observational data cannot justify a numerical uplift forecast or prove that a blanket discount ban would improve profit.')
p('<b>Priority 2: protect Computers availability and pilot Technology/Accessories attachment.</b> Computers supplies 39.73% of total revenue at 13.75% margin, while Technology/Accessories earns 28.29%. Preserve availability of the major sales contributor and test whether relevant accessories can improve contribution. Before scaling, check stock constraints, customer demand and incremental margin in a small controlled bundle pilot. Current data does not establish unmet demand, stock-outs or existing cross-selling effects. The expected benefit is more balanced purchase value and margin, without assuming a guaranteed outcome.')
h('Methodological and interpretation limits')
p('The supplied academic data extends through 28 December 2026, including records later than the preparation date. The assignment explicitly asks for the supplied full-year scope; these values should not be described as verified completed real-world sales. Three years and relatively few transactions per month constrain seasonal inference. Master costs are applied uniformly because no time-varying costs are supplied. Profit uses only the listed product and shipping expenses and is not comprehensive company net income.')
p('Exact duplicate removal follows the guide’s unique-transaction convention. No uncertain unmatched master attributes were invented. Discount comparisons are descriptive, and category mix can influence pooled margins. Revenue and profit contributions always use totals within matching filters. Dashboard growth is suppressed when selected years are not consecutive, and fixed recommendations are labeled as complete-dataset findings so they are not mistaken for results of a narrower selection.')
p('The preparation notebook, cleaning log and integrated transaction-level CSV provide the audit trail. The dashboard makes the comparisons accessible while preserving losses, units and filter scope. The two recommended pilots translate the evidence into feasible decisions whose effects must be measured before wider rollout.')
h('Sources')
p('BITS Pilani Digital. <i>Data Visualization and Storytelling, Assignment 1: From Raw Data to Business Decisions</i>, supplied assignment PDF. BITS Retail, supplied Orders_2024, Orders_2025, Orders_2026, Product_Master and Customer_Master workbooks. <i>BITS_Retail_Student_Guide.xlsx</i>, Data_Guide sheet: field meanings, INR and cost conventions. Screenshots are from the submitted local Streamlit dashboard; no external dataset was used.')
def footer(canvas,doc):
 canvas.setFont('Academic',9);canvas.drawCentredString(A4[0]/2,24,str(doc.page))
path=R/'reports/Data_Visualization_and_Storytelling_Report.pdf'
SimpleDocTemplate(str(path),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=38,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)
from pypdf import PdfReader
print('Report pages:',len(PdfReader(path).pages))
assert len(PdfReader(path).pages)<=7
