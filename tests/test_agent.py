
from simulation.disaster import (
    load_disaster_data,
    get_latest_village_state,
    get_latest_vehicle_state
)

from decision.agent import run_resource_allocation_agent


def get_agent_result():
    df = load_disaster_data()

    villages = get_latest_village_state(df)
    vehicles = get_latest_vehicle_state(df)

    return run_resource_allocation_agent(villages, vehicles)


def test_agent_returns_all_required_outputs():
    result = get_agent_result()

    required_keys = [
        "prioritized_villages",
        "resource_shortages",
        "vehicle_assignments",
        "resource_allocations",
        "camp_stock",
        "unserved_villages",
        "validation",
        "summary"
    ]

    for key in required_keys:
        assert key in result


def test_all_villages_are_evaluated():
    result = get_agent_result()

    assert result["summary"]["total_villages"] == 250


def test_priority_counts_are_consistent():
    result = get_agent_result()
    summary = result["summary"]

    total = (
        summary["critical_villages"]
        + summary["high_priority_villages"]
        + summary["moderate_priority_villages"]
    )

    assert total == summary["total_villages"]


def test_vehicle_assignments_are_unique():
    result = get_agent_result()

    assignments = result["vehicle_assignments"]

    recommended = assignments[
        assignments["dispatch_status"] == "Vehicle Recommended"
    ]

    assert recommended["vehicle_id"].is_unique


def test_resource_shipments_do_not_exceed_capacity():
    result = get_agent_result()

    shipments = result["resource_allocations"]
    assignments = result["vehicle_assignments"]

    capacities = assignments.set_index(
        "vehicle_id"
    )["vehicle_capacity_kg"].to_dict()

    for _, shipment in shipments.iterrows():
        vehicle_id = shipment["vehicle_id"]

        assert (
            shipment["total_shipment_kg"]
            <= capacities[vehicle_id] + 0.001
        )


def test_agent_validation_passes():
    result = get_agent_result()

    assert result["validation"]["status"] == "Passed"
    assert len(result["validation"]["errors"]) == 0
