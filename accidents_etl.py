from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

from task_1 import ms_1
from task_2 import ms_2
from task_visualization import start_visualize_server

import pandas as pd
from sqlalchemy import create_engine

import numpy as np
from scipy import stats
from sklearn.preprocessing import LabelEncoder


def ms_1(path="/opt/airflow/data/", filename="2011_Accidents_UK.csv"):
    # path = "/opt/airflow/data/"
    # Reading the data
    df = pd.read_csv(f"{path}/{filename}", encoding="latin-1", low_memory=False)

    # Helper functions

    # Handling missing values
    df = df.dropna(axis="index", subset=["road_type"], inplace=False)
    df["weather_conditions"].fillna(df["weather_conditions"].mode()[0], inplace=True)
    df = df.replace({"Data missing or out of range": np.nan}, inplace=False)
    df.dropna(axis="index", subset=["road_surface_conditions"], inplace=True)
    df["trunk_road_flag"].fillna(df["trunk_road_flag"].mode()[0], inplace=True)
    df["junction_control"].fillna(df["junction_control"].mode()[0], inplace=True)
    df["second_road_number"].fillna(-1, inplace=True)
    value = "first_road_class is C or Unclassified. These roads do not have official numbers so recorded as zero "
    df.replace({value: 0}, inplace=True)
    df = df.replace(
        {
            "first_road_class is C or Unclassified. These roads do not have official numbers so recorded as zero": 0
        },
        inplace=False,
    )
    df["first_road_number"] = df["first_road_number"].astype(float)
    df["second_road_number"] = df["second_road_number"].astype(float)

    # Handling outliers
    z = np.abs(stats.zscore(df["number_of_vehicles"]))
    filtered_entries = z < 3
    # REVISE THIS PART
    df = df[filtered_entries]
    floor = df["number_of_casualties"].quantile(0.10)
    cap = df["number_of_casualties"].quantile(0.90)
    df["number_of_casualties"] = np.where(
        df["number_of_casualties"] < floor, floor, df["number_of_casualties"]
    )
    df["number_of_casualties"] = np.where(
        df["number_of_casualties"] > cap, cap, df["number_of_casualties"]
    )

    # Discretization
    formatted_date = pd.to_datetime(df["date"])
    df["week_number"] = formatted_date.apply(lambda x: x.weekofyear)
    df["week_number"] = pd.cut(
        df["week_number"],
        bins=[0, 13, 26, 39, 52],
        labels=["weekGroup1", "weekGroup2", "weekGroup3", "weekGroup4"],
    )

    # Encoding
    is_trunk = lambda x: 0 if x == "Non-trunk" else 1
    df["trunk_road_flag"] = df["trunk_road_flag"].apply(is_trunk)

    df["first_road_A"] = df["first_road_class"].apply(lambda x: 1 if x == "A" else 0)
    df["first_road_B"] = df["first_road_class"].apply(lambda x: 1 if x == "B" else 0)
    df["first_road_C"] = df["first_road_class"].apply(lambda x: 1 if x == "C" else 0)
    df["second_road_A"] = df["second_road_class"].apply(lambda x: 1 if x == "A" else 0)
    df["second_road_B"] = df["second_road_class"].apply(lambda x: 1 if x == "B" else 0)
    df["second_road_C"] = df["second_road_class"].apply(lambda x: 1 if x == "C" else 0)

    is_urban = lambda x: 1 if x == "Urban" else 0
    df["urban_or_rural_area"] = df["urban_or_rural_area"].apply(is_urban)

    police_attended = lambda x: 1 if x == "Yes" else 0
    df["did_police_officer_attend_scene_of_accident"] = df[
        "did_police_officer_attend_scene_of_accident"
    ].apply(police_attended)

    lab = LabelEncoder()
    cols = [
        "accident_severity",
        "carriageway_hazards",
        "light_conditions",
        "pedestrian_crossing_human_control",
        "pedestrian_crossing_physical_facilities",
        "road_surface_conditions",
        "road_type",
        "police_force",
        "local_authority_district",
        "local_authority_ons_district",
        "local_authority_highway",
        "junction_detail",
        "junction_control",
        "special_conditions_at_site",
        "weather_conditions",
    ]
    encodings = pd.DataFrame([], columns=["column_name", "original_value", "encoding"])

    for col in cols:
        df[col] = lab.fit_transform(df[col])
        mappings = dict(zip(lab.classes_, lab.transform(lab.classes_)))
        for original, encoding in mappings.items():
            encodings = encodings.append(
                pd.Series(
                    [col, original, encoding],
                    index=["column_name", "original_value", "encoding"],
                ),
                ignore_index=True,
            )

    # lab = LabelEncoder()

    # df["accident_severity"] = lab.fit_transform(df["accident_severity"])
    # df["carriageway_hazards"] = lab.fit_transform(df["carriageway_hazards"])
    # df["light_conditions"] = lab.fit_transform(df["light_conditions"])
    # df["pedestrian_crossing_human_control"] = lab.fit_transform(
    #     df["pedestrian_crossing_human_control"]
    # )
    # df["pedestrian_crossing_physical_facilities"] = lab.fit_transform(
    #     df["pedestrian_crossing_physical_facilities"]
    # )
    # df["road_surface_conditions"] = lab.fit_transform(df["road_surface_conditions"])
    # df["road_type"] = lab.fit_transform(df["road_type"])
    # df["police_force"] = lab.fit_transform(df["police_force"])
    # df["local_authority_district"] = lab.fit_transform(df["local_authority_district"])
    # df["local_authority_ons_district"] = lab.fit_transform(
    #     df["local_authority_ons_district"]
    # )
    # df["local_authority_highway"] = lab.fit_transform(df["local_authority_highway"])
    # df["junction_detail"] = lab.fit_transform(df["junction_detail"])
    # df["junction_control"] = lab.fit_transform(df["junction_control"])
    # df["special_conditions_at_site"] = lab.fit_transform(
    #     df["special_conditions_at_site"]
    # )
    # df["weather_conditions"] = lab.fit_transform(df["weather_conditions"])

    # Normalization
    index_of_pos_number_of_vehicals = df.number_of_vehicles > 0
    pos_number_of_vehicals = df.number_of_vehicles.loc[index_of_pos_number_of_vehicals]
    # REVISE THIS PART
    df["number_of_vehicles"] = pos_number_of_vehicals

    # Adding more features
    is_weekend = lambda x: 1 if x == "Saturday" or x == "Sunday" else 0
    df["is_weekend"] = df["day_of_week"].apply(is_weekend)

    df["time"] = pd.to_datetime(df["time"], format="%H:%M")
    df["hour"] = df["time"].dt.hour

    # Exporting to csv file
    # df.to_csv("accidents_cleaned.csv", index=False)
    # encodings.to_csv("encodings.csv", index=False)
    # # Exporting to parquet file

    # df.to_parquet("accidents_cleaned.parquet", index=False)
    export_csv(df, path, "accidents_cleaned.csv")
    export_csv(df, path, "encodings.csv")
    export_parquet(df, path, "accidents_cleaned.parquet")


def export_csv(df, path, filename):
    filename = f"{path}/{filename}"
    df.to_csv(filename, index=False)


def export_parquet(df, path, filename):
    filename = f"{path}/{filename}"
    df.to_parquet(filename, index=False)


def load_to_postgres(
    path="/opt/airflow/data/",
    filename="accidents_cleaned_milestone2.csv",
    lookup_table="encodings.csv",
    port=5432,
):

    engine = create_engine(f"postgresql://root:root@pgdatabase5:{port}/accidents_etl")
    if engine.connect():
        print("connected succesfully")
    else:
        print("failed to connect")
    # "accidents_cleaned_milestone2.csv"
    df = pd.read_csv(f"{path}/{filename}")
    df.to_sql(name="UK_Accidents_2011", con=engine, if_exists="replace")

    # "encodings.csv"
    df = pd.read_csv(f"{path}/{lookup_table}")
    df.to_sql(name="lookup_table", con=engine, if_exists="replace")
    df.to_sql(name="titanic_passengers", con=engine, if_exists="replace")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(2),
    "retries": 1,
}

dag = DAG(
    "accidents_etl_pipeline",
    default_args=default_args,
    description="accidents etl pipeline",
)
with DAG(
    dag_id="accidents_etl_pipeline",
    schedule_interval="@once",
    default_args=default_args,
    tags=["accidents-pipeline"],
) as dag:
    extract_clean_task = PythonOperator(
        task_id="extract_dataset",
        python_callable=ms_1,
        op_kwargs={
            "path": "/opt/airflow/data/",
            "filename": "2011_Accidents_UK.csv",
        },
    )
    encoding_load_task = PythonOperator(
        task_id="add_feature",
        python_callable=ms_2,
        op_kwargs={
            "path": "/opt/airflow/data/",
            "cleaned_file": "accidents_cleaned.csv",
            "new_dataset": "2018_Accidents_UK.csv",
        },
    )
    load_to_postgres_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres,
        op_kwargs={
            "path": "/opt/airflow/data/",
            "filename": "accidents_cleaned_milestone2.csv",
            "lookup_table": "encodings.csv",
            "port": 5432,
        },
    )
    create_dashboard_task = PythonOperator(
        task_id="visualize_accidents",
        python_callable=start_visualize_server,
        op_kwargs={
            "path": "/opt/airflow/data/",
            "filename": "accidents_cleaned_milestone2.csv",
            "port": 8050,
        },
    )

    (
        extract_clean_task
        >> encoding_load_task
        >> load_to_postgres_task
        >> create_dashboard_task
    )
