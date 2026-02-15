# ==================================================
# Imports
# ==================================================
import os
import pandas as pd
import plotly.express as px

from dash import Dash, html, dcc


# ==================================================
# External CSS (Bootstrap)
# ==================================================
external_stylesheets = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
]


# ==================================================
# Create Dash App
# ==================================================
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server   # REQUIRED FOR RENDER


# ==================================================
# Load Data
# ==================================================
patients = pd.read_csv("content/IndividualDetails.csv")
confirmed = pd.read_csv("content/time_series_covid_19_confirmed.csv")


# ==================================================
# KPI METRICS
# ==================================================
total_patients = patients.shape[0]

active_patients = patients[
    patients["current_status"] == "Hospitalized"
].shape[0]

recovered_patients = patients[
    patients["current_status"] == "Recovered"
].shape[0]

deaths = patients[
    patients["current_status"] == "Deceased"
].shape[0]


# ==================================================
# DAY-BY-DAY CASES
# ==================================================
date_columns = confirmed.columns[4:]
daily_cases = confirmed[date_columns].sum()

df_daily = pd.DataFrame({
    "Date": date_columns,
    "Cases": daily_cases.values
})

df_daily["Date"] = pd.to_datetime(df_daily["Date"], format="%m/%d/%y")

line_fig = px.line(
    df_daily,
    x="Date",
    y="Cases",
    title="Day by Day Analysis"
)


# ==================================================
# AGE DISTRIBUTION
# ==================================================
patients["age"] = pd.to_numeric(patients["age"], errors="coerce")

patients["age_bracket"] = pd.cut(
    patients["age"],
    bins=[0, 20, 30, 40, 50, 60, 70, 120],
    labels=["0-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"],
    right=False
)

age_fig = px.pie(
    patients,
    names="age_bracket",
    title="Age Distribution"
)


# ==================================================
# STATE-WISE HOSPITALIZED
# ==================================================
state_hospitalized = (
    patients[patients["current_status"] == "Hospitalized"]
    .groupby("detected_state")
    .size()
    .reset_index(name="Count")
)

bar_fig = px.bar(
    state_hospitalized,
    x="detected_state",
    y="Count",
    title="Hospitalized Patients by State"
)


# ==================================================
# LAYOUT
# ==================================================
app.layout = html.Div(
    [
        html.H1(
            "COVID-19 Dashboard",
            className="text-center text-light mb-4"
        ),

        html.Div(
            [
                html.Div(
                    html.Div(
                        [html.H4("Total Cases"), html.H2(total_patients)],
                        className="card-body text-light text-center"
                    ),
                    className="card bg-danger col-md-3"
                ),

                html.Div(
                    html.Div(
                        [html.H4("Active"), html.H2(active_patients)],
                        className="card-body text-light text-center"
                    ),
                    className="card bg-primary col-md-3"
                ),

                html.Div(
                    html.Div(
                        [html.H4("Recovered"), html.H2(recovered_patients)],
                        className="card-body text-light text-center"
                    ),
                    className="card bg-warning col-md-3"
                ),

                html.Div(
                    html.Div(
                        [html.H4("Deaths"), html.H2(deaths)],
                        className="card-body text-light text-center"
                    ),
                    className="card bg-success col-md-3"
                ),
            ],
            className="row justify-content-around mb-4"
        ),

        html.Div(
            [
                html.Div(dcc.Graph(figure=line_fig), className="col-md-8"),
                html.Div(dcc.Graph(figure=age_fig), className="col-md-4"),
            ],
            className="row"
        ),

        html.Div(
            [html.Div(dcc.Graph(figure=bar_fig), className="col-md-12")],
            className="row mt-4"
        ),
    ],
    className="container-fluid",
    style={"backgroundColor": "#1f2c38", "minHeight": "100vh"}
)


# ==================================================
# RUN SERVER (RENDER SAFE)
# ==================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
