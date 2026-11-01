
import pandas as pd


RESOURCE_COLUMNS = {
    "Food": "food_inventory_units",
    "Water": "water_inventory_units",
    "Medicine": "medicine_inventory_units"
}


def calculate_resource_shortages(village_df):

    df = village_df.copy()

    # Calculate relative shortage for each resource.
    # Lower inventory compared with other villages
    # means a higher shortage score.

    for resource, column in RESOURCE_COLUMNS.items():

        inventory_percentile = df[column].rank(
            pct=True,
            method="average"
        )

        df[f"{resource.lower()}_shortage_score"] = (
            1 - inventory_percentile
        ) * 100

    shortage_columns = [
        "food_shortage_score",
        "water_shortage_score",
        "medicine_shortage_score"
    ]

    # Average shortage across all three resources
    df["overall_shortage_score"] = (
        df[shortage_columns].mean(axis=1)
    )

    # Highest shortage first
    df = df.sort_values(
        "overall_shortage_score",
        ascending=False
    ).reset_index(drop=True)

    return df
