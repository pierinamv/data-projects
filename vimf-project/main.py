
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


# ============================================================
# 3. LOAD ERA5 DATA
# ============================================================

def load_era5():

    print("\nLoading ERA5...")

    ds = xr.open_dataset(ERA5_FILE)

    # Standardize time coordinate
    if "valid_time" in ds.coords or "valid_time" in ds.dims:
        ds = ds.rename({"valid_time": "time"})

    # Check required variables
    required = [VAR_U, VAR_V, VAR_DIV]

    missing = set(required) - set(ds.data_vars)

    if missing:
        raise ValueError(
            f"Missing ERA5 variables: {missing}"
        )

    # Convert longitude to [-360, 0]
    if float(ds.longitude.max()) > 180:

        ds = ds.assign_coords(
            longitude=xr.where(
                ds.longitude > 180,
                ds.longitude - 360,
                ds.longitude
            )
        )

    # Sort coordinates
    ds = ds.sortby("latitude").sortby("longitude")

    # Select spatial domain
    ds = ds.sel(
        latitude=slice(LAT_MIN, LAT_MAX),
        longitude=slice(LON_MIN, LON_MAX)
    )

    # Select temporal domain
    ds = ds.sel(
        time=slice(START_DATE, END_DATE)
    )

    # Keep required variables
    ds = ds[required]

    # Rename vector components
    ds = ds.rename({
        VAR_U: "IVT_u",
        VAR_V: "IVT_v"
    })

    # Moisture flux convergence
    ds["MFC"] = -ds[VAR_DIV]

    # Monthly IVT magnitude
    ds["IVT"] = np.hypot(
        ds["IVT_u"],
        ds["IVT_v"]
    )

    # Standardize monthly timestamps
    dates = pd.DatetimeIndex(ds.time.values)

    ds = ds.assign_coords(
        time=dates.to_period("M").to_timestamp()
    )

    if pd.Index(ds.time.values).duplicated().any():
        raise ValueError("Duplicated ERA5 monthly records.")

    print("\nERA5 information:")
    print(ds)

    return ds


# ============================================================
# 4. VALIDATE TEMPORAL COVERAGE
# ============================================================

def validate_dates(ds, classification):

    era_dates = pd.DatetimeIndex(ds.time.values)

    class_dates = classification.index

    common = era_dates.intersection(class_dates)

    print("\nTemporal validation:")
    print(f"ERA5 records: {len(era_dates)}")
    print(f"Classification records: {len(class_dates)}")
    print(f"Common records: {len(common)}")

    expected = pd.date_range(
        START_DATE,
        END_DATE,
        freq="MS"
    )

    expected_seasonal = expected[
        expected.month.isin(
            SEASON_MONTHS["SON"] +
            SEASON_MONTHS["DJF"] +
            SEASON_MONTHS["MAM"]
        )
    ]

    missing = expected_seasonal.difference(era_dates)

    if len(missing) > 0:
        print(
            f"WARNING: {len(missing)} expected "
            "seasonal months are missing in ERA5."
        )
        print(missing)

    return common


# ============================================================
# 5. BUILD SEASONAL COMPOSITES
# ============================================================

def composite(ds, dates):

    available = pd.DatetimeIndex(ds.time.values)

    dates = pd.DatetimeIndex(dates).intersection(
        available
    )

    if len(dates) == 0:
        raise ValueError("No matching ERA5 dates.")

    result = ds.sel(time=dates).mean(
        dim="time",
        skipna=True
    )

    return result, len(dates)


def make_case(ds, classification, season, phase):

    # Select seasonal months
    table = classification.loc[
        classification.index.month.isin(
            SEASON_MONTHS[season]
        )
    ]

    # Target: drought months during ENSO phase
    target_mask = (
        (table["enso_phase"] == phase) &
        (table["drought"])
    )

    target_dates = table.index[target_mask]

    # Reference: all months during ENSO phase
    reference_mask = (
        table["enso_phase"] == phase
    )

    if REFERENCE == "non_drought":
        reference_mask &= ~table["drought"]

    reference_dates = table.index[reference_mask]

    # Compute composites
    target, n_target = composite(
        ds, target_dates
    )

    reference, n_reference = composite(
        ds, reference_dates
    )

    # Difference
    anomaly = target - reference

    print(
        f"\n{season} | {phase}"
        f"\nDrought months: {n_target}"
        f"\nReference months: {n_reference}"
    )

    return target, reference, anomaly, n_target, n_reference


# ============================================================
# 6. PLOT COMPOSITE DIFFERENCES
# ============================================================

def plot_case(
    anomaly,
    season,
    phase,
    n_target,
    n_reference
):

    lon = anomaly.longitude.values
    lat = anomaly.latitude.values

    X, Y = np.meshgrid(lon, lat)

    fig, axes = plt.subplots(
        1, 2,
        figsize=(15, 6),
        constrained_layout=True
    )

    # --------------------------------------------------------
    # Panel A: IVT magnitude difference and vector difference
    # --------------------------------------------------------

    ax = axes[0]

    delta_ivt = anomaly["IVT"].values

    vmax = np.nanpercentile(
        np.abs(delta_ivt), 98
    )

    vmax = max(vmax, 1e-12)

    levels = np.linspace(-vmax, vmax, 19)

    cf = ax.contourf(
        X, Y, delta_ivt,
        levels=levels,
        cmap="RdBu_r",
        extend="both"
    )

    U = anomaly["IVT_u"].values
    V = anomaly["IVT_v"].values

    step = QUIVER_STEP

    q = ax.quiver(
        X[::step, ::step],
        Y[::step, ::step],
        U[::step, ::step],
        V[::step, ::step],
        color="black",
        scale=50,
        width=0.0025
    )

    ax.quiverkey(
        q, 0.85, 1.04, 10,
        "10 kg m$^{-1}$ s$^{-1}$",
        labelpos="E"
    )

    fig.colorbar(
        cf,
        ax=ax,
        label="VIMF magnitude difference "
              "(kg m$^{-1}$ s$^{-1}$)"
    )

    ax.set_title(
        "VIMF magnitude difference"
    )

    # --------------------------------------------------------
    # Panel B: MFC difference
    # --------------------------------------------------------

    ax = axes[1]

    delta_mfc = anomaly["MFC"].values

    vmax = np.nanpercentile(
        np.abs(delta_mfc), 98
    )

    vmax = max(vmax, 1e-12)

    levels = np.linspace(-vmax, vmax, 19)

    cf = ax.contourf(
        X, Y, delta_mfc,
        levels=levels,
        cmap="RdBu_r",
        extend="both"
    )

    fig.colorbar(
        cf,
        ax=ax,
        label="VIMFC difference (kg m$^{-2}$ s$^{-1}$)"
    )

    ax.set_title(
        "Vertical INtegrated Moisture-flux convergence difference"
    )

    # --------------------------------------------------------
    # Formatting
    # --------------------------------------------------------

    for ax in axes:

        ax.set_xlim(LON_MIN, LON_MAX)
        ax.set_ylim(LAT_MIN, LAT_MAX)

        ax.set_xlabel("Longitude (degrees)")
        ax.set_ylabel("Latitude (degrees)")

        ax.set_xticks(
            np.arange(LON_MIN, LON_MAX + 1, 40)
        )

        ax.grid(alpha=0.25)

    fig.suptitle(
        f"{season} | {phase}\n"
        f"Drought (n={n_target}) vs "
        f"ENSO reference (n={n_reference})",
        fontsize=14
    )

    filename = (
        f"{season}_{phase.replace(' ', '_')}_"
        f"{REFERENCE}.png"
    )

    fig.savefig(
        FIG_DIR / filename,
        dpi=DPI,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Figure saved: {filename}")


# ============================================================
# 7. SAVE COMPOSITES
# ============================================================

def save_composites(
    target,
    reference,
    anomaly,
    season,
    phase
):

    name = f"{season}_{phase.replace(' ', '_')}"
    
    #Merge the three composites datasets
    output = xr.merge([
           target.rename({
               var:f"{var}_drought"
               for var in target.data_vars
               })
           ,
           reference.rename({
               var:f"{var}_reference"
               for var in reference.data_vars
               })
           ,
           anomaly.rename({
               var:f"{var}_difference"
               for var in anomaly.data_vars
               })
        ])

    #Save metadata
    output.attrs.update({
        "season":season,
        "enso-phase":phase,
        "reference":REFERENCE,
        "drought_threshold":DROUGHT_THRESHOLD,
        "enso_threshold":ENSO_THRESHOLD,
        "description":(
            "Seasonal moisture flux copmosites."
            "Difference = drought composite - "
            "ENSO reference composite."
            )
        })
    
  
    #output = xr.Dataset({
    #    "drought_composite": target,
    #    "enso_reference": reference,
    #    "difference": anomaly
    #})

    output.to_netcdf(
        COMP_DIR / f"{name}_composites.nc"
    )
    
    print(f"Composites saved: {name}_composites.nc")
    

# ============================================================
# 8. MAIN
# ============================================================

def main():

    print("=" * 60)
    print("VIMF PROJECT")
    print("Seasonal moisture-flux composite analysis")
    print("=" * 60)

    # Build classification from original CSV files
    classification = build_classification()

    # Load ERA5
    ds = load_era5()

    # Validate common dates
    common_dates = validate_dates(
        ds, classification
    )

    # Restrict classification to common dates
    classification = classification.loc[
        classification.index.isin(common_dates)
    ]

    print("\nGenerating seasonal composites...")

    for season, phase in CASES:

        target, reference, anomaly, nt, nr = make_case(
            ds,
            classification,
            season,
            phase
        )

        plot_case(
            anomaly,
            season,
            phase,
            nt,
            nr
        )

        save_composites(
            target,
            reference,
            anomaly,
            season,
            phase
        )

    ds.close()

    print("\nAnalysis completed.")
    print(f"Figures: {FIG_DIR.resolve()}")
    print(f"Composites: {COMP_DIR.resolve()}")


if __name__ == "__main__":
    main()

