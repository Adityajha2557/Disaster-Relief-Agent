
import pandas as pd


def calculate_priority(df):

    df = df.copy()

    # Normalize values between 0 and 1
    df["severity_score"] = (
        df["flood_severity"] / df["flood_severity"].max()
    )

    df["population_score"] = (
        df["population"] / df["population"].max()
    )

    # Calculate resource shortage
    inventory_columns = [
        "food_inventory_units",
        "water_inventory_units",
        "medicine_inventory_units"
    ]

    df["resource_shortage"] = (
        1 - (
            df[inventory_columns].mean(axis=1)
            / df[inventory_columns].max().max()
        )
    ).clip(0, 1)

    # Calculate independent priority score
    df["new_priority_score"] = (
        0.4 * df["severity_score"]
        + 0.3 * df["population_score"]
        + 0.3 * df["resource_shortage"]
    ) * 100

    # Assign priority categories
    def assign_priority(score):
        if score >= 70:
            return "Critical"
        elif score >= 40:
            return "High"
        else:
            return "Moderate"

    df["new_priority_level"] = (
        df["new_priority_score"].apply(assign_priority)
    )

    return df
