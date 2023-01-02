#!/usr/bin/env python
# coding: utf-8

import plotly.express as px
from dash import Dash, dcc, html
import pandas as pd
import sys


def road_type_severity(df_accidents):
    # grouped_df = df_accidents.groupby(by=['speed_limit','road_type'], as_index=False).count()#.agg( {"CategorySize": "sum"} )
    grouped_df = (
        df_accidents.groupby(by=["road_type", "accident_severity"], as_index=False)
        .size()
        .reset_index()
    )
    grouped_df.road_type = grouped_df.road_type.map(
        {
            0: "Dual carriageway",
            1: "One way street",
            2: "Roundabout",
            3: "Single carriageway",
            4: "Slip road",
        }
    )
    grouped_df.accident_severity = grouped_df.accident_severity.map(
        {0: "Fatal", 1: "Serious", 2: "Slight"}
    )

    fig = px.bar(
        data_frame=grouped_df,
        x="road_type",
        y="size",
        color="accident_severity",
        barmode="stack",
    )
    return fig


def road_type_speed(df_accidents):
    grouped_df = (
        df_accidents.groupby(by=["speed_limit", "road_type"], as_index=False)
        .size()
        .reset_index()
    )
    grouped_df.road_type = grouped_df.road_type.map(
        {
            0: "Dual carriageway",
            1: "One way street",
            2: "Roundabout",
            3: "Single carriageway",
            4: "Slip road",
        }
    )
    grouped_df

    fig = px.bar(
        data_frame=grouped_df,
        x="speed_limit",
        y="size",
        color="road_type",
        barmode="stack",
    )
    return fig


def carriage_junction(df_accidents):
    # Dual carriage way encoding = 0
    df_carriage = df_accidents[df_accidents["road_type"] == 0]
    grouped_df_carr = df_accidents.groupby(
        by=["junction_detail"], as_index=False
    ).size()
    grouped_df_carr.junction_detail = grouped_df_carr.junction_detail.map(
        {
            0: "Crossroads",
            1: "Mini-roundabout",
            2: "More than 4 arms (not roundabout)",
            3: "Not at junction or within 20 metres",
            4: "Other junction",
            5: "Private drive or entrance",
            6: "Roundabout",
            7: "Slip road",
            8: "T or staggered junction",
        }
    )

    fig = px.bar(
        data_frame=grouped_df_carr,
        x="junction_detail",
        y="size",
    )
    return fig


def light_conditions(df_accidents):
    df_light = df_accidents[df_accidents["light_conditions"] == 0]
    grouped_df = df_accidents.groupby(by=["light_conditions"], as_index=False).size()
    grouped_df.light_conditions = grouped_df.light_conditions.map(
        {
            0: "Darkness (unknown)",
            1: "Darkness (lit)",
            2: "Darkness (unlit)",
            3: "Darkness (no lighting)",
            4: "Daylight",
        }
    )

    fig = px.bar(
        data_frame=grouped_df,
        x="light_conditions",
        y="size",
    )
    return fig


def hours_fig(df_accidents):
    timef = df_accidents.copy(deep=True)
    timef["time"] = pd.to_datetime(timef["time"], format="%H:%M", exact=False)
    timef["hour"] = timef["time"].dt.hour
    grouped_df = timef.groupby(by=["hour"], as_index=False).size()

    fig = px.bar(
        data_frame=grouped_df,
        x="hour",
        y="size",
    )
    return fig


def start_visualize_server(
    path="/opt/airflow/data/", filename="accidents_cleaned_milestone2.csv", port=8050
):
    df_accidents = pd.read_csv(f"{path}/{filename}")
    app = Dash()
    app.layout = html.Div(
        [
            html.H1(
                "Web Application Dashboards with Dash", style={"text-align": "center"}
            ),
            html.Br(),
            html.H1("UK accidents 2011", style={"text-align": "center"}),
            html.Br(),
            html.Div(),
            html.H1(
                "Relationship between road type and accident severity",
                style={"text-align": "center"},
            ),
            dcc.Graph(figure=road_type_severity(df_accidents)),
            html.Br(),
            html.Div(),
            html.H1(
                "Relationship between road type and speed",
                style={"text-align": "center"},
            ),
            dcc.Graph(figure=road_type_speed(df_accidents)),
            html.Br(),
            html.Div(),
            html.H1(
                'Relationship between "carriage way" road type and junction detail',
                style={"text-align": "center"},
            ),
            dcc.Graph(figure=carriage_junction(df_accidents)),
            html.Br(),
            html.Div(),
            html.H1("Light conditions bar plot", style={"text-align": "center"}),
            dcc.Graph(figure=light_conditions(df_accidents)),
            html.Br(),
            html.Div(),
            html.H1("Accident hours bar plot", style={"text-align": "center"}),
            dcc.Graph(figure=hours_fig(df_accidents)),
        ]
    )

    if len(sys.argv) > 1:
        port = sys.argv[1]
    app.run_server(debug=False, port=port)


def main():
    start_visualize_server()


if __name__ == "__main__":
    main()
