
import pandas as pd


def apply_disaster_event(village_df, vehicle_df, event_type):

    villages = village_df.copy()
    vehicles = vehicle_df.copy()

    event_message = ""

    if event_type == "Heavy Rainfall":

        villages["flood_severity"] = (
            villages["flood_severity"] + 2
        ).clip(upper=10)

        event_message = (
            "Heavy rainfall simulated. "
            "Flood severity increased."
        )

    elif event_type == "Road Blockage":

        villages.loc[
            villages.index[0],
            "access_road_status"
        ] = "blocked"

        event_message = (
            "Road blockage simulated for one village."
        )

    elif event_type == "Vehicle Breakdown":

        available = vehicles[
            vehicles["vehicle_status"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "available"
        ]

        if not available.empty:

            vehicle_index = available.index[0]

            vehicles.loc[
                vehicle_index,
                "vehicle_status"
            ] = "Unavailable"

            event_message = (
                "Vehicle breakdown simulated. "
                "One available vehicle is now unavailable."
            )

        else:

            event_message = (
                "No available vehicle was found to simulate a breakdown."
            )

    elif event_type == "Flooding":

        villages.loc[
            villages.index[0],
            "access_road_status"
        ] = "flooded"

        villages.loc[
            villages.index[0],
            "flood_severity"
        ] = 10

        event_message = (
            "Flooding simulated for one village."
        )

    return villages, vehicles, event_message
