# ============================================================================
# Pull real WHO GHO indicator data for the child air pollution project
# HOW TO RUN: Open this file in RStudio, then click the "Source" button
# (top right of this script pane), or press Ctrl+Shift+S / Cmd+Shift+S
# ============================================================================

# Install these ONCE if you don't have them (uncomment the line below, run it, then re-comment it)
# install.packages(c("httr", "jsonlite", "dplyr"))

library(httr)
library(jsonlite)
library(dplyr)

base_url <- "https://ghoapi.azureedge.net/api/"

# The WHO indicators relevant to child air-pollution exposure
indicators <- c(
  "AIR_4",    # Ambient air pollution attributable deaths, children <5
  "AIR_6",    # ... per 100,000 children <5
  "AIR_8",    # Ambient air pollution attributable DALYs, children <5
  "AIR_10",   # ... per 100,000 children <5
  "AIR_12",   # Household air pollution attributable deaths, children <5
  "AIR_36",   # Joint effects (ambient+household) deaths, children <5
  "AIR_3_1",  # % urban population covered by PM measurement stations
  "carep"     # Children <5 with pneumonia symptoms taken to a facility (%)
)

pull_indicator <- function(code) {
  url <- paste0(base_url, code)
  cat("Pulling", code, "...\n")
  resp <- GET(url)
  if (status_code(resp) != 200) {
    cat("  failed with status", status_code(resp), "\n")
    return(NULL)
  }
  parsed <- fromJSON(content(resp, "text", encoding = "UTF-8"), flatten = TRUE)
  records <- parsed$value
  if (is.null(records) || nrow(records) == 0) {
    cat("  no data returned\n")
    return(NULL)
  }
  cat("  got", nrow(records), "records\n")

  # Keep only country-level rows (drop regional/global aggregates)
  records <- records[records$SpatialDimType == "COUNTRY", ]

  data.frame(
    indicator_code = records$IndicatorCode,
    country_iso3 = records$SpatialDim,
    year = records$TimeDim,
    sex_or_disaggregation = records$Dim1,
    value = records$NumericValue,
    low = records$Low,
    high = records$High,
    stringsAsFactors = FALSE
  )
}

all_data <- bind_rows(lapply(indicators, pull_indicator))

write.csv(all_data, "gho_child_air_pollution_data.csv", row.names = FALSE)

cat("\nDone. Wrote", nrow(all_data), "rows to gho_child_air_pollution_data.csv\n")
cat("This file is now in your RStudio working directory — check getwd()\n")

# Quick look at what you got, e.g. Kenya's rows:
kenya_data <- all_data[all_data$country_iso3 == "KEN", ]
print(kenya_data)
