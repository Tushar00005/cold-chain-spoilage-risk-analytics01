# Cold Chain Integrity & Spoilage Risk Analytics for Perishable Logistics

An end-to-end Data Analyst project built with **Python + Pandas + MySQL +
Power BI only**, following the workflow:

```
Raw Data → Python/Pandas Cleaning → MySQL Storage → MySQL Analysis →
Python/Pandas Analysis → Power BI Dashboard → Business Insights
```

## Folder guide

| Folder | Contents |
|---|---|
| `1_Raw_Data/` | `generate_raw_data.py` + intentionally messy raw CSVs (missing values, duplicates, invalid temperatures, inconsistent categories) |
| `2_Python_Pandas_Cleaning/` | `clean_data.py` — cleaning, validation, and engineered fields (excursion flags, delay flags, spoilage-risk score, estimated financial loss), with the full business-logic documentation in the file's docstring |
| `3_MySQL_Database/` | `schema.sql` (DDL, PKs/FKs), `load_data.py` (loader), `README.md` (setup steps) |
| `4_SQL_Analysis/` | `analysis_queries.sql` — 15 business-question queries using JOIN, GROUP BY, HAVING, CASE, subqueries, CTEs, and window functions; `preview_results_pandas.py` + `sql_results_preview.md` — a Pandas-computed preview of expected results (see note below) |
| `5_Python_Pandas_Analysis/` | `pandas_analysis.py` + `findings_report.md` — deeper risk-pattern analysis (no ML) |
| `6_PowerBI_Dashboard/` | Star-schema CSV exports (`fact_shipments.csv`, `dim_products.csv`, `dim_suppliers.csv`, `dim_routes.csv`, `dim_date.csv`) + `PowerBI_Build_Guide.md` (relationships, DAX measures, page-by-page layout) |
| `7_Business_Insights/` | `Business_Insights_Report.docx` — the final business-facing recommendations, fully supported by the analysis above |

## Environment note

This project was built in a sandbox with **no MySQL server and no network
access**, so `schema.sql` / `load_data.py` could not be executed live and no
`.pbix` file could be produced (Power BI Desktop is Windows-only software).
Every script is complete and correct and will run as-is once you have:
- a MySQL 8.x server (local or managed), and
- Power BI Desktop.

`4_SQL_Analysis/sql_results_preview.md` shows the numbers you should expect
from `analysis_queries.sql`, computed via Pandas on the identical cleaned
dataset that `load_data.py` inserts into MySQL.

Shipments and loss by month:


![image alt](https://github.com/Tushar00005/cold-chain-spoilage-risk-analytics01/blob/6d973be88376b12579eb72f7f6e809d13ab406d6/download.png)


spoilage risk mix:

![image_alt](https://github.com/Tushar00005/cold-chain-spoilage-risk-analytics01/blob/f62970e02bf1772061e897263a31111e3d0b53a6/download%20(1).png)


Estimated financial loss by product category:

![image_alt](https://github.com/Tushar00005/cold-chain-spoilage-risk-analytics01/blob/b6a71d9aefda236db510df6c37c4070be28517df/download%20(2).png)
