"""
This sandbox environment does not have a MySQL server available, so the
analysis_queries.sql cannot be executed live here. To let you validate the
logic and see representative numbers, this script recomputes the SAME
business questions using Pandas on shipments_clean.csv (the exact data that
load_data.py would insert into MySQL). Once you run schema.sql + load_data.py
against a real MySQL instance, analysis_queries.sql will return the same
figures (row-level ordering/formatting may differ slightly).

Output -> sql_results_preview.md
"""
import pandas as pd

CLEAN_DIR = "../2_Python_Pandas_Cleaning"
shipments = pd.read_csv(f"{CLEAN_DIR}/shipments_clean.csv")
products = pd.read_csv(f"{CLEAN_DIR}/products_clean.csv")
suppliers = pd.read_csv(f"{CLEAN_DIR}/suppliers_clean.csv")
routes = pd.read_csv(f"{CLEAN_DIR}/routes_clean.csv")

s = shipments.merge(products, on="product_id", suffixes=("", "_p"))
s = s.merge(suppliers, on="supplier_id")
s = s.merge(routes, on="route_id")

out = []
out.append("# SQL Analysis Results Preview (computed via Pandas)\n")
out.append("_Sandbox has no live MySQL server; figures below mirror what "
            "`analysis_queries.sql` returns once run against a real MySQL "
            "instance loaded via `load_data.py`._\n")

total = len(shipments)
delivered = (shipments.shipment_status == "Delivered").sum()
out.append("## Q1. Shipment volume & status")
out.append(f"- Total shipments: **{total}**")
out.append(f"- Delivered: **{delivered}** ({delivered/total:.1%})")
out.append(f"- In Transit: **{(shipments.shipment_status=='In Transit').sum()}**")
out.append(f"- Cancelled: **{(shipments.shipment_status=='Cancelled').sum()}**\n")

delivered_df = shipments[shipments.shipment_status == "Delivered"]
delayed = (delivered_df.delay_flag == 1).sum()
on_time = (delivered_df.delay_flag == 0).sum()
out.append("## Q2. On-time vs delayed")
out.append(f"- On time: **{on_time}**")
out.append(f"- Delayed: **{delayed}** ({delayed/(on_time+delayed):.1%})")
out.append(f"- Avg delay when delayed: **{delivered_df.loc[delivered_df.delay_flag==1,'delay_duration_hours'].mean():.1f} hrs**\n")

viol = shipments.temperature_excursion_flag.sum()
out.append("## Q3. Temperature compliance")
out.append(f"- Violations: **{viol}** ({viol/total:.1%})")
out.append(f"- Compliance rate: **{1-viol/total:.1%}**")
out.append(f"- Avg deviation: **{shipments.deviation_c.mean():.2f} C**\n")

out.append("## Q4. Spoilage risk distribution & loss")
grp = shipments.groupby("spoilage_risk_category", observed=True).agg(
    shipment_count=("shipment_id", "count"),
    total_spoiled_units=("estimated_spoilage_qty", "sum"),
    total_loss=("estimated_financial_loss", "sum"),
).reset_index()
out.append(grp.to_markdown(index=False))
out.append("")

out.append("\n## Q5. Loss by product category")
grp5 = s.groupby("product_category_p" if "product_category_p" in s.columns else "product_category").agg(
    total_shipments=("shipment_id", "count"),
    total_loss=("estimated_financial_loss", "sum"),
).sort_values("total_loss", ascending=False).reset_index()
out.append(grp5.to_markdown(index=False))

out.append("\n## Q6. Supplier performance (top 10 by loss)")
grp6 = s.groupby("supplier_name").agg(
    total_shipments=("shipment_id", "count"),
    violation_rate=("temperature_excursion_flag", "mean"),
    total_loss=("estimated_financial_loss", "sum"),
).sort_values("total_loss", ascending=False).head(10).reset_index()
grp6["violation_rate"] = (grp6["violation_rate"] * 100).round(2)
out.append(grp6.to_markdown(index=False))

out.append("\n## Q8. Route performance (top 10 by excursion rate, min 5 shipments)")
grp8 = s.groupby(["route_id", "origin", "destination"]).agg(
    total_shipments=("shipment_id", "count"),
    excursion_rate=("temperature_excursion_flag", "mean"),
    total_loss=("estimated_financial_loss", "sum"),
).reset_index()
grp8 = grp8[grp8.total_shipments >= 5].sort_values("excursion_rate", ascending=False).head(10)
grp8["excursion_rate"] = (grp8["excursion_rate"] * 100).round(2)
out.append(grp8.to_markdown(index=False))

out.append("\n## Q9. Top 10 highest-loss products")
grp9 = s.groupby(["product_id", "product_name"]).agg(
    total_shipments=("shipment_id", "count"),
    total_spoiled_units=("estimated_spoilage_qty", "sum"),
    total_loss=("estimated_financial_loss", "sum"),
).sort_values("total_loss", ascending=False).head(10).reset_index()
out.append(grp9.to_markdown(index=False))

out.append("\n## Q11. Delay vs spoilage risk")
def bucket(row):
    if row.delay_flag == 0:
        return "On Time"
    if row.delay_duration_hours < 6:
        return "Delayed < 6h"
    if row.delay_duration_hours < 24:
        return "Delayed 6-24h"
    return "Delayed 24h+"
tmp = shipments[shipments.delay_flag.notna()].copy()
tmp["delay_bucket"] = tmp.apply(bucket, axis=1)
grp11 = tmp.groupby("delay_bucket").apply(
    lambda d: pd.Series({
        "shipments": len(d),
        "high_critical_risk_pct": round(100*d.spoilage_risk_category.isin(["High Risk","Critical Risk"]).mean(),2),
        "avg_loss_per_shipment": round(d.estimated_financial_loss.mean(),2),
    }), include_groups=False
).reindex(["On Time","Delayed < 6h","Delayed 6-24h","Delayed 24h+"])
out.append(grp11.to_markdown())

with open("sql_results_preview.md", "w") as f:
    f.write("\n".join(str(x) for x in out))

print("Preview written to sql_results_preview.md")
print(f"\nTotal estimated financial loss across all shipments: ${shipments.estimated_financial_loss.sum():,.2f}")
