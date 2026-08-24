"""
Cold Chain Integrity & Spoilage Risk Analytics
STEP 2: PYTHON + PANDAS DATA CLEANING

Reads the raw CSVs from /1_Raw_Data, cleans them, engineers analytical
columns, and writes clean CSVs into this folder ready for loading into MySQL.

============================================================================
BUSINESS LOGIC DOCUMENTATION (read this before reading the code)
============================================================================

1. TEMPERATURE VALIDATION
   - Any sensor reading <= -50C or >= 50C is treated as a SENSOR ERROR
     (physically impossible for any of these product categories) and is
     set to NaN rather than being used in analysis. This mirrors how a
     real analyst would flag faulty IoT sensors rather than silently
     trusting them.

2. TEMPERATURE EXCURSION FLAG
   - A shipment is flagged `temperature_excursion_flag = 1` if its cleaned
     recorded_temperature falls outside the product's
     [required_temp_min, required_temp_max] range.
   - `excursion_duration_hours` approximates how long the product was out
     of range. Because we only have one representative recorded reading
     per shipment row (with more granular readings in
     temperature_readings), we estimate exposure duration as the
     proportion of transit_hours during which sensor readings for that
     shipment (from temperature_readings_clean.csv) were out of range.
     If no granular readings are usable, we conservatively assume 25% of
     transit time for a mild excursion and 60% for a severe excursion
     (>= 5C beyond the limit).

3. DELAY FLAG & DELAY DURATION
   - `delay_flag = 1` if actual_delivery_date > expected_delivery_date.
   - `delay_duration_hours` = (actual_delivery_date - expected_delivery_date)
     in hours, floored at 0.
   - Cancelled shipments (no actual delivery date) are excluded from delay
     calculations (delay_flag = NULL) since they never completed transit.

4. SPOILAGE RISK CATEGORY (rule-based, fully transparent — no ML)
   A shipment's risk score is the SUM of the following point values:
     +3  severe temperature excursion (>= 5C beyond the required range)
     +1  mild temperature excursion (< 5C beyond range)
     +2  excursion duration >= 25% of transit time
     +1  delay_flag = 1 AND delay_duration_hours >= 6
     +2  delay_flag = 1 AND delay_duration_hours >= 24
     +1  product category is Seafood or Dairy (more spoilage-sensitive)

   Score -> Category:
     0            -> Low Risk
     1 - 2         -> Medium Risk
     3 - 4         -> High Risk
     5+            -> Critical Risk

   This logic is intentionally simple, explainable, and reproducible from
   fields already present in the data — no machine learning involved.

5. ESTIMATED SPOILAGE QUANTITY
   - Applies an assumed spoilage percentage per risk category to the
     shipped quantity:
       Low Risk: 0%   Medium Risk: 10%   High Risk: 35%   Critical Risk: 75%
   - estimated_spoilage_qty = quantity * spoilage_rate (rounded down)

6. ESTIMATED FINANCIAL LOSS
   - estimated_financial_loss = estimated_spoilage_qty * unit_cost
   - This is a direct, transparent multiplication — no forecasting model.

============================================================================
"""

import numpy as np
import pandas as pd

RAW = "../1_Raw_Data"

# --------------------------------------------------------------------------
# LOAD RAW DATA
# --------------------------------------------------------------------------
products = pd.read_csv(f"{RAW}/products_raw.csv")
suppliers = pd.read_csv(f"{RAW}/suppliers_raw.csv")
routes = pd.read_csv(f"{RAW}/routes_raw.csv")
shipments = pd.read_csv(f"{RAW}/shipments_raw.csv")
temps = pd.read_csv(f"{RAW}/temperature_readings_raw.csv")

print("Raw row counts:", len(products), len(suppliers), len(routes), len(shipments), len(temps))

products = products.drop_duplicates(subset="product_id").copy()
products["product_category"] = (
    products["product_category"].str.strip().str.title()
)
products["product_name"] = products["product_name"].str.strip()
products["unit_cost"] = pd.to_numeric(products["unit_cost"], errors="coerce")
products["required_temp_min"] = pd.to_numeric(products["required_temp_min"], errors="coerce")
products["required_temp_max"] = pd.to_numeric(products["required_temp_max"], errors="coerce")
products = products.dropna(subset=["product_id"])

suppliers = suppliers.drop_duplicates(subset="supplier_id").copy()
suppliers["supplier_name"] = suppliers["supplier_name"].str.strip().str.title()
suppliers["supplier_rating"] = pd.to_numeric(suppliers["supplier_rating"], errors="coerce")
# missing ratings imputed with the median rating (transparent, documented choice)
median_rating = suppliers["supplier_rating"].median()
suppliers["supplier_rating"] = suppliers["supplier_rating"].fillna(median_rating)
suppliers["contract_start_year"] = pd.to_numeric(
    suppliers["contract_start_year"], errors="coerce"
)

routes = routes.drop_duplicates(subset="route_id").copy()
routes["transport_mode"] = routes["transport_mode"].str.strip().str.title()
routes.loc[routes["transport_mode"] == "", "transport_mode"] = "Unknown"
routes["transport_mode"] = routes["transport_mode"].replace("", "Unknown")
routes["transport_mode"] = routes["transport_mode"].fillna("Unknown")

temps["sensor_temperature"] = pd.to_numeric(temps["sensor_temperature"], errors="coerce")
# sensor error bounds: physically implausible for cold-chain perishables
temps.loc[
    (temps["sensor_temperature"] <= -50) | (temps["sensor_temperature"] >= 50),
    "sensor_temperature",
] = np.nan
temps["reading_timestamp"] = pd.to_datetime(temps["reading_timestamp"], errors="coerce")
temps = temps.drop_duplicates(subset="reading_id")
temps_clean = temps.dropna(subset=["sensor_temperature"]).copy()
temps_clean.to_csv("temperature_readings_clean.csv", index=False)

s = shipments.drop_duplicates().copy()

# --- shipment_status standardization ---
s["shipment_status"] = s["shipment_status"].str.strip().str.title()

# --- date parsing: handle mixed YYYY-MM-DD and DD/MM/YYYY formats ---
def parse_mixed_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT


s["shipment_date"] = s["shipment_date"].apply(parse_mixed_date)
s["expected_delivery_date"] = pd.to_datetime(s["expected_delivery_date"], errors="coerce")
s["actual_delivery_date"] = pd.to_datetime(s["actual_delivery_date"], errors="coerce")

# --- numeric fields ---
s["transit_hours"] = pd.to_numeric(s["transit_hours"], errors="coerce")
s["quantity"] = pd.to_numeric(s["quantity"], errors="coerce")
s["unit_cost"] = pd.to_numeric(s["unit_cost"], errors="coerce")
s["recorded_temperature"] = pd.to_numeric(s["recorded_temperature"], errors="coerce")

# invalid quantity (<=0) -> treat as missing, then impute with category median
s.loc[s["quantity"] <= 0, "quantity"] = np.nan

# sensor error bounds on shipment-level recorded temperature
s.loc[
    (s["recorded_temperature"] <= -50) | (s["recorded_temperature"] >= 50),
    "recorded_temperature",
] = np.nan

# --- impute missing numeric values (documented, simple, reproducible) ---
s["transit_hours"] = s["transit_hours"].fillna(s["transit_hours"].median())
s["quantity"] = s["quantity"].fillna(s["quantity"].median())
s["unit_cost"] = s["unit_cost"].fillna(
    s.groupby("product_id")["unit_cost"].transform("median")
)

# --- drop rows with no product / supplier / route reference (data integrity) ---
s = s.dropna(subset=["product_id", "supplier_id", "route_id", "shipment_id"])

# --- merge product requirements needed for downstream logic ---
s = s.merge(
    products[["product_id", "product_category", "required_temp_min", "required_temp_max"]],
    on="product_id",
    how="left",
)

# recorded_temperature missing after sensor-error cleaning -> fill with the
# mean of that shipment's clean temperature_readings if available, else
# fall back to the midpoint of the product's required range (best-available
# estimate, clearly documented rather than silently guessed).
temp_avg_by_shipment = temps_clean.groupby("shipment_id")["sensor_temperature"].mean()
s["recorded_temperature"] = s.apply(
    lambda row: row["recorded_temperature"]
    if pd.notna(row["recorded_temperature"])
    else temp_avg_by_shipment.get(row["shipment_id"], np.nan),
    axis=1,
)
midpoint = (s["required_temp_min"] + s["required_temp_max"]) / 2
s["recorded_temperature"] = s["recorded_temperature"].fillna(midpoint)

is_cancelled = s["shipment_status"] == "Cancelled"

s["delay_duration_hours"] = (
    (s["actual_delivery_date"] - s["expected_delivery_date"]).dt.total_seconds() / 3600
)
s["delay_duration_hours"] = s["delay_duration_hours"].clip(lower=0)
s["delay_flag"] = np.where(
    is_cancelled, np.nan, (s["delay_duration_hours"] > 0).astype(float)
)
s.loc[is_cancelled, "delay_duration_hours"] = np.nan

over = s["recorded_temperature"] - s["required_temp_max"]
under = s["required_temp_min"] - s["recorded_temperature"]
s["deviation_c"] = np.maximum(over, under).clip(lower=0)  # 0 if within range
s["temperature_excursion_flag"] = (s["deviation_c"] > 0).astype(int)
s["excursion_severity"] = np.select(
    [s["deviation_c"] == 0, s["deviation_c"] < 5],
    ["None", "Mild"],
    default="Severe",
)

# excursion duration: use granular temperature_readings where available to
# estimate the fraction of transit time spent out of range; fall back to
# fixed assumptions documented above.
def excursion_duration(row, readings_by_shipment):
    sid = row["shipment_id"]
    if sid in readings_by_shipment.groups:
        grp = readings_by_shipment.get_group(sid)
        tmin, tmax = row["required_temp_min"], row["required_temp_max"]
        out_of_range = ((grp["sensor_temperature"] < tmin) | (grp["sensor_temperature"] > tmax)).mean()
        return round(out_of_range * row["transit_hours"], 1)
    # fallback fixed assumption
    if row["excursion_severity"] == "Severe":
        return round(0.60 * row["transit_hours"], 1)
    elif row["excursion_severity"] == "Mild":
        return round(0.25 * row["transit_hours"], 1)
    return 0.0


readings_by_shipment = temps_clean.groupby("shipment_id")
s["excursion_duration_hours"] = s.apply(
    lambda r: excursion_duration(r, readings_by_shipment), axis=1
)

def risk_score(row):
    score = 0
    if row["excursion_severity"] == "Severe":
        score += 3
    elif row["excursion_severity"] == "Mild":
        score += 1

    transit_h = row["transit_hours"] if row["transit_hours"] else 0
    if transit_h > 0 and (row["excursion_duration_hours"] / transit_h) >= 0.25:
        score += 2

    if row["delay_flag"] == 1:
        if row["delay_duration_hours"] >= 24:
            score += 2
        elif row["delay_duration_hours"] >= 6:
            score += 1

    if row["product_category"] in ("Seafood", "Dairy"):
        score += 1

    return score


s["spoilage_risk_score"] = s.apply(risk_score, axis=1)
s["spoilage_risk_category"] = pd.cut(
    s["spoilage_risk_score"],
    bins=[-1, 0, 2, 4, 100],
    labels=["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
)

spoilage_rate_map = {
    "Low Risk": 0.00,
    "Medium Risk": 0.10,
    "High Risk": 0.35,
    "Critical Risk": 0.75,
}
s["spoilage_rate_applied"] = s["spoilage_risk_category"].astype(str).map(spoilage_rate_map)
s["estimated_spoilage_qty"] = np.floor(s["quantity"] * s["spoilage_rate_applied"]).astype(int)
s["estimated_financial_loss"] = round(s["estimated_spoilage_qty"] * s["unit_cost"], 2)

final_cols = [
    "shipment_id", "product_id", "supplier_id", "route_id",
    "shipment_date", "expected_delivery_date", "actual_delivery_date",
    "shipment_status", "transit_hours", "quantity", "unit_cost",
    "recorded_temperature", "required_temp_min", "required_temp_max",
    "deviation_c", "temperature_excursion_flag", "excursion_severity",
    "excursion_duration_hours", "delay_flag", "delay_duration_hours",
    "spoilage_risk_score", "spoilage_risk_category",
    "estimated_spoilage_qty", "estimated_financial_loss",
]
shipments_clean = s[final_cols].copy()

shipments_clean.to_csv("shipments_clean.csv", index=False)
products.to_csv("products_clean.csv", index=False)
suppliers.to_csv("suppliers_clean.csv", index=False)
routes.to_csv("routes_clean.csv", index=False)

print("\nClean row counts:")
print("  products_clean.csv             ->", len(products))
print("  suppliers_clean.csv            ->", len(suppliers))
print("  routes_clean.csv               ->", len(routes))
print("  shipments_clean.csv            ->", len(shipments_clean))
print("  temperature_readings_clean.csv ->", len(temps))

print("\nSpoilage risk category distribution:")
print(shipments_clean["spoilage_risk_category"].value_counts())
print("\nTotal estimated financial loss: $", round(shipments_clean["estimated_financial_loss"].sum(), 2))
