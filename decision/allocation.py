
import pandas as pd


def check_vehicle_compatibility(vehicle_type, road_status):

    vehicle_type = str(vehicle_type).strip().lower()
    road_status = str(road_status).strip().lower()

    compatibility = {
        "truck": ["open"],
        "rescue boat": ["flooded"],
        "helicopter": ["open", "flooded", "blocked"]
    }

    return road_status in compatibility.get(vehicle_type, [])


def allocate_vehicles(village_df, vehicle_df):

    villages = village_df.copy()
    vehicles = vehicle_df.copy()

    # Sort villages by highest priority first
    villages = villages.sort_values(
        "new_priority_score",
        ascending=False
    ).reset_index(drop=True)

    # Identify available vehicles
    available = vehicles[
        vehicles["vehicle_status"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "available"
    ].copy()

    used_vehicles = set()
    assignments = []

    for _, village in villages.iterrows():

        road_status = village["access_road_status"]

        # Find all compatible vehicles
        compatible_fleet = vehicles[
            vehicles["vehicle_type"].apply(
                lambda x: check_vehicle_compatibility(
                    x, road_status
                )
            )
        ]

        # Find available compatible vehicles
        compatible_available = available[
            available["vehicle_type"].apply(
                lambda x: check_vehicle_compatibility(
                    x, road_status
                )
            )
        ]

        # Exclude already assigned vehicles
        candidates = compatible_available[
            ~compatible_available["assigned_vehicle_id"].isin(
                used_vehicles
            )
        ]

        if not candidates.empty:

            selected = candidates.iloc[0]

            vehicle_id = selected["assigned_vehicle_id"]

            used_vehicles.add(vehicle_id)

            assignments.append({
                "village_id": village["village_id"],
                "priority_score": village["new_priority_score"],
                "priority_level": village["new_priority_level"],
                "road_status": road_status,
                "vehicle_id": vehicle_id,
                "vehicle_type": selected["vehicle_type"],
                "vehicle_capacity_kg": selected["vehicle_capacity_kg"],
                "dispatch_status": "Vehicle Recommended",
                "reason": "Compatible available vehicle assigned"
            })

        else:

            if compatible_fleet.empty:
                reason = "No compatible vehicle type in fleet"

            elif compatible_available.empty:
                reason = "Compatible vehicles are unavailable"

            else:
                reason = "All compatible vehicles assigned this round"

            assignments.append({
                "village_id": village["village_id"],
                "priority_score": village["new_priority_score"],
                "priority_level": village["new_priority_level"],
                "road_status": road_status,
                "vehicle_id": "Not Assigned",
                "vehicle_type": "None",
                "vehicle_capacity_kg": 0,
                "dispatch_status": "Unserved",
                "reason": reason
            })

    return pd.DataFrame(assignments)
