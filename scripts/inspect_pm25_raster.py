"""
Download and inspect a real SEDAC/ACAG PM2.5 GeoTIFF — no NASA Earthdata
login required, since the same data is mirrored on AWS Open Data (free,
no account needed) and via the ACAG lab's own site.

SETUP (run in a terminal, on your own machine — not this sandboxed chat):

    pip install rasterio numpy awscli

STEP 1 — list what's available in the AWS bucket (no account needed):

    aws s3 ls --no-sign-request s3://v6.gl.02.04/

    Look for a file matching the annual global PM2.5 grid, something like:
    V6.GL02.04.CNNPM25.Global.YYYY01-YYYY12.nc   (a full year, netCDF)

STEP 2 — download one year's file (example filename, adjust after Step 1):

    aws s3 cp --no-sign-request \
        s3://v6.gl.02.04/annual/GWRPM25.NA.202001-202012.nc \
        ./pm25_sample.nc

    (Exact paths inside the bucket vary by version — Step 1's `ls` output
    tells you the real filenames. If the .nc route is awkward, the ACAG lab
    site also lets you download individual-year GeoTIFFs directly at
    https://sites.wustl.edu/acag/datasets/surface-pm2-5/ under whichever
    version listed there, e.g. V5.GL.04 -> the wustl.box.com folder link.)

STEP 3 — open it and look at real pixel values for a specific place:
"""

import rasterio
import numpy as np

# Example: inspect PM2.5 values in a bounding box around Lagos, Nigeria
# (swap in coordinates for whatever city/region matters to your project)
LAT_MIN, LAT_MAX = 6.35, 6.65
LON_MIN, LON_MAX = 3.15, 3.55

FILE_PATH = "pm25_sample.tif"  # or .nc opened via rioxarray, see note below


def inspect_raster(path):
    with rasterio.open(path) as src:
        print(f"CRS: {src.crs}")
        print(f"Resolution: {src.res}")  # (x_res, y_res) in degrees
        print(f"Full grid shape: {src.width} x {src.height} pixels")
        print(f"Data type: {src.dtypes[0]}")

        # Convert our lat/lon bounding box into pixel row/col window
        window = rasterio.windows.from_bounds(
            LON_MIN, LAT_MIN, LON_MAX, LAT_MAX, transform=src.transform
        )
        data = src.read(1, window=window)

        valid = data[data > 0]  # PM2.5 can't be negative; filters nodata
        print(f"\nPixels in this bounding box: {data.size}")
        print(f"Mean PM2.5: {valid.mean():.2f} ug/m3")
        print(f"Min: {valid.min():.2f}  Max: {valid.max():.2f} ug/m3")
        print(f"\nRaw grid (each cell ~1km x 1km):\n{data}")


if __name__ == "__main__":
    # Note: if you downloaded a .nc (netCDF) file instead of .tif,
    # use rioxarray instead of rasterio:
    #   import rioxarray
    #   da = rioxarray.open_rasterio("pm25_sample.nc")
    #   subset = da.sel(x=slice(LON_MIN, LON_MAX), y=slice(LAT_MAX, LAT_MIN))
    #   print(subset.values)
    inspect_raster(FILE_PATH)
