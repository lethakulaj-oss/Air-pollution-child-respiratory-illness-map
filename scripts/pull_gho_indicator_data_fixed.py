"""
Pull real WHO GHO indicator data — FIXED VERSION.

The original indicator codes (AIR_4, AIR_6, AIR_8, AIR_10, AIR_12, AIR_36,
AIR_3_1) turned out to be outdated: WHO restructured its air pollution
indicators at some point and those specific codes no longer return data,
even though they still show up in the indicator name catalog. This version
finds the CURRENT working codes automatically instead of guessing.

Usage:
    pip install requests
    python pull_gho_indicator_data_fixed.py
"""

import requests
import csv

BASE_URL = "https://ghoapi.azureedge.net/api/"

# Step 1: pull the full indicator catalog and find anything pollution/
# respiratory related, so we're working from what's ACTUALLY live today.
print("Fetching current indicator catalog...")
resp = requests.get(f"{BASE_URL}Indicator", timeout=60)
all_indicators = resp.json().get("value", [])

keywords = ["pollution", "pm2.5", "pm2·5", "respiratory", "pneumonia", "PM10"]
candidates = [
    ind for ind in all_indicators
    if any(kw in ind["IndicatorName"].lower() for kw in keywords)
]

print(f"\nFound {len(candidates)} candidate indicators mentioning pollution/respiratory topics.\n")

# Step 2: test each candidate for actual data (not just existing in the catalog)
working_indicators = []
all_rows = []

for ind in candidates:
    code = ind["IndicatorCode"]
    name = ind["IndicatorName"]
    try:
        r = requests.get(f"{BASE_URL}{code}", timeout=30)
        records = r.json().get("value", [])
    except Exception:
        continue

    if len(records) == 0:
        continue  # dead/retired indicator, skip silently

    working_indicators.append((code, name, len(records)))

    for rec in records:
        if rec.get("SpatialDimType") != "COUNTRY":
            continue
        all_rows.append({
            "indicator_code": code,
            "indicator_name": name,
            "country_iso3": rec.get("SpatialDim"),
            "year": rec.get("TimeDim"),
            "sex_or_disaggregation": rec.get("Dim1"),
            "value": rec.get("NumericValue"),
        })

print("=" * 70)
print(f"WORKING indicators (have real data today): {len(working_indicators)}")
print("=" * 70)
for code, name, count in working_indicators:
    print(f"  {code:20s} {count:6d} records   {name}")

out_file = "gho_pollution_data_VERIFIED.csv"
with open(out_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "indicator_code", "indicator_name", "country_iso3",
        "year", "sex_or_disaggregation", "value"
    ])
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nSaved {len(all_rows)} total rows to {out_file}")

# Show Kenya's data specifically
print("\n" + "=" * 70)
print("Kenya's data across all working indicators:")
print("=" * 70)
kenya_rows = [r for r in all_rows if r["country_iso3"] == "KEN"]
for r in kenya_rows[:20]:
    print(f"  {r['indicator_code']} | {r['year']} | {r['value']}")
