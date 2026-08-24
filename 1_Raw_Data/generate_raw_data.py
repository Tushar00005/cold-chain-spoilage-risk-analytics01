"""
Cold Chain Integrity & Spoilage Risk Analytics
STEP 1: RAW DATA GENERATION

This script generates realistic, intentionally messy raw datasets that simulate
what a cold-chain logistics company's operational systems would actually export:
- Missing values
- Duplicate records
- Invalid temperatures (sensor errors, e.g. -999, 999)
- Temperature excursions (readings outside required range)
- Delayed deliveries
- Inconsistent categorical text ("Dairy" vs "dairy " vs "DAIRY")
- Inconsistent date formats
- A few negative/zero quantities and unit costs (data entry errors)

Only Python + Pandas are used. No external data sources or APIs are called;
all data is synthetically generated with Python's built-in `random` module so
the project is fully self-contained and reproducible.

Output (raw, uncleaned) CSVs are written to this folder:
    products_raw.csv
    suppliers_raw.csv
    routes_raw.csv
    shipments_raw.csv
    temperature_readings_raw.csv
"""

import random
import string
from datetime import datetime, timedelta

import pandas as pd

random.seed(42)

product_catalog = [
    ("P001", "Whole Milk 1L", "Dairy", 2, 4),
    ("P002", "Greek Yogurt", "Dairy", 2, 4),
    ("P003", "Cheddar Cheese", "Dairy", 2, 6),
    ("P004", "Butter Block", "Dairy", 2, 6),
    ("P005", "Fresh Chicken Breast", "Meat", 0, 4),
    ("P006", "Ground Beef", "Meat", 0, 4),
    ("P007", "Pork Chops", "Meat", 0, 4),
    ("P008", "Lamb Cuts", "Meat", 0, 4),
    ("P009", "Atlantic Salmon", "Seafood", -1, 2),
    ("P010", "Shrimp (Frozen)", "Seafood", -18, -15),
    ("P011", "Tuna Steaks", "Seafood", -1, 2),
    ("P012", "Strawberries", "Fruits", 0, 4),
    ("P013", "Blueberries", "Fruits", 0, 4),
    ("P014", "Bananas", "Fruits", 13, 15),
    ("P015", "Grapes", "Fruits", 0, 4),
    ("P016", "Lettuce", "Vegetables", 0, 4),
    ("P017", "Spinach", "Vegetables", 0, 4),
    ("P018", "Broccoli", "Vegetables", 0, 4),
    ("P019", "Tomatoes", "Vegetables", 8, 12),
    ("P020", "Mushrooms", "Vegetables", 0, 4),
]

products_rows = []
for pid, name, cat, tmin, tmax in product_catalog:
    unit_cost = round(random.uniform(1.5, 25.0), 2)
    cat_display = cat
    if random.random() < 0.2:
        cat_display = random.choice([cat.upper(), cat.lower(), f" {cat} "])
    row = {
        "product_id": pid,
        "product_name": name,
        "product_category": cat_display,
        "required_temp_min": tmin,
        "required_temp_max": tmax,
        "unit_cost": unit_cost,
        "shelf_life_hours": random.choice([48, 72, 96, 120, 168, 240]),
    }
    products_rows.append(row)

products_df = pd.DataFrame(products_rows)
products_df = pd.concat([products_df, products_df.iloc[[2, 9]]], ignore_index=True)
products_df.to_csv("products_raw.csv", index=False)

supplier_names = [
    "Fresh Valley Farms", "Arctic Ocean Seafoods", "Green Pasture Dairy",
    "Prime Cut Meats Co", "Sunrise Produce Ltd", "Coastal Catch Exports",
    "Highland Dairy Group", "Meadow Fresh Supplies", "BlueFin Seafood Traders",
    "Golden Harvest Farms",
]
suppliers_rows = []
for i, name in enumerate(supplier_names, start=1):
    sid = f"S{i:03d}"
    row = {
        "supplier_id": sid,
        "supplier_name": name if random.random() > 0.1 else name.upper(),
        "supplier_country": random.choice(
            ["USA", "Canada", "Mexico", "Netherlands", "India", "Chile", "Vietnam"]
        ),
        "supplier_rating": random.choice([None, 3, 4, 5, 2, 5, 4, 3]),  # some missing
        "contract_start_year": random.choice([2018, 2019, 2020, 2021, 2022, ""]),
    }
    suppliers_rows.append(row)

suppliers_df = pd.DataFrame(suppliers_rows)
suppliers_df.to_csv("suppliers_raw.csv", index=False)

cities = [
    "Chicago, USA", "Los Angeles, USA", "New York, USA", "Toronto, Canada",
    "Mexico City, Mexico", "Rotterdam, Netherlands", "Mumbai, India",
    "Santiago, Chile", "Ho Chi Minh City, Vietnam", "Miami, USA",
    "Dallas, USA", "Vancouver, Canada", "Atlanta, USA", "Seattle, USA",
]

routes_rows = []
route_id_counter = 1
for origin in cities:
    for _ in range(2):
        dest = random.choice([c for c in cities if c != origin])
        rid = f"R{route_id_counter:03d}"
        route_id_counter += 1
        distance_km = random.randint(300, 9000)
        routes_rows.append(
            {
                "route_id": rid,
                "origin": origin,
                "destination": dest,
                "distance_km": distance_km,
                "transport_mode": random.choice(
                    ["Refrigerated Truck", "Reefer Ship", "Air Cargo", "reefer truck", ""]
                ),
            }
        )

routes_df = pd.DataFrame(routes_rows)
routes_df.to_csv("routes_raw.csv", index=False)

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


start_range = datetime(2024, 1, 1)
end_range = datetime(2024, 12, 31)

statuses = ["Delivered", "Delivered", "Delivered", "In Transit", "Cancelled", "delivered"]

shipments_rows = []
n_shipments = 1500
for i in range(1, n_shipments + 1):
    sid = f"SHP{i:05d}"
    prod = random.choice(product_catalog)
    pid, pname, cat, tmin, tmax = prod
    supplier = random.choice(suppliers_rows)["supplier_id"]
    route = random.choice(routes_rows)
    ship_date = random_date(start_range, end_range)

    base_transit_hours = max(4, route["distance_km"] / 60)
    transit_hours = round(base_transit_hours * random.uniform(0.8, 1.6), 1)

    expected_delivery = ship_date + timedelta(hours=base_transit_hours * random.uniform(0.95, 1.15))
    delay_factor = random.choices([1.0, 1.1, 1.3, 1.6, 2.2], weights=[55, 20, 12, 8, 5])[0]
    actual_delivery = ship_date + timedelta(hours=transit_hours * delay_factor)

    roll = random.random()
    if roll < 0.65:
        recorded_temp = round(random.uniform(tmin, tmax), 1)
    elif roll < 0.85:
        recorded_temp = round(random.uniform(tmax, tmax + 6), 1) if random.random() < 0.5 else round(
            random.uniform(tmin - 6, tmin), 1
        )
    elif roll < 0.97:
        recorded_temp = round(random.uniform(tmax + 6, tmax + 15), 1)
    else:
        recorded_temp = random.choice([-999, 999, None])

    quantity = random.choice([50, 100, 150, 200, 250, 300, 400, 500])
    if random.random() < 0.02:
        quantity = random.choice([-50, 0])

    unit_cost = next(p["unit_cost"] for p in products_rows if p["product_id"] == pid)

    status = random.choice(statuses)

    row = {
        "shipment_id": sid,
        "product_id": pid,
        "supplier_id": supplier,
        "route_id": route["route_id"],
        "shipment_date": ship_date.strftime("%Y-%m-%d") if random.random() > 0.05 else ship_date.strftime("%d/%m/%Y"),
        "expected_delivery_date": expected_delivery.strftime("%Y-%m-%d %H:%M:%S"),
        "actual_delivery_date": actual_delivery.strftime("%Y-%m-%d %H:%M:%S") if status != "Cancelled" else "",
        "transit_hours": transit_hours,
        "quantity": quantity,
        "unit_cost": unit_cost,
        "recorded_temperature": recorded_temp,
        "shipment_status": status,
    }
    shipments_rows.append(row)

shipments_df = pd.DataFrame(shipments_rows)

for col, frac in [("transit_hours", 0.01), ("unit_cost", 0.01), ("quantity", 0.005)]:
    idx = shipments_df.sample(frac=frac, random_state=1).index
    shipments_df.loc[idx, col] = None

dup_rows = shipments_df.sample(15, random_state=2)
shipments_df = pd.concat([shipments_df, dup_rows], ignore_index=True)

shipments_df.to_csv("shipments_raw.csv", index=False)

temp_rows = []
reading_id = 1
for _, srow in shipments_df.drop_duplicates(subset="shipment_id").iterrows():
    n_readings = random.randint(2, 6)
    prod = next(p for p in product_catalog if p[0] == srow["product_id"])
    tmin, tmax = prod[3], prod[4]
    base_ship_date = srow["shipment_date"]
    try:
        date_format = "%d/%m/%Y" if "/" in str(base_ship_date) else "%Y-%m-%d"
        base_dt = pd.to_datetime(base_ship_date, format=date_format, errors="coerce")
    except Exception:
        base_dt = datetime(2024, 1, 1)
    if pd.isna(base_dt):
        base_dt = datetime(2024, 1, 1)

    for r in range(n_readings):
        roll = random.random()
        if roll < 0.75:
            temp = round(random.uniform(tmin, tmax), 1)
        elif roll < 0.93:
            temp = round(random.uniform(tmax, tmax + 8), 1)
        else:
            temp = random.choice([-999, 999, None])
        ts = base_dt + timedelta(hours=random.uniform(0, 48))
        temp_rows.append(
            {
                "reading_id": f"T{reading_id:06d}",
                "shipment_id": srow["shipment_id"],
                "reading_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "sensor_temperature": temp,
                "sensor_id": f"SEN{random.randint(100,199)}",
            }
        )
        reading_id += 1

temp_df = pd.DataFrame(temp_rows)
temp_df.to_csv("temperature_readings_raw.csv", index=False)

print("Raw data generated:")
print(f"  products_raw.csv             -> {len(products_df)} rows")
print(f"  suppliers_raw.csv            -> {len(suppliers_df)} rows")
print(f"  routes_raw.csv               -> {len(routes_df)} rows")
print(f"  shipments_raw.csv            -> {len(shipments_df)} rows")
print(f"  temperature_readings_raw.csv -> {len(temp_df)} rows")
