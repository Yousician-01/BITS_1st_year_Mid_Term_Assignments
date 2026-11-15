"""Build the final report from the completed notebook's existing results and figures.

This script reads the analysis summary and existing figures only. It does not execute or
modify the notebook, workbook, question paper or customer CSV.
"""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

ROOT = Path(__file__).resolve().parent
s = json.loads((ROOT / 'output/analysis_summary.json').read_text(encoding='utf-8'))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyReport', fontName='Times-Roman', fontSize=11, leading=14,
                         spaceAfter=8, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle(name='ReportTitle', fontName='Times-Bold', fontSize=19, leading=22,
                         alignment=1, spaceAfter=5))
styles.add(ParagraphStyle(name='ReportSubtitle', fontName='Times-Roman', fontSize=11, leading=14,
                         alignment=1, spaceAfter=14))
styles.add(ParagraphStyle(name='TaskHeading', fontName='Times-Bold', fontSize=13, leading=16,
                         spaceBefore=12, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name='TableCaption', fontName='Times-Bold', fontSize=9.5, leading=12,
                         spaceBefore=3, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name='SplitTableCaption', parent=styles['TableCaption'], keepWithNext=False))
styles.add(ParagraphStyle(name='FigureCaption', fontName='Times-Roman', fontSize=9.5, leading=12,
                         spaceBefore=4, spaceAfter=9))
styles.add(ParagraphStyle(name='TableText', fontName='Times-Roman', fontSize=9.5, leading=11.5))
styles.add(ParagraphStyle(name='TableNumber', parent=styles['TableText'], alignment=2))
styles.add(ParagraphStyle(name='TableHeader', fontName='Times-Bold', fontSize=9.5, leading=11.5))
story = []
WIDTH = A4[0] - 100

def p(text, keep=False):
    paragraph = Paragraph(text, styles['BodyReport'])
    story.append(KeepTogether([paragraph]) if keep else paragraph)

def heading(text):
    story.append(Paragraph(text, styles['TaskHeading']))

def table(caption, headers, rows, widths, numeric=(), split_rows=False):
    story.append(Paragraph(caption, styles['SplitTableCaption' if split_rows else 'TableCaption']))
    data = [[Paragraph(escape(str(x)), styles['TableHeader']) for x in headers]]
    for row in rows:
        data.append([Paragraph(escape(str(x)), styles['TableNumber' if i in numeric else 'TableText'])
                     for i, x in enumerate(row)])
    item = Table(data, colWidths=widths, repeatRows=1, splitByRow=int(split_rows), hAlign='LEFT')
    item.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ededed')),
        ('LINEABOVE', (0,0), (-1,0), .6, colors.black),
        ('LINEBELOW', (0,0), (-1,0), .4, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), .4, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.extend([item, Spacer(1,8)])

def figure(filename, caption):
    from PIL import Image as PILImage
    path = ROOT / 'figures' / filename
    with PILImage.open(path) as image:
        height = WIDTH * image.height / image.width
    story.append(KeepTogether([
        Image(str(path), width=WIDTH, height=height),
        Paragraph(caption, styles['FigureCaption'])]))

story.append(Paragraph('Data Preprocessing Assignment 1', styles['ReportTitle']))
story.append(Paragraph('MSc Data Pre-processing | MDSDF402 | T1-26', styles['ReportSubtitle']))
p('An online retailer wishes to understand customer purchasing behaviour and prepare features '
  'for a marketing campaign. Raw invoice lines cannot be used directly as customer observations: '
  'returns, missing identities and duplicate entries affect their meaning, while purchases must '
  'be aggregated before customers can be compared. This report explains the preprocessing '
  'decisions, their measured effects and the resulting customer similarities. The work ends '
  'with data preparation and proximity analysis; customer clustering is not implemented.')

heading('Task 1  Dataset understanding')
p(f'The local UCI Online Retail workbook (Chen, 2015) was restricted to invoice lines dated '
  f'1 September through 30 November 2011, inclusive, retaining all countries. The unchanged '
  f'baseline contains <b>{s["baseline_rows"]:,} lines and eight fields</b>, covering '
  f'{s["baseline_invoices"]:,} distinct invoice numbers and {s["countries"]} countries. '
  'This same subset was used for both dataset understanding and quality assessment, so '
  'neither missing identities nor invalid sales were removed before their prevalence was measured.')
table('Table 1. Field roles in the invoice-line dataset',
      ['Category', 'Fields', 'Interpretation'], [
          ['Identifiers', 'InvoiceNo, StockCode, CustomerID', 'Invoice, product and customer keys; numerical magnitudes have no business meaning'],
          ['Numeric', 'Quantity; UnitPrice', 'Discrete units; continuous unit price in GBP'],
          ['Date/time', 'InvoiceDate', 'Timestamp of the recorded invoice'],
          ['Categorical text', 'Description; Country', 'Product description and recorded customer country']],
      [80,190,WIDTH-270])
p('The records are individual invoice lines rather than complete invoices. An invoice containing '
  'several products therefore occupies multiple rows sharing InvoiceNo; these repetitions are '
  'expected and must not be confused with exact duplicates. The numerical summaries give a '
  'median quantity of 3 and median unit price of GBP 2.08, but also reveal negative quantities '
  'and zero prices. CustomerID is stored as a float because nulls occur, yet represents an '
  'identifier rather than a continuous measure. The notebook provides the inferred types, first '
  'five records and descriptive statistics supporting these observations.')

heading('Task 2  Data quality assessment')
p('Missing identity is the most consequential quality issue for customer profiling. CustomerID '
  'is absent on 38,564 lines (19.71%), preventing reliable attribution to individual shoppers. '
  'Description is missing on 278 lines (0.14%); this restricts product interpretation but does '
  'not necessarily prevent variety calculation when StockCode is known. No missing values '
  'occur in the other six fields. Table 2 distinguishes these effects from duplication, '
  'transaction adjustments and formatting differences.')
quality_rows = [
    ['Missing values','CustomerID','38,564','Cannot reliably attribute purchases to a customer'],
    ['Missing values','Description','278','Limits product interpretation; StockCode may still support variety'],
    ['Exact duplicate copies','All eight fields','2,506','May overstate units and spending'],
    ['Cancellation lines','InvoiceNo starts C','3,081','Return/correction activity outside completed sales'],
    ['Non-positive quantity','Quantity <= 0','3,462','Not positive completed-purchase quantities'],
    ['Non-positive price','UnitPrice <= 0','664','Free, adjustment or invalid-price entries'],
    ['Outer whitespace','Description','45,433','Inconsistent description labels'],
    ['Capitalization variants','StockCode','5,228','Risk of merging distinct product identifiers'],
    ['Unexpected types/values','Required fields','0','No malformed known IDs or other checked invalid values found'],
    ['IQR outliers','Quantity','10,471','Unusual quantities; not necessarily errors'],
    ['IQR outliers','UnitPrice','12,151','Unusual prices; not necessarily errors']]
table('Table 2. Quality issues measured on the unchanged baseline',
      ['Issue','Field','Count','Potential impact'], quality_rows,
      [108,92,52,WIDTH-252], numeric=(2,), split_rows=True)
p('The three transaction flags overlap: a cancellation may also have a non-positive quantity. '
  'Their union contains <b>3,745 distinct lines</b>, rather than the sum of the three separate '
  'counts. Exact duplicates were assessed across all eight fields, independently of repeated '
  'invoice numbers. Text inspection identified trailing spaces such as <font name="Courier">'
  "'BUTTON BOX '</font> and 67 capitalization-variant groups in StockCode, including "
  '<font name="Courier">15056N</font> and <font name="Courier">15056n</font>. These code '
  'variants were documented rather than assumed to be interchangeable. The checked text fields '
  'contained no blank strings. Validity checks found no invalid known customer IDs, unexpected '
  'invoice formats, missing/blank stock codes, non-finite quantities or prices, or missing '
  'timestamps in the baseline; alphanumeric stock codes are legitimate identifiers.')
p('Quantity and price outliers were identified using Q1 - 1.5 x IQR and Q3 + 1.5 x IQR. '
  'The quantity fences were -14 and 26; unit-price fences were GBP -3.07 and GBP 8.45. '
  'These thresholds flag statistical extremes, not proven errors. Large wholesale orders or '
  'expensive products can be genuine, so outlier status alone is insufficient grounds for '
  'deletion. This distinction informs the cleaning policy below.')

heading('Task 3  Data cleaning')
p('A separate completed-sales subset was created to describe identifiable customers through '
  'positive purchase activity. C-prefixed invoices, non-positive quantities and non-positive '
  'prices were excluded with one combined filter. Lines without CustomerID were then removed, '
  'followed by exact duplicate copies, retaining the first occurrence. The sequential audit '
  'in Table 3 avoids double-counting overlapping exclusions.')
table('Table 3. Sequential cleaning audit',
      ['Cleaning step','Rows before','Rows removed','Rows after'], [
          [row['Decision'],f'{row["Rows before"]:,}',f'{row["Rows removed"]:,}',f'{row["Rows after"]:,}']
          for row in s['cleaning']], [WIDTH-222,74,74,74], numeric=(1,2,3))
p('Excluding unidentified customers had the largest row-count effect: 37,821 otherwise-valid '
  'sales lines, representing GBP 569,091.25 of purchase value. Imputing IDs would risk combining '
  'unrelated shoppers into artificial profiles. Duplicate removal excluded a further 2,483 '
  'copies and GBP 11,436.29, limiting possible overstatement. However, identical entries may '
  'occasionally be legitimate purchases, and the absence of a unique line key prevents a '
  'definitive distinction. The baseline duplicate count is larger because some duplicate '
  'copies had already been excluded by earlier filters.')
p('Financial effects are signed Quantity x UnitPrice amounts. The combined sales filter '
  'excluded GBP -170,917.26 overall; removing negative return/correction value can therefore '
  'increase the remaining sum. These are observed exclusion values, not estimates of lost '
  f'revenue. The final <b>{s["cleaned_rows"]:,} lines total GBP {s["total_spend"]:,.2f}</b> '
  'in completed-sales spend, which must not be interpreted as net revenue after returns '
  'and cancellations.')
p('Outer whitespace was trimmed, changing 35,554 descriptions, for example '
  '<font name="Courier">\'BUTTON BOX \'</font> to <font name="Courier">\'BUTTON BOX\'</font>. '
  'Identifier case and internal characters were preserved to avoid merging different stock '
  'codes. Trimming changed neither row counts nor spend. Plausible positive IQR extremes were '
  'retained without capping, causing no additional removals. Assertions verified known '
  'customer IDs, nonblank stock codes, valid non-cancellation invoices and dates, positive '
  'quantities and prices, and finite line spend before customer aggregation.')

heading('Task 4  Data transformation and aggregation')
p(f'Grouping the completed-sales lines by CustomerID produced <b>{s["customers"]:,} unique '
  'customer observations</b>. The four features in Table 4 describe recent activity, repeat '
  'purchasing, monetary value and breadth of recorded purchases. They provide complementary '
  'views of purchasing behaviour without claiming to describe customer demographics or '
  'specific product preferences.')
table('Table 4. Customer features retained in original business units',
      ['Feature','Definition within September-November 2011'], [
          ['RecencyDays','Calendar days from the last completed purchase date to 1 December 2011'],
          ['Frequency','Number of distinct invoice numbers per customer'],
          ['TotalSpend','Sum of Quantity x UnitPrice, in GBP'],
          ['ProductVariety','Number of distinct StockCode values purchased']], [110,WIDTH-110])
p('The original spending distribution is strongly right-skewed: median spend is GBP 491.20, '
  'whereas the maximum is GBP 117,634.53. Applying natural log(1 + TotalSpend) reduced skewness '
  f'from <b>{s["spend_skew"]:.3f} to {s["log_skew"]:.3f}</b>. Figure 1 shows how compressing '
  'the upper tail produces a more balanced distribution for comparison. Original spending '
  'values remain in the customer table to preserve their monetary interpretation; the logged '
  'column is an additional representation, not a replacement for GBP spend.')
figure('spend_transformation.png',
       'Figure 1. Original customer spend (left) and log1p spend (right). The log transformation '
       'compresses the long right tail; the horizontal axes use different units.')
p('StandardScaler was fitted once to the four <i>original</i> numerical features. Table 5 '
  'compares their original scales with the resulting approximately zero means and unit '
  'population standard deviations. Scaling prevents GBP magnitudes from dominating distances '
  'solely because of units, but does not remove sensitivity to extreme customers. The same '
  'fitted scaled matrix was reused for reduction and both proximity measures; logged spend '
  'and recency categories were not added to those inputs.')
table('Table 5. Original and standardized feature scales',
      ['Feature','Original mean','Original pop. SD','Scaled mean / SD'], [
          [row['index'],f'{row["Original mean"]:,.3f}',f'{row["Original population std"]:,.3f}',
           f'{0 if abs(row["Scaled mean"])<1e-12 else row["Scaled mean"]:.3f} / {row["Scaled population std"]:.3f}']
          for row in s['scaling']], [105,115,125,WIDTH-345], numeric=(1,2,3))
p('Recency was also binned into right-closed intervals (0,30], (30,60] and (60,91], labelled '
  'Recent, Warm and Lapsed. These categories support a simple discussion of campaign timing, '
  'but lose differences within each band and create sharp boundaries between adjacent days. '
  'They describe activity in this three-month window rather than lifetime loyalty. Table 6 '
  'shows the group sizes and their observed median spending; these are descriptive comparisons, '
  'not evidence that recency causes spending differences.')
table('Table 6. Recency categories and observed spending',
      ['Recency category','Customers','Median spend (GBP)'], [
          [row['RecencyBand'],f'{row["Customers"]:,}',f'{row["MedianSpend"]:,.3f}']
          for row in s['bins']], [225,90,WIDTH-315], numeric=(1,2))
p('The exported CSV contains one row per CustomerID, the four business-unit features, '
  'Log1pTotalSpend and RecencyBand. Its seven-column schema has no missing feature values, '
  'duplicate customer IDs or extra index column. These checks preserve a usable customer '
  'table while making the two additional transformed columns explicit.')

heading('Task 5  Data reduction')
p('Correlation-based removal and PCA were applied to the same 2,851 x 4 standardized feature '
  'matrix. IDs were excluded. Correlation removal used an absolute Pearson threshold greater '
  'than 0.85: in the fixed feature order, a later feature would be removed only if it exceeded '
  'the threshold with an already retained feature. No feature met that rule. <b>All four '
  'features were retained, so this method did not reduce dimensionality.</b> Preserving them '
  'keeps their direct business meanings without discarding information solely to force a '
  'smaller table.')
figure('reduction.png',
       'Figure 2. Correlations among the standardized original features (left) and individual '
       'and cumulative PCA variance (right). No absolute correlation exceeds 0.85; three '
       'components are needed to cross the 90% cumulative-variance target.')
p('PCA constructs orthogonal combinations of the same inputs, concentrating variation into '
  'fewer numerical dimensions. The first two components explain 78.7948% of variance, '
  f'whereas <b>{s["n_components"]} components retain {s["cumulative"][s["n_components"]-1]:.4%}</b>; '
  'three is therefore the minimum reaching 90%. The first component largely describes '
  'purchase activity, with relatively large positive coefficients for frequency, spend and '
  'variety. The notebook includes the component coefficients supporting this interpretation.', keep=True)
table('Table 7. Reduction results from the same starting feature matrix',
      ['Method','Rows before / after','Features before / after'], [
          [row['Reduction method'],f'{row["Rows before"]:,} / {row["Rows after"]:,}',
           f'{row["Features before"]} / {row["Features after"]}'] for row in s['comparison']],
      [155,160,WIDTH-315], numeric=(1,2))
p('Neither method removes customers. Correlation selection preserves named variables, while '
  'PCA achieves a smaller representation at the cost of 6.7448% of standardized variance and '
  'direct business-unit interpretation. A component cannot be described as simply a number '
  'of invoices or pounds spent. Moreover, a low-variance direction may still be commercially '
  'relevant, so explained variance alone does not establish the best representation for a '
  'marketing campaign.')

heading('Task 6  Proximity measures')
p('Twenty distinct customers were sampled without replacement using <b>seed 42</b>. Both '
  'metrics used this identical sample and the four standardized original features from '
  'Task 4, rather than either reduced representation. Customer IDs served exclusively as '
  'labels. The notebook contains both complete 20 x 20 matrices; Table 8 presents their '
  'closest-pair results without reproducing the full matrices in the report.')
table('Table 8. Closest non-self pairs in the reproducible customer sample',
      ['Metric','Customer A','Customer B','Minimum distance'], [
          [row['Metric'],row['Customer A'],row['Customer B'],f'{row["Distance"]:.6f}']
          for row in s['nearest']], [105,105,105,WIDTH-315], numeric=(1,2,3))
p('Minima were searched across 190 unordered pairs in the strict upper triangle, excluding '
  'self-comparisons. A relative tolerance of 1e-9 and absolute tolerance of 1e-12 were used '
  'to check for ties; neither metric produced a tied minimum. Both matrices were symmetric '
  'with zero diagonals. Euclidean distance squares feature differences before summing and '
  'taking a square root, giving a large single-feature gap more relative influence. '
  'Manhattan distance adds absolute gaps linearly. Their different nearest pairs show that '
  'similarity depends on the metric even when preprocessing and inputs are held constant.')
table('Table 9. Original features for customers in the closest pairs',
      ['CustomerID','Recency (days)','Frequency','Spend (GBP)','Variety'], [
          [row['CustomerID'],row['RecencyDays'],row['Frequency'],f'{row["TotalSpend"]:,.2f}',row['ProductVariety']]
          for row in s['pair_original']], [85,110,90,120,WIDTH-405], numeric=(0,1,2,3,4))
p('For the Euclidean pair, customers 14514 and 15264 last purchased 53 and 56 days before '
  'the reference date. Each has one invoice, with spend of GBP 587.09 versus GBP 393.74 and '
  'variety of 29 versus 23 stock codes. These histories are close on the selected activity '
  'measures, but do not establish common demographics or product preferences. The closest '
  'pair within this sample is also not necessarily the closest pair among all customers.')
p('Together, the results show how cleaning defines which purchases enter a profile, aggregation '
  'defines the customer-level measures, and scaling determines their numerical contribution '
  'to proximity. The resulting table is consistent and interpretable, while the comparison '
  'of metrics demonstrates that customer similarity is conditional on these choices rather '
  'than an intrinsic customer label.')

heading('Task 7  Reflection and explainability')
reflection = '''The central challenge was deciding what a useful customer profile should represent. Returns, cancellations and missing identities were not interchangeable defects: each changed the meaning or attribution of a purchase. Repeated invoice numbers also required care because products within one invoice legitimately share that key. I therefore treated exact duplication separately from invoice repetition and distinguished statistically unusual purchases from values unsuitable for a completed-sales definition.

Excluding unidentified customers had the greatest measurable impact at one sequential cleaning step. It removed 37,821 otherwise-valid lines, equivalent to 19.33% of the 195,679-line baseline, representing GBP 569,091.25 of purchase value. Although this improved the reliability of customer attribution, it narrowed the population being described. The final 151,630 lines and 2,851 customers represent identifiable shoppers in the selected window, not every shopper. Inventing identities would have concealed this limitation and risked creating artificial high-value customers from unrelated purchases.

Cleaning also changes the marketing interpretation of value. Completed-sales spend totals GBP 3,142,538.26, but excludes return and cancellation activity. A customer with substantial returns could therefore appear attractive on purchase spend without being equally profitable. The sales filter excluded signed value of GBP -170,917.26; removing negative values increases the remaining sum rather than demonstrating a revenue gain. I would communicate this distinction before the retailer used spending profiles to allocate campaign resources.

I retained plausible positive extremes because an IQR flag alone did not establish that a large wholesale order was wrong. This preserves evidence about large customers while leaving sensitivity to extremes unresolved. Exact deduplication involved a different uncertainty: keeping the first copy limits possible overstatement, but some identical entries may have been legitimate. The three-month window further limits interpretation because observed frequency is not lifetime loyalty, and shoppers absent from the window do not enter the table.

The transformations made these trade-offs visible. Log spend reduced skewness from 19.253 to 0.342, but the distance calculations consistently used the standardized original features. Standardization controls differences in units while remaining affected by extreme customers. Correlation removal retained all four features; PCA compressed them into three components explaining 93.2552% of variance. That compression is numerically useful but makes marketing explanations less direct and can discard commercially relevant low-variance differences. The different Euclidean and Manhattan nearest pairs reinforce that similarity depends on representation and distance definition.

For subsequent segmentation, I would explore K-Means using appropriately transformed and standardized features, with the representation chosen explicitly rather than assumed. Centroids can support understandable descriptions of purchasing activity, although the method favours compact Euclidean groups and is sensitive to extremes. Before campaign use, I would test assignment stability across random initializations and resampled customer sets, comparing agreement on shared customers. Reviewing stability alongside group sizes and centroid profiles would help identify groups that are reproducible and interpretable, rather than accepting a partition solely because one numerical score looks favourable. These decisions should accompany any customer labels so that a campaign team can distinguish recent purchase activity from broader customer value, and avoid treating descriptive similarities as validated market segments.'''
assert 480 <= len(reflection.split()) <= 520, len(reflection.split())
for paragraph in reflection.split('\n\n'):
    p(escape(paragraph), keep=True)

heading('Reference')
p('Chen, D. (2015). <i>Online Retail</i> [Dataset]. UCI Machine Learning Repository. '
  '<link href="https://doi.org/10.24432/C5BW33">https://doi.org/10.24432/C5BW33</link>.')

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawCentredString(A4[0]/2,25,str(doc.page))
    canvas.restoreState()

output = ROOT / 'reports/Data_Preprocessing_Report.pdf'
doc = SimpleDocTemplate(str(output),pagesize=A4,leftMargin=50,rightMargin=50,
                        topMargin=42,bottomMargin=42,title='Data Preprocessing Assignment 1',
                        subject='MSc Data Pre-processing | MDSDF402 | T1-26')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
from pypdf import PdfReader
pages = len(PdfReader(output).pages)
assert pages <= 8
print('Report pages:',pages,'| reflection words:',len(reflection.split()))
