# Data Preprocessing Assignment 1

MSc | MDSDF402 | T1-26

This assignment prepares customer features from UCI Online Retail invoice lines and compares
customer similarity. All countries are included for 1 September to 30 November 2011 inclusive.
The official question paper and source workbook remain in their original locations:

- `Data/Assignment 1 - Data Preprocessing T1-26.docx`
- `Data/online+retail/Online Retail.xlsx`

Source: Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository.
https://doi.org/10.24432/C5BW33

## Submission files

- `notebooks/Data_Preprocessing_Assignment_1.ipynb`: executed analysis for all seven tasks.
- `reports/Data_Preprocessing_Report.pdf`: seven-page report with a 508-word reflection.
- `output/cleaned_customer_features.csv`: 2,851 customer rows and seven columns.

`figures/` contains three charts used by the analysis. The small `output/analysis_summary.json`
is retained because `build_report.py` uses it to regenerate report tables from computed results.
It contains no source hashes, version metadata or generated essay.

## Run the analysis

Install the dependencies in `requirements.txt`, then run the notebook from top to bottom in a
Python kernel. It works from either the project root or `notebooks/`.

Alternatively, from the project root:

```powershell
python -m pip install -r requirements.txt
python execute_notebook.py notebooks
python build_report.py
```

The execution helper starts a fresh kernel and saves outputs. The report builder applies simple
academic formatting to the computed results and the written reflection. In the managed workspace,
installed dependencies are available in the parent `.assignment_deps` directory through `PYTHONPATH`;
this local setup is not required when the dependencies are installed in a normal Python environment.

## Customer features

| Column | Meaning |
|---|---|
| CustomerID | Customer identifier; excluded from numerical calculations |
| RecencyDays | Calendar days from last purchase date to 1 December 2011 |
| Frequency | Distinct invoice count in the window |
| TotalSpend | Completed-sales Quantity x UnitPrice, in GBP |
| ProductVariety | Number of distinct StockCode values |
| Log1pTotalSpend | Natural logarithm of 1 + TotalSpend |
| RecencyBand | Recent: 1-30 days; Warm: 31-60 days; Lapsed: 61-91 days |

## Main decisions and results

Tasks 1 and 2 use the unchanged 195,679-line baseline. Cleaning excludes the union of cancellation,
non-positive quantity and non-positive price flags, then unknown customer IDs, then exact duplicate
copies. This leaves 151,630 lines. Descriptions are trimmed; identifier case is preserved. Positive
statistical outliers are retained because unusual wholesale purchases are not automatically errors.
Completed-sales spend is not net revenue after returns. Duplicate removal may discard legitimate
identical entries because no unique line key is available.

One StandardScaler is fitted to the four original numeric features and reused for both reduction
and proximity analysis. Correlation removal at >0.85 retains every feature and therefore performs
no reduction. PCA retains three components and 93.2552% of variance. A 20-customer sample with seed
42 gives Euclidean nearest pair 14514/15264 and Manhattan nearest pair 17221/16012, with no ties.
Both complete distance matrices remain visible in the notebook. No clustering model is fitted.

## Revision checks

The notebook is written as my answers to the seven tasks, with a linked contents guide, numbered
question parts, labels before tables and charts, and interpretations beside the relevant results.
The full reflection appears in both the notebook and report. The revised notebook passed clean execution. Customer features were independently recalculated
from the workbook and the CSV was preserved byte-for-byte. Both displayed matrices, nearest pairs,
transformations and PCA variance were checked. All seven PDF pages were rendered and visually
inspected. The three-month window, excluded anonymous shoppers and retained extreme customers
remain interpretation limits, discussed in the reflection.
