
import pandas as pd
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "drraa_cleaned_outputs_drraa_cleaned_dataset.csv"
)


def load_disaster_data():
    """Load the synthetic disaster dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    return pd.read_csv(DATA_PATH)


def get_dataset_summary(df):
    """Generate dataset statistics."""

    return {
        "total_records": len(df),
        "total_villages": df["village_id"].nunique(),
        "total_relief_camps": df["nearest_relief_camp"].nunique(),
        "total_vehicles": df["assigned_vehicle_id"].nunique(),
        "priority_categories": df["priority_level"].nunique()
    }


def prepare_timestamps(df):
    """Convert timestamps into datetime format."""

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    return df.dropna(subset=["timestamp"])


def get_latest_village_state(df):
    """Get the latest record for every village."""

    df = prepare_timestamps(df)

    latest_df = (
        df.sort_values("timestamp")
        .drop_duplicates(
            subset=["village_id"],
            keep="last"
        )
    )

    return latest_df.reset_index(drop=True)


def get_latest_vehicle_state(df):
    """Get the latest record for every vehicle."""

    df = prepare_timestamps(df)

    latest_df = (
        df.sort_values("timestamp")
        .drop_duplicates(
            subset=["assigned_vehicle_id"],
            keep="last"
        )
    )

    return latest_df.reset_index(drop=True)
