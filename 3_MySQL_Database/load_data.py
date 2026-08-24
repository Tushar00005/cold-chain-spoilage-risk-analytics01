"""
Cold Chain Integrity & Spoilage Risk Analytics
STEP 3b: LOAD CLEANED DATA INTO MYSQL

Loads the cleaned CSVs produced by /2_Python_Pandas_Cleaning/clean_data.py
into the MySQL database created by schema.sql.

Requirements (install once):
    pip install mysql-connector-python pandas

Usage:
    python load_data.py --host localhost --user root --password YOURPASS

The database and tables must already exist (run schema.sql first, e.g.:
    mysql -u root -p < schema.sql
).

Load order respects foreign keys:
    products -> suppliers -> routes -> shipments -> temperature_readings
"""

import argparse
import math

import mysql.connector
import pandas as pd

CLEAN_DIR = "../2_Python_Pandas_Cleaning"


def clean_nan(row):
    """Convert pandas NaN/NaT to None so MySQL receives proper NULLs."""
    return [None if (isinstance(v, float) and math.isnan(v)) or pd.isna(v) else v for v in row]


def load_table(cursor, df, table_name, columns):
    placeholders = ", ".join(["%s"] * len(columns))
    col_list = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"
    rows = [clean_nan(r) for r in df[columns].itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    print(f"  Loaded {len(rows)} rows into {table_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="cold_chain_analytics")
    args = parser.parse_args()

    conn = mysql.connector.connect(
        host=args.host, user=args.user, password=args.password, database=args.database
    )
    cursor = conn.cursor()

    products = pd.read_csv(f"{CLEAN_DIR}/products_clean.csv")
    suppliers = pd.read_csv(f"{CLEAN_DIR}/suppliers_clean.csv")
    routes = pd.read_csv(f"{CLEAN_DIR}/routes_clean.csv")
    shipments = pd.read_csv(f"{CLEAN_DIR}/shipments_clean.csv")
    temps = pd.read_csv(f"{CLEAN_DIR}/temperature_readings_clean.csv")

    print("Loading data into MySQL...")
    load_table(
        cursor, products, "products",
        ["product_id", "product_name", "product_category", "required_temp_min",
         "required_temp_max", "unit_cost", "shelf_life_hours"],
    )
    load_table(
        cursor, suppliers, "suppliers",
        ["supplier_id", "supplier_name", "supplier_country", "supplier_rating",
         "contract_start_year"],
    )
    load_table(
        cursor, routes, "routes",
        ["route_id", "origin", "destination", "distance_km", "transport_mode"],
    )
    load_table(
        cursor, shipments, "shipments",
        ["shipment_id", "product_id", "supplier_id", "route_id", "shipment_date",
         "expected_delivery_date", "actual_delivery_date", "shipment_status",
         "transit_hours", "quantity", "unit_cost", "recorded_temperature",
         "required_temp_min", "required_temp_max", "deviation_c",
         "temperature_excursion_flag", "excursion_severity",
         "excursion_duration_hours", "delay_flag", "delay_duration_hours",
         "spoilage_risk_score", "spoilage_risk_category",
         "estimated_spoilage_qty", "estimated_financial_loss"],
    )
    load_table(
        cursor, temps, "temperature_readings",
        ["reading_id", "shipment_id", "reading_timestamp", "sensor_temperature", "sensor_id"],
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Done. All tables loaded into MySQL database:", args.database)


if __name__ == "__main__":
    main()
