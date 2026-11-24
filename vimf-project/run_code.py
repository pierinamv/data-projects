
from pathlib import Path
import glob
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

# ============================================================
# 1. CONFIGURATION
# ============================================================

DATA_DIR = Path("./ERA5")
CLASS_FILE = Path("./olivia_classification.csv")
OUT_DIR = Path("./results")

OUT_DIR.mkdir(exist_ok=True)

# Adapt these patterns to your downloaded files
FILES = sorted(glob.glob(str(DATA_DIR / "*.nc")))

START_DATE = "1980-01-01"
END_DATE = "2020-12-31"

# Spatial domain: 5S-20S, 140E-0E
LAT_MIN, LAT_MAX = -20, -5
LON_MIN, LON_MAX = -220, 0

# "all": all months of the corresponding ENSO phase.
# "non_drought": only non-drought months of that ENSO phase.
REFERENCE = "all"

# Plot resolution
QUIVER_STEP = 4

# Variable names in ERA5
VAR_U = "viwve"
VAR_V = "viwvn"
VAR_DIV = "viwvd"

# Four target comparisons
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
# 2. READ MONTHLY CLASSIFICATION
# ============================================================

def read_classification(filename):

    df = pd.read_csv(filename)

    required = {"date", "enso_phase", "drought"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["date"] = pd.to_datetime(df["date"]).dt.to_period(
        "M"
    ).dt.to_timestamp()

    df["enso_phase"] = (
        df["enso_phase"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({
            "el niño": "El Nino",
            "el nino": "El Nino",
            "elnino": "El Nino",
            "la niña": "La Nina",
            "la nina": "La Nina",
            "lanina": "La Nina",
            "neutral": "Neutral",
        })
    )

    if df["drought"].dtype != bool:
        mapping = {
            "true": True, "1": True, "yes": True, "dry": True,
            "false": False, "0": False, "no": False, "wet": False
        }
        df["drought"] = (
            df["drought"].astype(str).str.lower().str.strip()
            .map(mapping)
        )

    if df["drought"].isna().any():
        raise ValueError("Unrecognized or missing drought values.")

    if df["date"].duplicated().any():
        raise ValueError("Classification contains duplicated months.")

    df = df.set_index("date").sort_index()

    return df.loc[START_DATE:END_DATE]


# ============================================================
# 3. READ AND PREPARE ERA5
# ============================================================

def load_era5(files):

    if not files:
        raise FileNotFoundError("No NetCDF files found.")

    ds = xr.open_mfdataset(
        files,
        combine="by_coords",
        chunks={"time": 120},
        parallel=True
    )

    # Standardize longitude to [-360, 0]
    lon = ds.longitude
    if float(lon.max()) > 180:
        ds = ds.assign_coords(
            longitude=xr.where(lon > 0, lon - 360, lon)
        )

    ds = ds.sortby("longitude").sortby("latitude")

    # Select the region
    ds = ds.sel(
        latitude=slice(LAT_MIN, LAT_MAX),
        longitude=slice(LON_MIN, LON_MAX)
    )

    # Some datasets have latitude in descending order.
    # The previous slice assumes ascending coordinates.
    if ds.latitude.size == 0:
        ds = ds.sel(
            latitude=slice(LAT_MAX, LAT_MIN),
            longitude=slice(LON_MIN, LON_MAX)
        )

    # Select period
    ds = ds.sel(time=slice(START_DATE, END_DATE))

    # Monthly data are expected.
    # If submonthly data were downloaded, average to monthly means.
    ds = ds.resample(time="MS").mean()

    # Keep only necessary variables
    ds = ds[[VAR_U, VAR_V, VAR_DIV]]

    # Rename for convenience
    ds = ds.rename({
        VAR_U: "IVT_u",
        VAR_V: "IVT_v",
        VAR_DIV: "IVT_div"
    })

    # Moisture flux convergence = - divergence
    ds["MFC"] = -ds["IVT_div"]

    # IVT magnitude
    ds["IVT"] = np.hypot(ds["IVT_u"], ds["IVT_v"])

    return ds


# ============================================================
# 4. ASSIGN SEASONS
# ============================================================

def select_season(df, season):

    months = SEASON_MONTHS[season]

    return df[df.index.month.isin(months)]


# ============================================================
# 5. BUILD COMPOSITES
# ============================================================

def composite(ds, dates):

    dates = pd.DatetimeIndex(dates)

    # Only use dates actually present in ERA5
    available = pd.DatetimeIndex(ds.time.values)

    dates = dates.intersection(available)

    if len(dates) == 0:
        raise ValueError("No matching dates in ERA5.")

    result = ds.sel(time=dates).mean("time")

    return result, len(dates)


def make_case(ds, classification, season, phase):

    table = select_season(classification, season)

    # Drought months in the selected ENSO phase
    target_dates = table.index[
        (table["enso_phase"] == phase) &
        (table["drought"])
    ]

    # Reference months in the same ENSO phase and season
    reference_mask = table["enso_phase"] == phase

    if REFERENCE == "non_drought":
        reference_mask &= ~table["drought"]

    reference_dates = table.index[reference_mask]

    target, n_target = composite(ds, target_dates)
    reference, n_reference = composite(ds, reference_dates)

    # Difference: drought composite - ENSO reference
    anomaly = target - reference

    print(
        f"{season} | {phase}: "
        f"target n={n_target}, reference n={n_reference}"
    )

    return target, reference, anomaly, n_target, n_reference


# ============================================================
# 6. PLOT COMPOSITE DIFFERENCES
# ============================================================

def plot_case(anomaly, target, reference,
              season, phase, n_target, n_reference):

    lon = anomaly.longitude.values
    lat = anomaly.latitude.values

    X, Y = np.meshgrid(lon, lat)

    fig, axes = plt.subplots(
        1, 2, figsize=(15, 6),
        constrained_layout=True
    )

    # ----------------------------------------
    # Panel A: IVT anomaly vectors
    # ----------------------------------------

    ax = axes[0]

    U = anomaly["IVT_u"].values
    V = anomaly["IVT_v"].values

    magnitude = anomaly["IVT"].values

    levels = np.linspace(
        np.nanpercentile(magnitude, 5),
        np.nanpercentile(magnitude, 95),
        12
    )

    cf = ax.contourf(
        X, Y, magnitude,
        levels=levels,
        cmap="YlOrRd",
        extend="both"
    )

    step = QUIVER_STEP

    q = ax.quiver(
        X[::step, ::step],
        Y[::step, ::step],
        U[::step, ::step],
        V[::step, ::step],
        color="black",
        scale=None
    )

    ax.quiverkey(
        q, 0.85, 1.04, 10,
        "10 kg m$^{-1}$ s$^{-1}$",
        labelpos="E"
    )

    fig.colorbar(
        cf, ax=ax,
        label="Difference in IVT magnitude (kg m$^{-1}$ s$^{-1}$)"
    )

    ax.set_title("IVT anomaly: drought − ENSO reference")

    # ----------------------------------------
    # Panel B: MFC anomaly
    # ----------------------------------------

    ax = axes[1]

    mfc = anomaly["MFC"].values

    vmax = np.nanpercentile(np.abs(mfc), 98)
    vmax = max(vmax, 1e-12)

    levels = np.linspace(-vmax, vmax, 17)

    cf = ax.contourf(
        X, Y, mfc,
        levels=levels,
        cmap="RdBu",
        extend="both"
    )

    fig.colorbar(
        cf, ax=ax,
        label="MFC anomaly (kg m$^{-2}$ s$^{-1}$)"
    )

    ax.set_title("Moisture-flux convergence anomaly")

    # ----------------------------------------
    # Common formatting
    # ----------------------------------------

    for ax in axes:
        ax.set_xlim(LON_MIN, LON_MAX)
        ax.set_ylim(LAT_MIN, LAT_MAX)

        ax.set_xlabel("Longitude (degrees)")
        ax.set_ylabel("Latitude (degrees)")

        ax.grid(alpha=0.25)

    fig.suptitle(
        f"{season} | {phase} drought "
        f"(n={n_target}) vs ENSO reference "
        f"(n={n_reference})",
        fontsize=14
    )

    filename = (
        f"{season}_{phase.replace(' ', '_')}_"
        f"{REFERENCE}.png"
    )

    fig.savefig(
        OUT_DIR / filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# 7. SAVE RESULTS
# ============================================================

def save_composites(target, reference, anomaly,
                    season, phase):

    name = f"{season}_{phase.replace(' ', '_')}"

    xr.Dataset({
        "target": target,
        "reference": reference,
        "anomaly": anomaly
    }).to_netcdf(OUT_DIR / f"{name}_composites.nc")


# ============================================================
# 8. MAIN
# ============================================================

def main():

    print("Reading monthly classification...")
    classification = read_classification(CLASS_FILE)

    print("Loading ERA5...")
    ds = load_era5(FILES)

    print("Generating seasonal composites...")

    for season, phase in CASES:

        target, reference, anomaly, nt, nr = make_case(
            ds, classification, season, phase
        )

        plot_case(
            anomaly, target, reference,
            season, phase, nt, nr
        )

        save_composites(
            target, reference, anomaly,
            season, phase
        )

    print("\nAnalysis completed.")
    print(f"Results saved in: {OUT_DIR.resolve()}")

    ds.close()


if __name__ == "__main__":
    main()

