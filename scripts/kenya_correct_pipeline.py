"""
Kenya child pollution risk score - CORRECT approach.

Instead of stretching PM2.5 (1km cells) to fake precision at WorldPop's
100m resolution, this sums the real children inside each real PM2.5 cell.
Every number in the output is either directly measured (PM2.5) or directly
counted (population) - nothing is invented.

SETUP:
    pip install rasterio numpy

BEFORE RUNNING:
    Update the 5 file paths below to match your actual downloaded filenames.
    Run "ls" in your terminal, in the folder with your downloads, and copy
    the exact names you see - they may not match these guesses exactly.
"""

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np

# ---- UPDATE THESE 5 PATHS to match your actual downloaded files ----
WORLDPOP_FILES = [
    "ken_f_0_2020_constrained.tif",
    "ken_f_1_2020_constrained.tif",
    "ken_m_0_2020_constrained.tif",
    "ken_m_1_2020_constrained.tif",
]
PM25_FILE = "pm25_kenya.tif"   # whatever you downloaded from sites.wustl.edu/acag
# ----------------------------------------------------------------------


def sum_children_under_5():
    """Add the 4 WorldPop files into one 'children under 5' grid (100m)."""
    total = None
    profile = None
    for path in WORLDPOP_FILES:
        with rasterio.open(path) as src:
            data = src.read(1, masked=True).filled(0)
            if total is None:
                total = data.astype("float64")
                profile = src.profile
            else:
                total += data
    print(f"Total children under 5 (Kenya, summed): {total.sum():,.0f}")
    return total, profile


def aggregate_population_to_pm25_grid(children_100m, wp_profile, pm25_path):
    """
    THE KEY STEP: instead of stretching PM2.5 to 100m (fake precision),
    we shrink the population data down into PM2.5's real, native cells.
    Resampling.sum adds up every 100m population cell that falls inside
    each coarser PM2.5 cell - a real total, not an interpolated guess.
    """
    with rasterio.open(pm25_path) as pm25_src:
        pm25 = pm25_src.read(1)
        pm25_profile = pm25_src.profile

        children_aggregated = np.zeros(
            (pm25_src.height, pm25_src.width), dtype="float64"
        )

        reproject(
            source=children_100m,
            destination=children_aggregated,
            src_transform=wp_profile["transform"],
            src_crs=wp_profile["crs"],
            dst_transform=pm25_src.transform,
            dst_crs=pm25_src.crs,
            resampling=Resampling.sum,   # <-- the fix: sum, not blend
        )

    return pm25, children_aggregated, pm25_profile


def compute_and_save_risk_score(pm25, children, profile):
    risk_score = pm25 * children

    out_profile = profile.copy()
    out_profile.update(dtype="float32", count=1)
    with rasterio.open("kenya_child_pollution_risk_score.tif", "w", **out_profile) as dst:
        dst.write(risk_score.astype("float32"), 1)

    print(f"\nSaved: kenya_child_pollution_risk_score.tif")
    print(f"Grid resolution: same as PM2.5 (~1km cells, real measurements)")
    print(f"Highest-risk cell score: {np.nanmax(risk_score):,.1f}")

    who_guideline = 5  # ug/m3, WHO 2021 annual guideline
    exposed_mask = pm25 > who_guideline
    total_exposed = children[exposed_mask].sum()
    print(f"\nChildren under 5 living above WHO's PM2.5 guideline "
          f"({who_guideline} ug/m3): {total_exposed:,.0f}")

    # Top 10 highest-risk cells - a first-pass "priority list"
    flat_idx = np.argsort(risk_score.flatten())[::-1][:10]
    rows, cols = np.unravel_index(flat_idx, risk_score.shape)
    print("\nTop 10 highest-risk grid cells:")
    for r, c in zip(rows, cols):
        lon, lat = rasterio.transform.xy(profile["transform"], r, c)
        print(f"  lat={lat:.4f}, lon={lon:.4f}  "
              f"PM2.5={pm25[r,c]:.1f}  children={children[r,c]:.0f}  "
              f"score={risk_score[r,c]:,.0f}")


if __name__ == "__main__":
    children_100m, wp_profile = sum_children_under_5()
    pm25, children_aggregated, pm25_profile = aggregate_population_to_pm25_grid(
        children_100m, wp_profile, PM25_FILE
    )
    compute_and_save_risk_score(pm25, children_aggregated, pm25_profile)
