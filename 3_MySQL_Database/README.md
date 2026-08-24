# MySQL Database — Setup Instructions

> **Sandbox note:** the environment used to build this project has no MySQL
> server installed and no network access, so `schema.sql` and `load_data.py`
> could not be executed live here. Both are complete and ready to run against
> any real MySQL 8.x instance. Section 4 (`/4_SQL_Analysis`) includes a
> Pandas-computed preview of the expected query results so you can sanity
> check the numbers before/without a live server.

## Steps to reproduce

1. Install MySQL 8.x locally (or use any managed MySQL instance).
2. Create the schema and tables:
   ```bash
   mysql -u root -p < schema.sql
   ```
3. Install the Python MySQL connector:
   ```bash
   pip install mysql-connector-python
   ```
4. Load the cleaned data (produced by `../2_Python_Pandas_Cleaning/clean_data.py`):
   ```bash
   python load_data.py --host localhost --user root --password YOURPASS
   ```
5. Run the business analysis queries:
   ```bash
   mysql -u root -p cold_chain_analytics < ../4_SQL_Analysis/analysis_queries.sql
   ```
6. Connect Power BI directly to `cold_chain_analytics` (Get Data → MySQL
   database) or import the CSV exports in `/6_PowerBI_Dashboard`.

## Entity-relationship summary

```
products (1) ───< shipments (*) >─── suppliers (1)
                        │
                        └──< routes (1)

shipments (1) ───< temperature_readings (*)
```

- `products.product_id` → `shipments.product_id`
- `suppliers.supplier_id` → `shipments.supplier_id`
- `routes.route_id` → `shipments.route_id`
- `shipments.shipment_id` → `temperature_readings.shipment_id`
