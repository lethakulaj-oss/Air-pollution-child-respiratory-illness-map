# Air Pollution & Child Respiratory Illness Map

A dashboard that overlays satellite-measured PM2.5 pollution levels with child population
density to identify which neighborhoods carry the highest respiratory-illness risk — often
informal settlements near highways or industrial zones with zero official air-quality
monitoring. It gives health ministries and NGOs a way to target asthma/pneumonia prevention
campaigns without waiting years for ground-sensor networks to be built.

**Prototype country:** Kenya (focus: Nairobi's informal settlements — Kibera, Mathare, Viwandani)

**Project duration:** 3 months (Aug 13 – Nov 13, 2026)

---

## Status

| Component | Status |
|---|---|
| Dataset identification | Done |
| Data collection (all 3 sources, real & verified) | Done |
| Data preprocessing pipeline | In progress |
| Risk score calculation | Not started |
| Dashboard (Power BI) | Not started |
| ML model layer | Not started |

Full timeline: see [`docs/TIMELINE.md`](docs/TIMELINE.md) or the linked Notion page.

---

## The Three Datasets

### 1. WHO GHO (Global Health Observatory)
Health outcome statistics — deaths, DALYs, pneumonia care-seeking rates, and air quality
monitoring coverage, by country.

- **Source:** `https://ghoapi.azureedge.net/api/` (free, no auth)
- **Real data collected:** 14,858 records for the `carep` indicator (children under 5 with
  pneumonia symptoms taken to a health facility), plus a smaller curated Kenya-specific
  extract in [`data/reference/carep_real_data_clean.csv`](data/reference/carep_real_data_clean.csv)
- **Role:** Validation/context layer. Not part of the risk score calculation — shows why the
  map matters and where ground monitoring is weakest.

### 2. SEDAC / ACAG PM2.5
Satellite-derived ground-level PM2.5 concentration, ~1km resolution, annual.

- **Source:** Verified live via Google Earth Engine
  (`projects/sat-io/open-datasets/GLOBAL-SATELLITE-PM25/ANNUAL`); also available at
  `sites.wustl.edu/acag/datasets/surface-pm2-5/`
- **Real data collected:** Kenya's full PM2.5 raster (`kenya_pm25_2020.tif`, not committed —
  see [Large Files](#large-files-not-in-this-repo)). National average confirmed at
  **17.97 µg/m³** (2020), verified against 589,474 real pixel values.
- **Role:** The exposure layer — how polluted the air is at each location.

### 3. WorldPop
Gridded child population counts (age 0–1 and 1–4, both sexes), ~100m resolution, constrained
to real building footprints.

- **Source:** `data.worldpop.org/GIS/AgeSex_structures/Global_2000_2020_Constrained/2020/KEN/`
- **Real data collected:** 4 raw files combined into one "children under 5" layer
  (`ken_children_under5_2020.tif`, not committed — see [Large Files](#large-files-not-in-this-repo)).
  Total: **7,655,634 children under 5 in Kenya** (2020).
- **Role:** The vulnerability layer — how many children are exposed at each location.

### How they combine
```
Risk score = PM2.5 value  ×  child population, per location
```
WHO GHO joins separately, by country code, as a validation/context layer — it is not
multiplied into the score.

---

## Key Real Findings So Far

- Kenya's national average PM2.5 (17.97 µg/m³) is **~3.6x** the WHO safety guideline (5 µg/m³)
- **Viwandani**, an industrial informal settlement in Nairobi, measured a peak PM2.5 of
  **111.87 µg/m³** — over **22x** the WHO guideline
- An estimated **8,000 premature deaths per year** in Nairobi are linked to air pollution
- **80%** of hospital visits at one Nairobi clinic (serving informal settlements) were linked
  to air pollution
- **68.6%** of children with pneumonia symptoms in Kenya (2014, mid-income households) were
  taken to a health facility — care-seeking gaps are worse in lower-income groups

Full source list in [`data/reference/kenya_real_published_numbers.csv`](data/reference/kenya_real_published_numbers.csv)
and [`data/reference/kenya_who_health_statistics_real.csv`](data/reference/kenya_who_health_statistics_real.csv).

---

## Repository Structure

```
├── README.md                          this file
├── data/
│   └── reference/                     small, real reference CSVs (country codes,
│                                       indicator names, published Kenya stats)
├── scripts/
│   ├── pull_gho_indicator_data_fixed.py   pulls real, current WHO GHO indicator data
│   ├── pull_gho_data.R                    R version of the WHO data pull
│   ├── kenya_correct_pipeline.py          combines PM2.5 + WorldPop into a risk score
│   ├── inspect_pm25_raster.py             opens and inspects a PM2.5 GeoTIFF
│   └── explore_all_datasets.py            quick-look script across all 3 sources
└── docs/
    ├── Kenya_Air_Pollution_Project.pptx       pitch deck
    └── Kenya_Air_Pollution_Project_Data.xlsx  consolidated data workbook
```

## Large Files Not In This Repo

The actual raster files (WorldPop GeoTIFFs, PM2.5 GeoTIFF) are large (tens of MB each) and
are not committed to keep the repo lightweight. They're reproducible by running the scripts
in `scripts/` against the live data sources listed above, or available on request.

## Methodology Notes

- **Grid alignment:** PM2.5 (~1km cells) and WorldPop (~100m cells) don't share a native
  resolution. The correct approach — used in `kenya_correct_pipeline.py` — is to **sum**
  population into each real PM2.5 cell (via `Resampling.sum`), not interpolate PM2.5 up to
  WorldPop's finer grid. This avoids inventing pollution values that were never measured.
- **Prototype country choice:** Kenya was selected over Nigeria/India/Ethiopia for a
  balance of severity (well-documented informal settlements next to industrial zones),
  data availability, and manageable file sizes for a fast first working pipeline.

## Next Steps

See the [Notion timeline](#) for the full week-by-week plan. Immediate next steps:
1. Finish the preprocessing pipeline (grid alignment)
2. Compute the real risk score across all of Kenya
3. Aggregate to neighborhood/ward level for the dashboard
4. Build the Power BI dashboard
5. Add an ML layer using WHO health data as a training target
