
import streamlit as st
import pandas as pd

from simulation.disaster import (
    load_disaster_data,
    get_latest_village_state,
    get_latest_vehicle_state
)

from simulation.events import apply_disaster_event

from decision.priority import calculate_priority
from decision.resources import calculate_resource_shortages
from decision.allocation import allocate_vehicles
from decision.resource_allocation import allocate_resources
from decision.agent import run_resource_allocation_agent

from dashboard.agent_panel import render_agent_panel
from dashboard.map_view import render_disaster_map


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="DRRAA | Disaster Relief Agent",
    page_icon="🚨",
    layout="wide"
)


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_data():

    df = load_disaster_data()

    villages = get_latest_village_state(df)
    vehicles = get_latest_vehicle_state(df)

    return df, villages, vehicles


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "villages" not in st.session_state:

    df, villages, vehicles = load_data()

    st.session_state.df = df
    st.session_state.villages = villages
    st.session_state.vehicles = vehicles

if "event_history" not in st.session_state:
    st.session_state.event_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("DRRAA")
st.sidebar.caption("Disaster Relief Resource Allocation Agent")
st.sidebar.divider()

st.sidebar.subheader("Simulation Controls")

event_type = st.sidebar.selectbox(
    "Select Disaster Event",
    [
        "None",
        "Heavy Rainfall",
        "Road Blockage",
        "Vehicle Breakdown",
        "Flooding"
    ]
)

if st.sidebar.button("Trigger Event", use_container_width=True):

    if event_type != "None":

        villages, vehicles, message = apply_disaster_event(
            st.session_state.villages,
            st.session_state.vehicles,
            event_type
        )

        st.session_state.villages = villages
        st.session_state.vehicles = vehicles

        st.session_state.event_history.append({
            "event": event_type,
            "message": message
        })

        st.session_state.agent_result = None

        st.sidebar.success(message)
        st.rerun()


st.sidebar.divider()

if st.sidebar.button("Reset Simulation", use_container_width=True):

    _, villages, vehicles = load_data()

    st.session_state.villages = villages
    st.session_state.vehicles = vehicles
    st.session_state.event_history = []
    st.session_state.messages = []
    st.session_state.agent_result = None

    st.rerun()


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.title("Disaster Relief Resource Allocation Agent")

st.caption(
    "AI-assisted disaster simulation, prioritization "
    "and relief resource allocation."
)

st.info(
    "The dataset is synthetic and AI-generated. "
    "Map routes, camp positions and vehicle positions are illustrative. "
    "This is a decision-support simulation, not a live emergency system."
)


# --------------------------------------------------
# CURRENT SIMULATION CALCULATIONS
# --------------------------------------------------

prioritized_df = calculate_priority(
    st.session_state.villages
)

shortage_df = calculate_resource_shortages(
    prioritized_df
)

vehicle_allocations = allocate_vehicles(
    prioritized_df,
    st.session_state.vehicles
)

resource_allocations, camp_stock = allocate_resources(
    prioritized_df,
    vehicle_allocations,
    st.session_state.vehicles
)


# --------------------------------------------------
# DASHBOARD TABS
# --------------------------------------------------

overview_tab, village_tab, allocation_tab, agent_tab, ai_tab = st.tabs([
    "Overview",
    "Village Status",
    "Resource Allocation",
    "Resource Allocation Agent",
    "AI Operations Assistant"
])


# ==================================================
# OVERVIEW TAB - BEFORE AGENT MAP
# ==================================================

with overview_tab:

    st.header("Disaster Situation Overview")

    total_villages = len(prioritized_df)

    critical_count = (
        prioritized_df["new_priority_level"] == "Critical"
    ).sum()

    high_count = (
        prioritized_df["new_priority_level"] == "High"
    ).sum()

    moderate_count = (
        prioritized_df["new_priority_level"] == "Moderate"
    ).sum()

    available_vehicles = (
        st.session_state.vehicles["vehicle_status"]
        .astype(str)
        .str.strip()
        .str.lower() == "available"
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Villages", total_villages)
    col2.metric("Critical Villages", int(critical_count))
    col3.metric("High Priority", int(high_count))
    col4.metric("Moderate Priority", int(moderate_count))

    col1, col2 = st.columns(2)

    col1.metric("Available Vehicles", int(available_vehicles))

    col2.metric(
        "Triggered Events",
        len(st.session_state.event_history)
    )

    st.divider()

    st.header("Pre-Agent Disaster Map")

    render_disaster_map(
        prioritized_df,
        st.session_state.vehicles,
        agent_result=None,
        title="Current Disaster Situation"
    )

    st.divider()

    st.subheader("Village Priority Distribution")

    priority_chart = (
        prioritized_df["new_priority_level"]
        .value_counts()
        .reindex(
            ["Critical", "High", "Moderate"],
            fill_value=0
        )
    )

    st.bar_chart(priority_chart)

    st.subheader("Recent Disaster Events")

    if st.session_state.event_history:

        for event in reversed(st.session_state.event_history):
            st.write(
                f"**{event['event']}** — {event['message']}"
            )

    else:

        st.info("No dynamic events have been triggered.")


# ==================================================
# VILLAGE STATUS TAB
# ==================================================

with village_tab:

    st.header("Village Priority Assessment")

    st.dataframe(
        prioritized_df[
            [
                "village_id",
                "population",
                "flood_severity",
                "new_priority_score",
                "new_priority_level"
            ]
        ].sort_values(
            "new_priority_score",
            ascending=False
        ),
        use_container_width=True
    )

    st.divider()

    st.subheader("Resource Shortage Analysis")

    st.dataframe(
        shortage_df[
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


# ==================================================
# RESOURCE ALLOCATION TAB
# ==================================================

with allocation_tab:

    st.header("Vehicle Allocation")

    st.dataframe(
        vehicle_allocations,
        use_container_width=True
    )

    st.divider()

    st.header("Resource Distribution")

    if not resource_allocations.empty:

        st.dataframe(
            resource_allocations,
            use_container_width=True
        )

    else:

        st.warning("No resource shipments generated.")

    st.divider()

    st.subheader("Relief Camp Inventory")

    if camp_stock:

        camp_df = pd.DataFrame.from_dict(
            camp_stock,
            orient="index"
        )

        camp_df.index.name = "Relief Camp"

        st.dataframe(
            camp_df,
            use_container_width=True
        )


# ==================================================
# AGENT TAB - AFTER AGENT MAP
# ==================================================

with agent_tab:

    st.header("Resource Allocation Agent")

    st.write(
        "The agent evaluates the current disaster situation, "
        "ranks villages, assigns vehicles and recommends "
        "relief resource shipments."
    )

    if st.button(
        "Run Resource Allocation Agent",
        type="primary",
        use_container_width=True
    ):

        with st.spinner("Agent is analysing the disaster situation..."):

            try:

                result = run_resource_allocation_agent(
                    st.session_state.villages,
                    st.session_state.vehicles
                )

                st.session_state.agent_result = result

                st.success(
                    "Resource Allocation Agent executed successfully!"
                )

            except Exception as error:

                st.session_state.agent_result = None

                st.error(f"Agent execution failed: {error}")

    st.divider()

    if st.session_state.agent_result is not None:

        render_agent_panel(
            st.session_state.agent_result
        )

        st.divider()

        st.header("Post-Agent Operations Map")

        render_disaster_map(
            st.session_state.agent_result["prioritized_villages"],
            st.session_state.vehicles,
            agent_result=st.session_state.agent_result,
            title="Agent Allocation Results"
        )

    else:

        st.info(
            "The agent has not run yet. "
            "The pre-agent disaster map is available in the Overview tab. "
            "Run the agent to see allocation decisions on this map."
        )


# ==================================================
# AI OPERATIONS ASSISTANT
# ==================================================

with ai_tab:

    st.header("AI Operations Assistant")

    st.caption(
        "Ask questions about the current disaster simulation."
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask about village priorities, vehicles or resources..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        simulation_context = {

            "dataset_type": "Synthetic AI-generated dataset",

            "total_villages": len(prioritized_df),

            "priority_counts": (
                prioritized_df["new_priority_level"]
                .value_counts()
                .to_dict()
            ),

            "top_priority_villages": (
                prioritized_df.sort_values(
                    "new_priority_score",
                    ascending=False
                ).head(10).to_dict("records")
            ),

            "resource_shortages": (
                shortage_df.head(10).to_dict("records")
            ),

            "vehicle_summary": (
                vehicle_allocations["dispatch_status"]
                .value_counts()
                .to_dict()
            ),

            "vehicle_assignments": (
                vehicle_allocations.head(15).to_dict("records")
            ),

            "resource_allocations": (
                resource_allocations.head(15).to_dict("records")
            ),

            "camp_stock": camp_stock,

            "event_history": st.session_state.event_history,

            "agent_summary": (
                st.session_state.agent_result["summary"]
                if st.session_state.agent_result is not None
                else "Agent has not been executed."
            ),

            "limitations": [
                "Dataset is synthetic and AI-generated.",
                "Resource requirements use illustrative assumptions.",
                "Camp locations are illustrative map positions.",
                "Vehicle positions and routes are simulated.",
                "Recommendations are not real-world dispatch orders."
            ]
        }

        with st.chat_message("assistant"):

            with st.spinner("Analysing simulation data..."):

                try:

                    from ai.assistant import ask_assistant

                    answer = ask_assistant(
                        question,
                        simulation_context
                    )

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:

                    error_message = f"AI Assistant error: {error}"

                    st.error(error_message)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
