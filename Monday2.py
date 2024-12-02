import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page title
st.title("BizDev Dashboard")

# Load data
@st.cache_data  # Cache the data to optimize app performance
def load_data():
    activity_df = pd.read_csv("sdr_activity_metrics_2024_more_variance.csv")
    SDR_df = pd.read_csv("sdr_bizdev_data_2024_refined (1).csv")
return activity_df, SDR_df

activity_df, SDR_df = load_data()

# Ensure Month column is in datetime format
activity_df["Month"] = pd.to_datetime(activity_df["Month"], errors="coerce")
activity_df = activity_df.dropna(subset=["Month"])  # Drop rows with invalid dates

# Display data preview
st.header("Data Preview")
st.subheader("Activity Data")
st.dataframe(activity_df.head())
st.subheader("BizDev Data")
st.dataframe(SDR_df.head())

# Sidebar for filters
st.sidebar.header("Filters")

# Filter for SDR selection
selected_sdr = st.sidebar.selectbox(
    "Select SDR",
    options=["All"] + list(activity_df["SDR"].unique())
)

# Filter for date range (if applicable)
selected_date = st.sidebar.date_input(
    "Select Date Range",
    value=(pd.to_datetime("2024-01-01"), pd.to_datetime("2024-12-31"))
)

# Filter activity data by SDR
if selected_sdr != "All":
    activity_df = activity_df[activity_df["SDR"] == selected_sdr]

# Convert selected_date range to datetime
start_date, end_date = [pd.to_datetime(d) for d in selected_date]

# Filter activity data by date range
activity_df = activity_df[
    (activity_df["Month"] >= start_date) &
    (activity_df["Month"] <= end_date)
]

# Process data for visualizations
annual_activity_df = activity_df.groupby("SDR").agg(
    Total_Calls=("Number_of_Calls", "sum"),
    Total_Emails=("Number_of_Emails", "sum"),
    Total_Talktime=("Talk_Time_Hours", "sum"),
    Total_Demos=("Demo_Bookings", "sum"),
    Total_Opps=("Opportunities_Created", "sum")
).reset_index()

annual_activity_df["Target_Attainment_Percentage"] = (
    annual_activity_df["Total_Opps"] / 60 * 100
)

# Visualization: Target Attainment
import plotly.express as px
import streamlit as st

# Sort the data by "Target_Attainment_Percentage" in descending order
sorted_df = annual_activity_df.sort_values("Target_Attainment_Percentage", ascending=False)

# Create a Plotly bar chart
fig = px.bar(
    sorted_df,
    x="SDR",
    y="Target_Attainment_Percentage",
    title="Sales Development Representatives Target Attainment Percentage (2024)",
    labels={"Target_Attainment_Percentage": "Percentage to Target", "SDR": "SDR Name"},
    color="SDR",
    text="Target_Attainment_Percentage",  # Add percentage as text on bars
)

# Update layout for better readability
fig.update_traces(texttemplate="%{text:.1f}%", hovertemplate="<b>SDR:</b> %{x}<br><b>Percentage to Target:</b> %{y:.2f}%", textposition="outside")
fig.update_layout(
    xaxis_title="SDR Name",
    yaxis_title="Percentage to Target",
    uniformtext_minsize=8,
    uniformtext_mode="hide",
    yaxis=dict(showgrid=True),
    showlegend=False,
    height=600,
    width=1800
)

# Display the Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)


import plotly.express as px

# Monthly Activity Visualizations
monthly_activity_df = activity_df.groupby(["SDR", "Month"]).agg(
    Total_Calls=("Number_of_Calls", "sum"),
    Total_Emails=("Number_of_Emails", "sum"),
    Total_Posts=("LinkedIn_Posts", "sum"),
    Avg_LinkedIn_Score=("LinkedIn_Score", "mean"),
    Total_Contacts_Added=("Contacts_Added_to_Salesforce", "sum"),
    Total_Talktime=("Talk_Time_Hours", "sum"),
    Total_Demos=("Demo_Bookings", "sum"),
    Total_Opps=("Opportunities_Created", "sum")
).reset_index()

# Custom sorting for SDRs
sdr_order = sorted(
    monthly_activity_df["SDR"].unique(),
    key=lambda x: (int(x.split("_")[1]) if x != "SDR_10" else 999)
)

# Update SDR column with custom order
monthly_activity_df["SDR"] = pd.Categorical(
    monthly_activity_df["SDR"],
    categories=sdr_order,
    ordered=True
)

# Sort the DataFrame by SDR and Month
monthly_activity_df = monthly_activity_df.sort_values(by=["SDR", "Month"]).reset_index(drop=True)

import plotly.graph_objects as go
import streamlit as st

# Highlighted: Mapping of internal names to user-friendly display names
metric_display_map = {
    "Total_Calls": "Total Calls",
    "Total_Emails": "Total Emails",
    "Total_Talktime": "Total Talktime",
    "Total_Opps": "Total Opportunities"
}
metric_internal_map = {v: k for k, v in metric_display_map.items()}  # Reverse mapping

# Custom sorting for SDRs
sdr_order = sorted(
    monthly_activity_df["SDR"].unique(),
    key=lambda x: (int(x.split("_")[1]) if x != "SDR_10" else 999)
)

# Update SDR column with custom order
monthly_activity_df["SDR"] = pd.Categorical(
    monthly_activity_df["SDR"],
    categories=sdr_order,
    ordered=True
)

# Sort the DataFrame by SDR and Month
monthly_activity_df = monthly_activity_df.sort_values(by=["SDR", "Month"]).reset_index(drop=True)

def plot_monthly_metric_with_dynamic_title(metric, monthly_activity_df):
    fig = go.Figure()

    # Create a trace for each SDR
    for sdr in monthly_activity_df["SDR"].unique():
        sdr_data = monthly_activity_df[monthly_activity_df["SDR"] == sdr]
        fig.add_trace(go.Scatter(
            x=sdr_data["Month"],
            y=sdr_data[metric],
            mode="lines+markers",
            name=sdr,
            visible=True if sdr == "SDR_1" else False  # Show only SDR_1 by default
        ))

    # Add dropdown for SDR selection
    buttons = []
    for sdr in monthly_activity_df["SDR"].unique():
        buttons.append(dict(
            method="update",
            label=sdr,
            args=[
                {"visible": [trace.name == sdr for trace in fig.data]},  # Toggle visibility
            ]
        ))

    # Update layout with dynamic title
    metric_titles = {
        "Total_Calls": "Total Calls per Month by SDR",
        "Total_Emails": "Total Emails per Month by SDR",
        "Total_Talktime": "Total Talktime per Month by SDR",
        "Total_Opps": "Total Opportunities per Month by SDR"
    }
    fig.update_layout(
        title=metric_titles.get(metric, "Monthly Metrics by SDR"),  # Dynamic title
        xaxis=dict(
            tickformat="%b %Y",  # Show abbreviated month and year
            showgrid=True,
            dtick="M1"  # Tick for every month
        ),
        yaxis=dict(showgrid=True),
        hovermode="x unified",
        updatemenus=[{
            "buttons": buttons,
            "direction": "down",
            "showactive": True,
            "x": 0.1,
            "y": 1.15,
            "xanchor": "left",
            "yanchor": "top",
        }]
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Streamlit Title
st.title("Monthly Metrics Dashboard")

# Highlighted: Use friendly names in dropdown and map back to internal names
metric_display = st.selectbox("Select Metric", options=list(metric_display_map.values()))
metric = metric_internal_map[metric_display]

# Call the plotting function with the selected metric
plot_monthly_metric_with_dynamic_title(metric, monthly_activity_df)

stage_overview = SDR_df.groupby("Deal_Stage").agg(
    Total_Leads=("Lead_ID", "count"),
    Total_Potential_MRR=("MRR_Potential", "sum")
)
stage_overview = stage_overview.reset_index()  # Ensure 'Deal_Stage' is a column

# Create the pie chart
fig = px.pie(
    stage_overview,  # DataFrame with the required columns
    values="Total_Leads",  # Proportional metric
    names="Deal_Stage",  # Labels for each section
    title="Pipeline Distribution by Deal Stage",
)

# Add customdata and hover template
fig.update_traces(
    customdata=stage_overview["Total_Potential_MRR"],  # Pass MRR as custom data
    hovertemplate="Stage: %{label}<br>Total Leads: %{value}<br>Potential MRR: $%{customdata:.2f}",
    pull=[0.09 if stage == "Closed Won" else 0 for stage in stage_overview["Deal_Stage"]]
)

# Update layout for aesthetics
fig.update_layout(
    height=500,
    width=700
)

# Streamlit-friendly display
st.plotly_chart(fig, use_container_width=True)

lead_source_df = SDR_df.groupby("Lead_Source").agg(
    Total_Leads=("Lead_ID", "count"),
    Total_MRR_Potential=("MRR_Potential", "sum")
)
import plotly.express as px

# Ensure index is reset properly
if "level_0" in lead_source_df.columns:
    lead_source_df = lead_source_df.reset_index(drop=True)
else:
    lead_source_df = lead_source_df.reset_index()

# Create a Plotly bar chart
fig = px.bar(
    lead_source_df.sort_values("Total_MRR_Potential", ascending=False),
    x="Lead_Source",
    y="Total_MRR_Potential",
    text="Total_MRR_Potential",
    title="MRR Potential by Lead Source",
    color="Lead_Source",
    labels={"Total_MRR_Potential": "MRR Potential ($)", "Lead_Source": "Lead Source"},
    custom_data=["Total_Leads"]  # Pass Total Leads for hover
)

# Customize the hover template
fig.update_traces(
    hovertemplate="<b>%{x}</b><br>MRR Potential: $%{y:.2f}<br>Total Leads: %{customdata[0]}"
)

# Update layout for better readability
fig.update_layout(
    title={
        "text":"MRR Potential by Lead Source",
    },
    xaxis_title="Lead Source",
    yaxis_title="MRR Potential ($)",
    hovermode="x unified",
    showlegend=False,
    height=600
)
st.plotly_chart(fig, use_container_width=True)
