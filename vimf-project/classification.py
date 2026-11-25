from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

OUT_DIR = BASE_DIR / "results"
FIG_DIR = OUT_DIR / "figures"
COMP_DIR = OUT_DIR / "composites"
CLASS_DIR = OUT_DIR / "classification"

for folder in [FIG_DIR, COMP_DIR, CLASS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


ERA5_FILE = DATA_DIR / "era5_moisture_flux_1984_2020.nc"
DROUGHT_FILE = DATA_DIR / "drought_indices_vilcanota.csv"
ENSO_FILE = DATA_DIR / "driver_composites.csv"

START_DATE = "1985-01-01"
END_DATE = "2020-12-01"

# Drought threshold (PROVISIONAL: confirm with Olivia)
DROUGHT_THRESHOLD = -1.0

# ENSO threshold
ENSO_THRESHOLD = 0.5

# Spatial domain
LAT_MIN, LAT_MAX = -20, -5
LON_MIN, LON_MAX = -220, 0

# ERA5 variables
VAR_U = "viwve"
VAR_V = "viwvn"
VAR_DIV = "vimdf"

# Reference:
# "all" = all months of the same ENSO phase and season
# "non_drought" = only non-drought months
REFERENCE = "all"

# Plot configuration
QUIVER_STEP = 4
DPI = 300

CASES = [
    ("SON", "La Nina"),
    ("DJF", "El Nino"),
    ("DJF", "La Nina"),
    ("MAM", "El Nino"),
]

SEASON_MONTHS = {
    "SON": [9, 10, 11],
    "DJF": [12, 1, 2],
    "MAM": [3, 4, 5],
}


# ============================================================
# 2. BUILD MONTHLY CLASSIFICATION
# ============================================================

def build_classification():

    print("\nBuilding monthly classification...")

    # --------------------------------------------------------
    # Read drought indices
    # --------------------------------------------------------

    drought = pd.read_csv(DROUGHT_FILE)

    drought["date"] = (
        pd.to_datetime(drought["time"])
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    drought = drought[["date", "SPEI_3"]]

    # --------------------------------------------------------
    # Read ENSO indices
    # --------------------------------------------------------

    enso = pd.read_csv(ENSO_FILE)

    enso["date"] = (
        pd.to_datetime(enso["date"])
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    enso = enso[["date", "nino34"]]

    # --------------------------------------------------------
    # Validate monthly records
    # --------------------------------------------------------

    for name, table in [
        ("Drought", drought),
        ("ENSO", enso)
    ]:

        if table["date"].duplicated().any():
            raise ValueError(
                f"Duplicated dates in {name} dataset."
            )

    # --------------------------------------------------------
    # Merge datasets
    # --------------------------------------------------------

    df = pd.merge(
        drought,
        enso,
        on="date",
        how="inner",
        validate="one_to_one"
    )

    df = df.sort_values("date")

    df = df.loc[
        (df["date"] >= START_DATE) &
        (df["date"] <= END_DATE)
    ].copy()

    # --------------------------------------------------------
    # ENSO classification using monthly Nino 3.4
    # --------------------------------------------------------

    df["enso_phase"] = np.select(
        [
            df["nino34"] > ENSO_THRESHOLD,
            df["nino34"] < -ENSO_THRESHOLD
        ],
        [
            "El Nino",
            "La Nina"
        ],
        default="Neutral"
    )

    # --------------------------------------------------------
    # Drought classification using SPEI-3
    # --------------------------------------------------------

    # Threshold: SPEI <= -1.0
    df["drought"] = (
        df["SPEI_3"] <= DROUGHT_THRESHOLD
    )

    # Missing SPEI values cannot be classified
    df.loc[
        df["SPEI_3"].isna(),
        "drought"
    ] = False

    # --------------------------------------------------------
    # Save classification
    # --------------------------------------------------------

    output_file = CLASS_DIR / "classification.csv"

    df.to_csv(output_file, index=False)

    print(f"Classification saved: {output_file}")

    print("\nENSO distribution:")
    print(df["enso_phase"].value_counts())

    print("\nDrought distribution:")
    print(df["drought"].value_counts())

    print("\nClassification preview:")
    print(df.head())

    return df.set_index("date").sort_index()

build_classification()
