
import pandas as pd

from decision.config import (
    DAILY_REQUIREMENTS,
    RELIEF_DAYS,
    UNIT_WEIGHT_KG,
    CAMP_INITIAL_STOCK_KG
)


def calculate_village_demand(village_df):

    df = village_df.copy()

    resources = [
        "food",
        "water",
        "medicine"
    ]

    for resource in resources:

        inventory_column = f"{resource}_inventory_units"

        # Convert existing inventory into kg
        current_inventory_kg = (
            df[inventory_column]
            * UNIT_WEIGHT_KG[resource]
        )

        # Calculate required quantity
        demand_kg = (
            df["population"]
            * DAILY_REQUIREMENTS[resource]
            * RELIEF_DAYS
        )

        # Calculate unmet demand
        unmet_demand_kg = (
            demand_kg - current_inventory_kg
        ).clip(lower=0)

        df[f"{resource}_demand_kg"] = demand_kg

        df[f"{resource}_inventory_kg"] = (
            current_inventory_kg
        )

        df[f"{resource}_unmet_kg"] = (
            unmet_demand_kg
        )

    return df


def create_camp_inventory(camp_names):

    """
    Generate deterministic initial stock for each camp.

    All camps receive the same illustrative starting stock.
    """

    inventory = {}

    for camp in camp_names:

        inventory[camp] = {
            resource: quantity
            for resource, quantity
            in CAMP_INITIAL_STOCK_KG.items()
        }

    return inventory


def allocate_resources(
    village_df,
    allocation_df,
    vehicle_df
):

    """
    Allocate resources using existing vehicle recommendations.

    A shipment is limited by:
    1. Village unmet demand
    2. Relief camp stock
    3. Vehicle carrying capacity
    """

    villages = calculate_village_demand(village_df)

    # Keep only villages with a vehicle recommendation
    assignments = allocation_df[
        allocation_df["dispatch_status"]
        == "Vehicle Recommended"
    ].copy()

    # Process highest-priority villages first
    assignments = assignments.sort_values(
        "priority_score",
        ascending=False
    )

    # Generate initial camp inventory
    camp_names = villages[
        "nearest_relief_camp"
    ].dropna().unique()

    camp_stock = create_camp_inventory(camp_names)

    # Store vehicle capacities
    vehicle_capacity = (
        vehicle_df.set_index("assigned_vehicle_id")
        ["vehicle_capacity_kg"]
        .to_dict()
    )

    results = []

    for _, assignment in assignments.iterrows():

        village_id = assignment["village_id"]

        village_match = villages[
            villages["village_id"] == village_id
        ]

        if village_match.empty:
            continue

        village = village_match.iloc[0]

        camp = village["nearest_relief_camp"]

        vehicle_id = assignment["vehicle_id"]

        capacity = float(
            vehicle_capacity.get(vehicle_id, 0)
        )

        if camp not in camp_stock:
            continue

        # Available quantities from the camp
        requested = {}

        resources = [
            "food",
            "water",
            "medicine"
        ]

        for resource in resources:

            unmet = float(
                village[f"{resource}_unmet_kg"]
            )

            stock = float(
                camp_stock[camp][resource]
            )

            requested[resource] = min(
                unmet,
                stock
            )

        total_requested = sum(requested.values())

        # Fit shipment within vehicle capacity
        if total_requested > capacity and total_requested > 0:

            scale = capacity / total_requested

        else:

            scale = 1.0

        shipment = {}

        for resource in resources:

            quantity = requested[resource] * scale

            shipment[resource] = quantity

            # Deduct dispatched quantity from camp stock
            camp_stock[camp][resource] -= quantity

        total_shipment = sum(shipment.values())

        results.append({

            "village_id": village_id,

            "priority_score": assignment["priority_score"],

            "relief_camp": camp,

            "vehicle_id": vehicle_id,

            "vehicle_capacity_kg": capacity,

            "food_allocated_kg": shipment["food"],

            "water_allocated_kg": shipment["water"],

            "medicine_allocated_kg": shipment["medicine"],

            "total_shipment_kg": total_shipment,

            "remaining_vehicle_capacity_kg": (
                capacity - total_shipment
            ),

            "allocation_status": (
                "Resources Allocated"
                if total_shipment > 0
                else "No Resources Available"
            )

        })

    return pd.DataFrame(results), camp_stock
