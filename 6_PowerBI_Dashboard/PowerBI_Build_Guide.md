# Power BI Dashboard — Build Guide

> **Environment note:** This sandbox cannot run Power BI Desktop (Windows
> application), so no `.pbix` file could be produced here. This folder gives
> you everything needed to build the dashboard yourself in ~15 minutes:
> Power-BI-ready CSV exports (star schema), the exact relationships to draw,
> every DAX measure, and the page-by-page layout. A wireframe preview image
> (`dashboard_mockup.png` / see chat) shows the intended look.

## 1. Data to import

Import these CSVs (**Get Data → Text/CSV**), or better, connect Power BI
directly to your MySQL database (**Get Data → MySQL database**) once
`load_data.py` has populated it — either source works with the model below.

| File | Role |
|---|---|
| `fact_shipments.csv` | Fact table (1 row = 1 shipment) |
| `dim_products.csv` | Product dimension |
| `dim_suppliers.csv` | Supplier dimension |
| `dim_routes.csv` | Route dimension |
| `dim_date.csv` | Date dimension (Jan–Dec 2024, mark as Date Table) |

## 2. Relationships (Model view)

```
dim_products (product_id)   1 ──── * fact_shipments (product_id)
dim_suppliers (supplier_id) 1 ──── * fact_shipments (supplier_id)
dim_routes (route_id)       1 ──── * fact_shipments (route_id)
dim_date (date)              1 ──── * fact_shipments (shipment_date)
```

All relationships: **single direction, one-to-many**, dimension → fact.
In `dim_date`, right-click the table → **Mark as date table** → `date` column.

## 3. DAX Measures

Create these in a new measure table called `_Measures`:

```DAX
Total Shipments = COUNTROWS(fact_shipments)

On-Time Delivery % =
DIVIDE(
    CALCULATE(COUNTROWS(fact_shipments), fact_shipments[delay_flag] = 0),
    CALCULATE(COUNTROWS(fact_shipments), NOT ISBLANK(fact_shipments[delay_flag]))
)

Temperature Compliance % =
DIVIDE(
    CALCULATE(COUNTROWS(fact_shipments), fact_shipments[temperature_excursion_flag] = 0),
    COUNTROWS(fact_shipments)
)

Spoilage Risk % =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_shipments),
        fact_shipments[spoilage_risk_category] IN {"High Risk","Critical Risk"}
    ),
    COUNTROWS(fact_shipments)
)

Estimated Financial Loss = SUM(fact_shipments[estimated_financial_loss])

Average Transit Time (hrs) = AVERAGE(fact_shipments[transit_hours])

Delayed Shipments = CALCULATE(COUNTROWS(fact_shipments), fact_shipments[delay_flag] = 1)

Temperature Violations = SUM(fact_shipments[temperature_excursion_flag])

Avg Loss per Shipment = DIVIDE([Estimated Financial Loss], [Total Shipments])

Critical Risk Shipments =
CALCULATE(COUNTROWS(fact_shipments), fact_shipments[spoilage_risk_category] = "Critical Risk")

MoM Loss Change % =
VAR CurrMonth = [Estimated Financial Loss]
VAR PrevMonth = CALCULATE([Estimated Financial Loss], DATEADD(dim_date[date], -1, MONTH))
RETURN DIVIDE(CurrMonth - PrevMonth, PrevMonth)
```

## 4. Page layout (3 pages)

### Page 1 — Executive Overview
- **KPI cards** (top row): Total Shipments · On-Time Delivery % · Temperature
  Compliance % · Spoilage Risk % · Estimated Financial Loss · Average
  Transit Time
- **Line chart**: `Estimated Financial Loss` and `Total Shipments` by
  `dim_date[month_year]` (shipment trend)
- **Donut chart**: shipments by `spoilage_risk_category`
- **Bar chart**: `Estimated Financial Loss` by `dim_products[product_category]`
- **Slicers panel** (left): Date range, Product Category, Supplier, Origin,
  Destination, Shipment Status, Spoilage Risk Category

### Page 2 — Temperature & Delay Risk
- **Bar chart**: Temperature violation rate by product category
- **Bar chart**: Delay rate by transport mode (`dim_routes[transport_mode]`)
- **Scatter/clustered column**: Delay bucket (On Time / <6h / 6-24h / 24h+)
  vs % High/Critical risk shipments (illustrates the delay→spoilage
  relationship)
- **Table**: Top 10 highest-risk routes (route, excursion rate %, avg
  transit hours, total loss) — sort descending by excursion rate
- **Matrix**: Product category × Spoilage risk category, values = shipment
  count, conditional-formatted (heatmap)

### Page 3 — Supplier & Route Performance
- **Table/matrix**: Supplier scorecard — supplier name, total shipments,
  temperature violation rate %, delay rate %, total estimated loss, rank
  (use DAX `RANKX` or the SQL `loss_rank` column if importing from MySQL)
- **Bar chart**: Total estimated loss by supplier (descending)
- **Map visual** (if available) or bar chart: Total loss by origin city
- **Card**: worst-performing supplier and route, driven by bookmarks/top-N
  filter

## 5. Suggested conditional formatting

- Spoilage Risk Category color scale: Low Risk = green, Medium Risk =
  yellow, High Risk = orange, Critical Risk = red — apply consistently
  across every visual using this field (Format → Data colors → Conditional
  formatting, or a disconnected color-mapping table).
- KPI cards: add a red/green indicator when `Temperature Compliance %` <
  90% or `On-Time Delivery %` < 85% using data bars / conditional font
  color.

## 6. Filters/Slicers

Add a slicer panel (Page 1, reused via **Sync Slicers** across all pages)
with:
- `dim_date[date]` (between)
- `dim_products[product_category]`
- `dim_suppliers[supplier_name]`
- `dim_routes[origin]`
- `dim_routes[destination]`
- `fact_shipments[shipment_status]`
- `fact_shipments[spoilage_risk_category]`
