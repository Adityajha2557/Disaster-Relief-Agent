
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


PRIORITY_COLORS = {
    "Critical": "#ef4444",
    "High": "#f59e0b",
    "Moderate": "#22c55e"
}


def render_disaster_map(
    village_df,
    vehicle_df=None,
    agent_result=None,
    title="Disaster Operations Map"
):

    st.subheader(title)

    st.caption(
        "SIMULATION MAP | Village coordinates are dataset-based. "
        "Camp positions, vehicle positions and routes are illustrative."
    )

    villages = village_df.copy()

    required = ["latitude", "longitude", "village_id"]

    if not all(column in villages.columns for column in required):
        st.error("Required map coordinates are missing.")
        return

    villages["latitude"] = pd.to_numeric(
        villages["latitude"], errors="coerce"
    )

    villages["longitude"] = pd.to_numeric(
        villages["longitude"], errors="coerce"
    )

    villages = villages.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    villages = villages[
        villages["latitude"].between(-90, 90)
        & villages["longitude"].between(-180, 180)
    ]

    if villages.empty:
        st.warning("No valid village coordinates found.")
        return

    villages["map_status"] = "Awaiting Agent"
    villages["shipment_kg"] = 0.0
    villages["assigned_vehicle"] = "Not assigned"

    if agent_result is not None:

        assignments = agent_result["vehicle_assignments"].copy()
        shipments = agent_result["resource_allocations"].copy()

        if not assignments.empty:

            assignments["village_id"] = (
                assignments["village_id"].astype(str)
            )

            status_lookup = assignments.set_index(
                "village_id"
            )["dispatch_status"].to_dict()

            vehicle_lookup = assignments.set_index(
                "village_id"
            )["vehicle_id"].to_dict()

            villages["map_status"] = (
                villages["village_id"].astype(str)
                .map(status_lookup)
                .fillna("Not assigned")
            )

            villages["assigned_vehicle"] = (
                villages["village_id"].astype(str)
                .map(vehicle_lookup)
                .fillna("Not assigned")
            )

        if not shipments.empty:

            shipment_lookup = {
                str(key): value
                for key, value in
                shipments.groupby("village_id")[
                    "total_shipment_kg"
                ].sum().to_dict().items()
            }

            villages["shipment_kg"] = (
                villages["village_id"].astype(str)
                .map(shipment_lookup)
                .fillna(0)
            )

    if "new_priority_level" not in villages.columns:
        villages["new_priority_level"] = "Unclassified"

    for column in [
        "population",
        "flood_severity",
        "access_road_status",
        "new_priority_score"
    ]:
        if column not in villages.columns:
            villages[column] = "Unknown"

    center_lat = villages["latitude"].mean()
    center_lon = villages["longitude"].mean()

    fig = go.Figure()

    # --------------------------------------------------
    # RELIEF CAMPS - ILLUSTRATIVE LOCATIONS
    # --------------------------------------------------

    camp_positions = {}

    if "nearest_relief_camp" in villages.columns:

        camps = (
            villages.dropna(subset=["nearest_relief_camp"])
            .groupby("nearest_relief_camp")
            .agg(
                latitude=("latitude", "mean"),
                longitude=("longitude", "mean")
            )
            .reset_index()
        )

        for _, camp in camps.iterrows():

            camp_name = str(camp["nearest_relief_camp"])

            camp_positions[camp_name] = (
                float(camp["latitude"]),
                float(camp["longitude"])
            )

        if not camps.empty:

            fig.add_trace(go.Scattermap(
                lat=camps["latitude"],
                lon=camps["longitude"],
                mode="markers+text",
                name="Illustrative Relief Camps",
                text=camps["nearest_relief_camp"].astype(str),
                textposition="top right",
                marker=dict(
                    size=15,
                    color="#2563eb",
                    symbol="square"
                ),
                hovertemplate=(
                    "<b>Illustrative Relief Camp</b><br>"
                    "%{text}<extra></extra>"
                )
            ))

    # --------------------------------------------------
    # SIMULATED ROUTES AFTER AGENT EXECUTION
    # --------------------------------------------------

    if agent_result is not None:

        route_lat = []
        route_lon = []

        for _, village in villages.iterrows():

            if village["map_status"] != "Vehicle Recommended":
                continue

            camp = village.get("nearest_relief_camp")

            if pd.isna(camp):
                continue

            camp_position = camp_positions.get(str(camp))

            if camp_position is None:
                continue

            route_lat.extend([
                camp_position[0],
                village["latitude"],
                None
            ])

            route_lon.extend([
                camp_position[1],
                village["longitude"],
                None
            ])

        if route_lat:

            fig.add_trace(go.Scattermap(
                lat=route_lat,
                lon=route_lon,
                mode="lines",
                name="Illustrative Relief Routes",
                line=dict(
                    color="#2563eb",
                    width=3
                ),
                hoverinfo="skip"
            ))

    # --------------------------------------------------
    # VILLAGE MARKERS
    # --------------------------------------------------

    for priority, color in PRIORITY_COLORS.items():

        subset = villages[
            villages["new_priority_level"] == priority
        ]

        if subset.empty:
            continue

        fig.add_trace(go.Scattermap(
            lat=subset["latitude"],
            lon=subset["longitude"],
            mode="markers",
            name=f"{priority} Priority Villages",
            marker=dict(
                size=11,
                color=color,
                opacity=0.9
            ),
            customdata=subset[
                [
                    "village_id",
                    "population",
                    "flood_severity",
                    "access_road_status",
                    "map_status",
                    "assigned_vehicle",
                    "shipment_kg"
                ]
            ].astype(str).values,
            hovertemplate=(
                "<b>Village: %{customdata[0]}</b><br>"
                "Population: %{customdata[1]}<br>"
                "Flood Severity: %{customdata[2]}<br>"
                "Road Status: %{customdata[3]}<br>"
                "Agent Status: %{customdata[4]}<br>"
                "Vehicle: %{customdata[5]}<br>"
                "Shipment: %{customdata[6]} kg"
                "<extra></extra>"
            )
        ))

    # --------------------------------------------------
    # VEHICLE MARKERS AFTER AGENT EXECUTION
    # --------------------------------------------------

    if agent_result is not None:

        assigned = villages[
            villages["map_status"] == "Vehicle Recommended"
        ].copy()

        if not assigned.empty:

            assigned["vehicle_lat"] = [
                lat + (index + 1) * 0.001
                for index, lat in enumerate(assigned["latitude"])
            ]

            assigned["vehicle_lon"] = [
                lon + (index + 1) * 0.001
                for index, lon in enumerate(assigned["longitude"])
            ]

            fig.add_trace(go.Scattermap(
                lat=assigned["vehicle_lat"],
                lon=assigned["vehicle_lon"],
                mode="markers",
                name="Assigned Vehicles (Simulated)",
                marker=dict(
                    size=15,
                    color="#111827",
                    symbol="car"
                ),
                text=assigned["assigned_vehicle"].astype(str),
                hovertemplate=(
                    "<b>Simulated Vehicle</b><br>"
                    "Vehicle ID: %{text}<extra></extra>"
                )
            ))

    # --------------------------------------------------
    # MAP LAYOUT - MAPLIBRE
    # --------------------------------------------------

    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(
                lat=center_lat,
                lon=center_lon
            ),
            zoom=8
        ),
        height=620,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            x=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # MAP SUMMARY
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("Villages on Map", len(villages))

    col2.metric(
        "Critical Villages",
        int(
            (villages["new_priority_level"] == "Critical").sum()
        )
    )

    col3.metric(
        "Villages with Shipments",
        int((villages["shipment_kg"] > 0).sum())
    )

    if agent_result is None:

        st.info(
            "Pre-agent view: current village conditions "
            "and illustrative relief camps."
        )

    else:

        st.success(
            "Post-agent view: vehicle assignments, "
            "shipment destinations and illustrative routes."
        )
