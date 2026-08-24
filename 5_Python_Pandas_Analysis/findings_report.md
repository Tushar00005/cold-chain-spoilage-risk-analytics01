# Python + Pandas Analytical Findings

## 1. Temperature-Risk Patterns by Product Category
| product_category   |   shipments |   violation_rate_pct |   avg_deviation_c |   critical_risk_pct |
|:-------------------|------------:|---------------------:|------------------:|--------------------:|
| Meat               |         307 |                39.74 |              2.25 |               12.38 |
| Vegetables         |         369 |                37.4  |              2.32 |               13.82 |
| Fruits             |         281 |                35.94 |              2.13 |               13.88 |
| Seafood            |         226 |                30.97 |              2.09 |               31.86 |
| Dairy              |         317 |                30.91 |              1.81 |               20.5  |

**Finding:** `Meat` has the highest temperature-violation rate (39.74%), making it the category needing the tightest cold-chain control.

## 2. Delay-Risk Patterns by Transport Mode
| transport_mode     |   shipments |   delay_rate_pct |   avg_delay_hours |
|:-------------------|------------:|-----------------:|------------------:|
| Reefer Truck       |         266 |            83.83 |              30.2 |
| Air Cargo          |         132 |            81.82 |              24.1 |
| Unknown            |         458 |            80.35 |              35.4 |
| Reefer Ship        |         167 |            79.64 |              35.8 |
| Refrigerated Truck |         242 |            78.1  |              41.7 |

## 3. Suppliers Associated with Higher Failure Rates
| supplier_name           |   shipments |   violation_rate_pct |   critical_risk_pct |   total_loss |
|:------------------------|------------:|---------------------:|--------------------:|-------------:|
| Highland Dairy Group    |         148 |                35.81 |               24.32 |       158074 |
| Prime Cut Meats Co      |         145 |                36.55 |               19.31 |       164071 |
| Sunrise Produce Ltd     |         158 |                35.44 |               18.35 |       148266 |
| Coastal Catch Exports   |         157 |                40.13 |               17.83 |       149643 |
| Bluefin Seafood Traders |         152 |                31.58 |               17.11 |       141520 |
| Green Pasture Dairy     |         142 |                33.1  |               16.9  |       137957 |
| Fresh Valley Farms      |         137 |                35.04 |               16.79 |       133539 |
| Arctic Ocean Seafoods   |         158 |                35.44 |               16.46 |       128776 |
| Golden Harvest Farms    |         140 |                36.43 |               15    |       118964 |
| Meadow Fresh Supplies   |         163 |                33.13 |               14.72 |       158459 |

**Finding:** Fleet-wide average temperature-violation rate is 35.27%. 6 of 10 suppliers exceed this average and should be reviewed: Highland Dairy Group, Prime Cut Meats Co, Sunrise Produce Ltd, Coastal Catch Exports, Arctic Ocean Seafoods, Golden Harvest Farms.

## 4. Routes Associated with Higher Temperature Excursions
| route_id   | origin                    | destination               |   shipments |   excursion_rate_pct |   avg_distance_km |
|:-----------|:--------------------------|:--------------------------|------------:|---------------------:|------------------:|
| R010       | Mexico City, Mexico       | Los Angeles, USA          |          43 |                48.84 |              5189 |
| R019       | Miami, USA                | Los Angeles, USA          |          42 |                47.62 |              2360 |
| R011       | Rotterdam, Netherlands    | Dallas, USA               |          66 |                45.45 |              3558 |
| R002       | Chicago, USA              | Dallas, USA               |          49 |                44.9  |              1340 |
| R005       | New York, USA             | Vancouver, Canada         |          52 |                42.31 |              4671 |
| R018       | Ho Chi Minh City, Vietnam | Los Angeles, USA          |          43 |                41.86 |              1703 |
| R023       | Vancouver, Canada         | Ho Chi Minh City, Vietnam |          51 |                41.18 |              3595 |
| R021       | Dallas, USA               | New York, USA             |          69 |                40.58 |              4642 |
| R001       | Chicago, USA              | Vancouver, Canada         |          54 |                38.89 |              2921 |
| R009       | Mexico City, Mexico       | Seattle, USA              |          55 |                36.36 |              3227 |

## 5. Relationship Between Delays and Spoilage Risk
| delay_flag   |   Critical Risk |   High Risk |   Low Risk |   Medium Risk |
|:-------------|----------------:|------------:|-----------:|--------------:|
| Delayed      |            22.2 |        36.7 |        4.2 |          36.8 |
| On Time      |             7.4 |        22.1 |       25   |          45.5 |

**Finding:** 58.9% of delayed shipments fall into High/Critical spoilage risk, versus 29.5% of on-time shipments — delayed shipments are roughly 2.0x as likely to be High/Critical risk.

## 6. Financial Impact of Cold-Chain Failures
- Total estimated financial loss across all shipments: **$1,439,268.81**
- Loss attributable to shipments with a **severe** temperature excursion: **$543,680.63** (37.8% of total)
- Loss on shipments that were also **delayed**: **$1,118,114.21** (77.7% of total)
- Average loss per shipment: **$959.51**
- Average loss per shipment, Critical Risk only: **$2,475.22**
