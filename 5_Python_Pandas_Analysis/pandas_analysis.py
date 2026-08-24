"""
Cold Chain Integrity & Spoilage Risk Analytics
STEP 5: PYTHON + PANDAS ANALYTICAL ANALYSIS

Goes beyond the SQL aggregate reporting to surface risk PATTERNS using only
Pandas descriptive statistics and group-by comparisons (no machine learning /
predictive modeling of any kind, per project scope).

Writes findings to findings_report.md
"""
import pandas as pd

CLEAN_DIR = "../2_Python_Pandas_Cleaning"
shipments = pd.read_csv(f"{CLEAN_DIR}/shipments_clean.csv")
products = pd.read_csv(f"{CLEAN_DIR}/products_clean.csv")
suppliers = pd.read_csv(f"{CLEAN_DIR}/suppliers_clean.csv")
routes = pd.read_csv(f"{CLEAN_DIR}/routes_clean.csv")

s = shipments.merge(products, on="product_id").merge(suppliers, on="supplier_id").merge(routes, on="route_id")

lines = ["# Python + Pandas Analytical Findings\n"]

lines.append("## 1. Temperature-Risk Patterns by Product Category")
cat_risk = s.groupby("product_category").agg(
    shipments=("shipment_id", "count"),
    violation_rate_pct=("temperature_excursion_flag", lambda x: round(100*x.mean(), 2)),
    avg_deviation_c=("deviation_c", lambda x: round(x.mean(), 2)),
    critical_risk_pct=("spoilage_risk_category", lambda x: round(100*(x == "Critical Risk").mean(), 2)),
).sort_values("violation_rate_pct", ascending=False)
lines.append(cat_risk.to_markdown())
worst_cat = cat_risk.index[0]
lines.append(f"\n**Finding:** `{worst_cat}` has the highest temperature-violation rate "
             f"({cat_risk.iloc[0]['violation_rate_pct']}%), making it the category needing "
             f"the tightest cold-chain control.\n")

lines.append("## 2. Delay-Risk Patterns by Transport Mode")
delayed_only = s[s.delay_flag.notna()]
mode_delay = delayed_only.groupby("transport_mode").agg(
    shipments=("shipment_id", "count"),
    delay_rate_pct=("delay_flag", lambda x: round(100*x.mean(), 2)),
    avg_delay_hours=("delay_duration_hours", lambda x: round(x[x > 0].mean(), 1) if (x > 0).any() else 0),
).sort_values("delay_rate_pct", ascending=False)
lines.append(mode_delay.to_markdown())
lines.append("")

lines.append("## 3. Suppliers Associated with Higher Failure Rates")
sup_stats = s.groupby("supplier_name").agg(
    shipments=("shipment_id", "count"),
    violation_rate_pct=("temperature_excursion_flag", lambda x: round(100*x.mean(), 2)),
    critical_risk_pct=("spoilage_risk_category", lambda x: round(100*(x == "Critical Risk").mean(), 2)),
    total_loss=("estimated_financial_loss", "sum"),
).sort_values("critical_risk_pct", ascending=False)
lines.append(sup_stats.to_markdown())
fleet_avg_violation = s.temperature_excursion_flag.mean() * 100
flagged_suppliers = sup_stats[sup_stats.violation_rate_pct > fleet_avg_violation]
lines.append(f"\n**Finding:** Fleet-wide average temperature-violation rate is "
             f"{fleet_avg_violation:.2f}%. {len(flagged_suppliers)} of "
             f"{len(sup_stats)} suppliers exceed this average and should be reviewed: "
             f"{', '.join(flagged_suppliers.index.tolist())}.\n")

lines.append("## 4. Routes Associated with Higher Temperature Excursions")
route_stats = s.groupby(["route_id", "origin", "destination"]).agg(
    shipments=("shipment_id", "count"),
    excursion_rate_pct=("temperature_excursion_flag", lambda x: round(100*x.mean(), 2)),
    avg_distance_km=("distance_km", "mean"),
).reset_index()
route_stats = route_stats[route_stats.shipments >= 5].sort_values("excursion_rate_pct", ascending=False).head(10)
lines.append(route_stats.to_markdown(index=False))
lines.append("")

lines.append("## 5. Relationship Between Delays and Spoilage Risk")
xtab = pd.crosstab(
    s.loc[s.delay_flag.notna(), "delay_flag"].map({0: "On Time", 1: "Delayed"}),
    s.loc[s.delay_flag.notna(), "spoilage_risk_category"],
    normalize="index",
) * 100
xtab = xtab.round(1)
lines.append(xtab.to_markdown())
on_time_high = xtab.loc["On Time", ["High Risk", "Critical Risk"]].sum() if "On Time" in xtab.index else 0
delayed_high = xtab.loc["Delayed", ["High Risk", "Critical Risk"]].sum() if "Delayed" in xtab.index else 0
lines.append(f"\n**Finding:** {delayed_high:.1f}% of delayed shipments fall into High/Critical "
             f"spoilage risk, versus {on_time_high:.1f}% of on-time shipments — delayed shipments "
             f"are roughly {delayed_high/on_time_high:.1f}x as likely to be High/Critical risk.\n" if on_time_high else "")

lines.append("## 6. Financial Impact of Cold-Chain Failures")
total_loss = s.estimated_financial_loss.sum()
loss_from_severe = s.loc[s.excursion_severity == "Severe", "estimated_financial_loss"].sum()
loss_from_delay = s.loc[s.delay_flag == 1, "estimated_financial_loss"].sum()
lines.append(f"- Total estimated financial loss across all shipments: **${total_loss:,.2f}**")
lines.append(f"- Loss attributable to shipments with a **severe** temperature excursion: **${loss_from_severe:,.2f}** "
             f"({loss_from_severe/total_loss:.1%} of total)")
lines.append(f"- Loss on shipments that were also **delayed**: **${loss_from_delay:,.2f}** "
             f"({loss_from_delay/total_loss:.1%} of total)")
lines.append(f"- Average loss per shipment: **${s.estimated_financial_loss.mean():,.2f}**")
lines.append(f"- Average loss per shipment, Critical Risk only: "
             f"**${s.loc[s.spoilage_risk_category=='Critical Risk','estimated_financial_loss'].mean():,.2f}**\n")

with open("findings_report.md", "w") as f:
    f.write("\n".join(str(l) for l in lines))

print("Findings written to findings_report.md")
print(f"Total estimated financial loss: ${total_loss:,.2f}")
