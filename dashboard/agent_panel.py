
import streamlit as st
import pandas as pd


def render_agent_panel(result):
    st.header("🤖 Resource Allocation Agent")

    st.caption(
        "Review the decisions made by the DRRAA allocation engine."
    )

    if not result:
        st.info("Run the Resource Allocation Agent to generate decisions.")
        return

    summary = result["summary"]

    st.subheader("Agent Execution Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Villages Evaluated", summary["total_villages"])
    col2.metric("Critical Villages", summary["critical_villages"])
    col3.metric("Vehicles Recommended", summary["vehicles_recommended"])
    col4.metric("Unserved Villages", summary["unserved_villages"])

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Villages Receiving Resources",
        summary["villages_receiving_resources"]
    )

    col2.metric(
        "Total Resources Allocated",
        f'{summary["total_resources_allocated_kg"]:,.2f} kg'
    )

    col3.metric(
        "Validation",
        summary["validation_status"]
    )

    st.divider()

    st.subheader("1. Village Priority Assessment")

    priorities = result["prioritized_villages"]

    st.dataframe(
        priorities[
            [
                "village_id",
                "population",
                "flood_severity",
                "new_priority_score",
                "new_priority_level"
            ]
        ].sort_values("new_priority_score", ascending=False),
        use_container_width=True
    )

    st.subheader("2. Resource Shortage Analysis")

    shortages = result["resource_shortages"]

    st.dataframe(
        shortages[
            [
                "village_id",
                "food_shortage_score",
                "water_shortage_score",
                "medicine_shortage_score",
                "overall_shortage_score"
            ]
        ],
        use_container_width=True
    )

    st.subheader("3. Vehicle Allocation Decisions")

    st.dataframe(
        result["vehicle_assignments"],
        use_container_width=True
    )

    st.subheader("4. Resource Distribution Decisions")

    shipments = result["resource_allocations"]

    if not shipments.empty:
        st.dataframe(shipments, use_container_width=True)

    else:
        st.warning("No resource shipments were generated.")

    st.subheader("5. Unserved Villages")

    unserved = result["unserved_villages"]

    if not unserved.empty:
        st.dataframe(unserved, use_container_width=True)
    else:
        st.success("All evaluated villages received vehicle recommendations.")

    st.subheader("6. Relief Camp Inventory")

    camp_stock = result["camp_stock"]

    if camp_stock:
        camp_df = pd.DataFrame.from_dict(
            camp_stock,
            orient="index"
        )
        camp_df.index.name = "Relief Camp"

        st.dataframe(camp_df, use_container_width=True)

    st.subheader("7. Agent Validation")

    validation = result["validation"]

    if validation["status"] == "Passed":
        st.success("All implemented allocation validation checks passed.")
    else:
        st.error("Allocation validation failed.")

    for error in validation["errors"]:
        st.error(error)

    for warning in validation["warnings"]:
        st.warning(warning)
