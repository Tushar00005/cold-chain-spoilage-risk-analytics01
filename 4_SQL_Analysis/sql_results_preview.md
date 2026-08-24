# SQL Analysis Results Preview (computed via Pandas)

_Sandbox has no live MySQL server; figures below mirror what `analysis_queries.sql` returns once run against a real MySQL instance loaded via `load_data.py`._

## Q1. Shipment volume & status
- Total shipments: **1500**
- Delivered: **1025** (68.3%)
- In Transit: **240**
- Cancelled: **235**

## Q2. On-time vs delayed
- On time: **190**
- Delayed: **835** (81.5%)
- Avg delay when delayed: **34.0 hrs**

## Q3. Temperature compliance
- Violations: **529** (35.3%)
- Compliance rate: **64.7%**
- Avg deviation: **2.13 C**

## Q4. Spoilage risk distribution & loss
| spoilage_risk_category   |   shipment_count |   total_spoiled_units |   total_loss |
|:-------------------------|-----------------:|----------------------:|-------------:|
| Critical Risk            |              265 |                 48027 |       655933 |
| High Risk                |              490 |                 42738 |       584789 |
| Low Risk                 |              167 |                     0 |            0 |
| Medium Risk              |              578 |                 13785 |       198547 |


## Q5. Loss by product category
| product_category   |   total_shipments |   total_loss |
|:-------------------|------------------:|-------------:|
| Vegetables         |               369 |       404171 |
| Dairy              |               317 |       348321 |
| Meat               |               307 |       293433 |
| Seafood            |               226 |       224433 |
| Fruits             |               281 |       168911 |

## Q6. Supplier performance (top 10 by loss)
| supplier_name           |   total_shipments |   violation_rate |   total_loss |
|:------------------------|------------------:|-----------------:|-------------:|
| Prime Cut Meats Co      |               145 |            36.55 |       164071 |
| Meadow Fresh Supplies   |               163 |            33.13 |       158459 |
| Highland Dairy Group    |               148 |            35.81 |       158074 |
| Coastal Catch Exports   |               157 |            40.13 |       149643 |
| Sunrise Produce Ltd     |               158 |            35.44 |       148266 |
| Bluefin Seafood Traders |               152 |            31.58 |       141520 |
| Green Pasture Dairy     |               142 |            33.1  |       137957 |
| Fresh Valley Farms      |               137 |            35.04 |       133539 |
| Arctic Ocean Seafoods   |               158 |            35.44 |       128776 |
| Golden Harvest Farms    |               140 |            36.43 |       118964 |

## Q8. Route performance (top 10 by excursion rate, min 5 shipments)
| route_id   | origin                    | destination               |   total_shipments |   excursion_rate |   total_loss |
|:-----------|:--------------------------|:--------------------------|------------------:|-----------------:|-------------:|
| R010       | Mexico City, Mexico       | Los Angeles, USA          |                43 |            48.84 |      38748.8 |
| R019       | Miami, USA                | Los Angeles, USA          |                42 |            47.62 |      52095.1 |
| R011       | Rotterdam, Netherlands    | Dallas, USA               |                66 |            45.45 |      50820.2 |
| R002       | Chicago, USA              | Dallas, USA               |                49 |            44.9  |      40257.7 |
| R005       | New York, USA             | Vancouver, Canada         |                52 |            42.31 |      42647.5 |
| R018       | Ho Chi Minh City, Vietnam | Los Angeles, USA          |                43 |            41.86 |      29986.6 |
| R023       | Vancouver, Canada         | Ho Chi Minh City, Vietnam |                51 |            41.18 |      51220.7 |
| R021       | Dallas, USA               | New York, USA             |                69 |            40.58 |      94552.8 |
| R001       | Chicago, USA              | Vancouver, Canada         |                54 |            38.89 |      51697.5 |
| R009       | Mexico City, Mexico       | Seattle, USA              |                55 |            36.36 |      59801.2 |

## Q9. Top 10 highest-loss products
| product_id   | product_name         |   total_shipments |   total_spoiled_units |   total_loss |
|:-------------|:---------------------|------------------:|----------------------:|-------------:|
| P003         | Cheddar Cheese       |                82 |                  7080 |     133883   |
| P011         | Tuna Steaks          |                63 |                  5974 |     127963   |
| P020         | Mushrooms            |                74 |                  4837 |     113718   |
| P001         | Whole Milk 1L        |                74 |                  6542 |     108139   |
| P018         | Broccoli             |                78 |                  5888 |      96798.7 |
| P006         | Ground Beef          |                82 |                  5420 |      90893.4 |
| P008         | Lamb Cuts            |                76 |                  4528 |      87526.2 |
| P017         | Spinach              |                74 |                  3947 |      86281.4 |
| P005         | Fresh Chicken Breast |                92 |                  5717 |      76493.5 |
| P012         | Strawberries         |                65 |                  3859 |      71970.4 |

## Q11. Delay vs spoilage risk
| delay_bucket   |   shipments |   high_critical_risk_pct |   avg_loss_per_shipment |
|:---------------|------------:|-------------------------:|------------------------:|
| On Time        |         244 |                    29.51 |                  725.48 |
| Delayed < 6h   |         175 |                    31.43 |                  576.75 |
| Delayed 6-24h  |         337 |                    52.23 |                  913.91 |
| Delayed 24h+   |         509 |                    72.89 |                 1393.31 |