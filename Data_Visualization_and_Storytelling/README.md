# Data Visualization and Storytelling Assignment 1

This is a separate assignment from Data Preprocessing. The supplied BITS Retail academic
transactions cover full years 2024–2026, including December 2026. Original files in `Data/`
are preserved. Source definitions are in `BITS_Retail_Student_Guide.xlsx`.

## Files

- `notebooks/Retail_Data_Preparation_and_Analysis.ipynb`: executed source inspection, append,
  merges, cleaning, measures, validation and analytical narrative.
- `dashboard/app.py`: editable Streamlit/Plotly dashboard with seven visuals.
- `output/BITS_Retail_Cleaned_Integrated.csv`: 1,310 enriched transaction records.
- `output/Data_Cleaning_Log.csv`: corrections, removals, retained unusual values and checks.
- `reports/Data_Visualization_and_Storytelling_Report.pdf`: six-page report with genuine dashboard screenshots.
- `figures/`: actual browser captures of the dashboard and its seven charts.
- `retail_metrics.py`: small shared financial and aggregation functions.
- `execute_notebook.py`, `build_report.py`, `verify_assignment.py`: reproduction and checks.

## Run locally

Tested on Python 3.14; Python 3.11+ with compatible installed dependencies is appropriate.
From this project directory:

```powershell
python -m pip install -r requirements.txt
python execute_notebook.py notebooks
python -m streamlit run dashboard/app.py --global.developmentMode false
python verify_assignment.py
python build_report.py
```

Alternatively open the notebook in Jupyter, select the installed Python kernel and run all
cells. It works from the project root or `notebooks/` and regenerates both CSV exports.
`build_report.py` uses Arial from Windows Fonts; on another operating system change the two
font paths to an available Unicode font with the rupee glyph. The completed PDF is portable.
The dashboard needs no path editing, environment variables, credentials or online service.
It is locally runnable, not a hosted dashboard link. In the development workspace the running
instance uses port 8502; the default launch command normally uses port 8501.

## Interaction and definitions

Year, region, category and customer-segment filters update all KPIs, charts and tables. Empty
selections show a message; Reset all filters restores everything. Growth compares consecutive
selected years only. Regional insight text uses active filters. The two priorities and connected
story are explicitly labeled as complete-dataset findings and remain fixed under filters.

Currency is INR (₹). GrossSales = Quantity × Unit_Price; DiscountAmount = GrossSales ×
Discount_Pct; NetSales = GrossSales − DiscountAmount; ProductCost = Quantity × Unit_Cost;
Profit = NetSales − ProductCost − Shipping_Cost. Shipping is subtracted once per transaction.
Aggregate margin is summed profit / summed net sales, not average transaction margin. Weighted
discount is summed discount amount / summed gross sales. Orders count distinct Order_ID.
Source_Year provides provenance. Year, Month and YearMonth come from Order_Date. Discount bands
are exactly 0%, (0,10%], (10%,20%] and >20%; only the grouping key is rounded to avoid float artifacts.
Contributions use totals under the same active filters. Negative profit is retained.

## Findings and limitations

Raw counts are 362, 442 and 512 (1,316 appended). Six extra exact copies are removed, leaving
360, 440 and 510. Both master joins match fully and preserve rows. Category aliases are mapped
explicitly. IQR extremes are documented and retained. Full supplied-year scope is used; dates
in the academic dataset are not evidence of verified real-time sales.

Sales grow from ₹7.79m to ₹15.81m while margin improves from 12.14% to 19.09%. West leads
sales/profit, Central is lowest, and North has the highest regional margin. Technology dominates
sales; Computers is the largest subcategory. Discounts above 20% are associated with a pooled
loss. The two actions are margin checks for >20% discounts and a controlled Computers/accessories
pilot. Neither an uplift nor a causal discount effect is inferred. Three years constrain seasonal
inference; costs do not vary over time in the supplied master, and other company expenses are absent.

## Verification and rubric evidence

The notebook was executed in a clean kernel; sample arithmetic and year/region/category totals
reconcile. Financial fixture tests check shipping allocation and ratio-of-sums metrics. All four
filters, combined filtered KPI totals, empty selection and reset were tested with Streamlit AppTest.
Chrome rendered all seven charts and captured genuine screenshots. The PDF pages were rendered
and visually inspected. Task 1 maps the five questions; Task 2 provides integration and cleaning;
Tasks 3–4 are evidenced by the interactive visuals and design discussion; Task 5 connects three
findings; Task 6 gives exactly two priorities with benefits and validation cautions.
