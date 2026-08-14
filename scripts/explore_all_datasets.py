"""
EXPLORE ALL THREE DATASETS — run this one file to look at real samples
from WHO GHO, SEDAC/PM2.5, and WorldPop, all in one place.

SETUP (run once in your terminal):
    pip install requests rasterio numpy pandas

RUN:
    python explore_all_datasets.py

This prints real data to your screen AND saves CSVs you can open in Excel.
"""

import requests
import csv
import os

print("=" * 70)
print("DATASET 1 of 3: WHO GHO — health outcome statistics")
print("=" * 70)

resp = requests.get("https://ghoapi.azureedge.net/api/AIR_3_1", timeout=60)
data = resp.json().get("value", [])
kenya_rows = [r for r in data if r.get("SpatialDim") == "KEN"]

print(f"\nTotal records in this indicator (all countries, all years): {len(data)}")
print("\nKenya's actual values for 'AIR_3_1' (% of urban areas with PM monitoring):")
for r in kenya_rows[:5]:
    print(f"  Year {r.get('TimeDim')}: {r.get('NumericValue')}%")

with open("who_gho_sample.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["country_iso3", "year", "value"])
    for r in data:
        w.writerow([r.get("SpatialDim"), r.get("TimeDim"), r.get("NumericValue")])
print(f"\nSaved full dataset ({len(data)} rows) to who_gho_sample.csv — open it in Excel")


print("\n" + "=" * 70)
print("DATASET 2 of 3: WorldPop — child population grid")
print("=" * 70)

wp_url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2000_2020_Constrained/2020/KEN/ken_f_0_2020_constrained.tif"
wp_file = "kenya_children_sample.tif"

if not os.path.exists(wp_file):
    print(f"\nDownloading real Kenya population file (~36MB, this takes a moment)...")
    r = requests.get(wp_url, stream=True, timeout=120)
    with open(wp_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")

try:
    import rasterio
    with rasterio.open(wp_file) as src:
        print(f"\nFile: {wp_file}")
        print(f"This is a real map grid, {src.width} x {src.height} pixels")
        print(f"Each pixel = ~100m x 100m on the ground")
        print(f"Each pixel's value = estimated number of female children age 0-1 living there")

        # Sample a small window near Nairobi (roughly lat -1.28, lon 36.8)
        window = rasterio.windows.from_bounds(36.75, -1.35, 36.95, -1.20, transform=src.transform)
        sample = src.read(1, window=window)
        valid = sample[sample > 0]
        print(f"\nSample near Nairobi:")
        print(f"  Pixels with any population: {len(valid)}")
        if len(valid) > 0:
            print(f"  Total estimated children (this small area, this age/sex band only): {valid.sum():.1f}")
except ImportError:
    print("\n(Install rasterio to see the actual pixel values: pip install rasterio)")


print("\n" + "=" * 70)
print("DATASET 3 of 3: SEDAC/PM2.5 — pollution grid")
print("=" * 70)
print("""
This one can't be auto-downloaded here the same way — the file is large
(global coverage) and needs the AWS CLI. Real, already-published numbers
for context (from the same underlying dataset) are in
sedac_pm25_ethiopia_real_sample.csv — open that file directly.

To get the real Kenya-specific pixels, run download_all_kenya_data.sh first
(it fetches the actual global PM2.5 file), then run inspect_pm25_raster.py
pointed at Nairobi's coordinates instead of Lagos's.
""")

print("=" * 70)
print("DONE. Files now in your folder:")
print("  who_gho_sample.csv        - open in Excel, real WHO data")
print("  kenya_children_sample.tif - real population map (open in QGIS to see visually)")
print("=" * 70)
