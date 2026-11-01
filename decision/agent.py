
import pandas as pd

from decision.priority import calculate_priority
from decision.resources import calculate_resource_shortages
from decision.allocation import allocate_vehicles
from decision.resource_allocation import allocate_resources


def validate_allocations(vehicle_df, vehicle_assignments, resource_allocations):
    """Validate vehicle assignments and resource shipment constraints."""

    errors = []
    warnings = []

    # Check that a vehicle is not assigned to multiple villages.
    recommended = vehicle_assignments[
        vehicle_assignments["dispatch_status"] == "Vehicle Recommended"
    ]

    if recommended["vehicle_id"].duplicated().any():
        errors.append("A vehicle has been assigned to multiple villages.")

    # Check resource shipment capacity.
    if not resource_allocations.empty:
        capacity_lookup = (
            vehicle_df.set_index("assigned_vehicle_id")
            ["vehicle_capacity_kg"].to_dict()
        )

        for _, row in resource_allocations.iterrows():
            vehicle_id = row["vehicle_id"]
            capacity = float(capacity_lookup.get(vehicle_id, 0))
            shipment = float(row["total_shipment_kg"])

            if shipment > capacity + 0.001:
                errors.append(
                    f"Shipment exceeds vehicle capacity for {vehicle_id}."
                )

            if shipment < 0:
                errors.append(
                    f"Negative shipment quantity for {vehicle_id}."
                )

    if recommended.empty:
        warnings.append("No vehicles could be assigned.")

    if resource_allocations.empty:
        warnings.append("No resource shipments were generated.")

    return {
        "status": "Passed" if not errors else "Failed",
        "errors": errors,
        "warnings": warnings
    }


def run_resource_allocation_agent(village_df, vehicle_df):
    """
    Central DRRAA agent.

    Coordinates priority assessment, vehicle assignment,
    resource allocation and validation.

    All decisions are simulation recommendations.
    """

    if village_df.empty:
        raise ValueError("Village dataset is empty.")

    if vehicle_df.empty:
        raise ValueError("Vehicle dataset is empty.")

    # 1. Assess village priorities.
    prioritized_villages = calculate_priority(village_df)

    # 2. Calculate relative resource shortages.
    resource_shortages = calculate_resource_shortages(
        prioritized_villages
    )

    # 3. Assign compatible available vehicles.
    vehicle_assignments = allocate_vehicles(
        prioritized_villages,
        vehicle_df
    )

    # 4. Allocate resources based on demand and vehicle capacity.
    resource_allocations, camp_stock = allocate_resources(
        prioritized_villages,
        vehicle_assignments,
        vehicle_df
    )

    # 5. Identify villages without vehicle assignments.
    unserved_villages = vehicle_assignments[
        vehicle_assignments["dispatch_status"] == "Unserved"
    ].copy()

    # 6. Validate the allocation decisions.
    validation = validate_allocations(
        vehicle_df,
        vehicle_assignments,
        resource_allocations
    )

    # 7. Generate operational summary.
    priority_summary = (
        prioritized_villages["new_priority_level"]
        .value_counts()
        .to_dict()
    )

    total_shipments = (
        float(resource_allocations["total_shipment_kg"].sum())
        if not resource_allocations.empty else 0.0
    )

    summary = {
        "total_villages": len(prioritized_villages),
        "critical_villages": priority_summary.get("Critical", 0),
        "high_priority_villages": priority_summary.get("High", 0),
        "moderate_priority_villages": priority_summary.get("Moderate", 0),
        "vehicles_recommended": len(
            vehicle_assignments[
                vehicle_assignments["dispatch_status"]
                == "Vehicle Recommended"
            ]
        ),
        "unserved_villages": len(unserved_villages),
        "villages_receiving_resources": len(resource_allocations),
        "total_resources_allocated_kg": round(total_shipments, 2),
        "validation_status": validation["status"]
    }

    return {
        "prioritized_villages": prioritized_villages,
        "resource_shortages": resource_shortages,
        "vehicle_assignments": vehicle_assignments,
        "resource_allocations": resource_allocations,
        "camp_stock": camp_stock,
        "unserved_villages": unserved_villages,
        "validation": validation,
        "summary": summary
    }
