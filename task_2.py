import pandas as pd
from sklearn.preprocessing import LabelEncoder


def ms_2(
    path="/opt/airflow/data/",
    cleaned_file="accidents_cleaned.csv",
    new_dataset="2018_Accidents_UK",
):
    accidents_cleaned = pd.read_csv(
        f"{path}/{cleaned_file}", encoding="latin-1", low_memory=False
    )
    df_ms2 = pd.read_csv(f"{path}/{new_dataset}", encoding="latin-1", low_memory=False)

    df_ms2.dropna(inplace=True)

    # week number into bins
    formatted_date_ms2 = pd.to_datetime(df_ms2["date"])
    df_ms2["week_number"] = formatted_date_ms2.apply(lambda x: x.weekofyear)
    df_ms2["week_number"] = pd.cut(
        df_ms2["week_number"],
        bins=[0, 13, 26, 39, 52],
        labels=["weekGroup1", "weekGroup2", "weekGroup3", "weekGroup4"],
    )
    df_ms2[["date", "week_number"]].head()

    is_trunk = lambda x: 0 if x == "Non-trunk" else 1
    df_ms2["trunk_road_flag"] = df_ms2["trunk_road_flag"].apply(is_trunk)
    df_ms2["trunk_road_flag"].head()

    # one-hot encoding
    df_ms2["first_road_A"] = df_ms2["first_road_class"].apply(
        lambda x: 1 if x == "A" else 0
    )
    df_ms2["first_road_B"] = df_ms2["first_road_class"].apply(
        lambda x: 1 if x == "B" else 0
    )
    df_ms2["first_road_C"] = df_ms2["first_road_class"].apply(
        lambda x: 1 if x == "C" else 0
    )

    df_ms2["second_road_A"] = df_ms2["second_road_class"].apply(
        lambda x: 1 if x == "A" else 0
    )
    df_ms2["second_road_B"] = df_ms2["second_road_class"].apply(
        lambda x: 1 if x == "B" else 0
    )
    df_ms2["second_road_C"] = df_ms2["second_road_class"].apply(
        lambda x: 1 if x == "C" else 0
    )
    df_ms2[
        [
            "first_road_A",
            "first_road_B",
            "first_road_C",
            "second_road_A",
            "second_road_B",
            "second_road_C",
        ]
    ].head()

    """
    one hot encoding for 'urban_or_rural_area' because it is binary
    1 is urban, 0 is rural.
    """
    is_urban = lambda x: 1 if x == "Urban" else 0
    df_ms2["urban_or_rural_area"] = df_ms2["urban_or_rural_area"].apply(is_urban)

    """
    one hot encoding for 'did_police_officer_attend_scene_of_accident' because it is binary
    """
    police_attended = lambda x: 1 if x == "Yes" else 0
    df_ms2["did_police_officer_attend_scene_of_accident"] = df_ms2[
        "did_police_officer_attend_scene_of_accident"
    ].apply(police_attended)
    df_ms2["did_police_officer_attend_scene_of_accident"].head()

    is_weekend = lambda x: 1 if x == "Saturday" or x == "Sunday" else 0
    df_ms2["is_weekend"] = df_ms2["day_of_week"].apply(is_weekend)

    df_ms2["time"] = pd.to_datetime(df_ms2["time"], format="%H:%M")
    df_ms2["hour"] = df_ms2["time"].dt.hour

    lab = LabelEncoder()

    df_ms2["accident_severity"] = lab.fit_transform(df_ms2["accident_severity"])
    df_ms2["carriageway_hazards"] = lab.fit_transform(df_ms2["carriageway_hazards"])
    df_ms2["light_conditions"] = lab.fit_transform(df_ms2["light_conditions"])
    df_ms2["pedestrian_crossing_human_control"] = lab.fit_transform(
        df_ms2["pedestrian_crossing_human_control"]
    )
    df_ms2["pedestrian_crossing_physical_facilities"] = lab.fit_transform(
        df_ms2["pedestrian_crossing_physical_facilities"]
    )
    df_ms2["road_surface_conditions"] = lab.fit_transform(
        df_ms2["road_surface_conditions"]
    )
    df_ms2["road_type"] = lab.fit_transform(df_ms2["road_type"])
    df_ms2["police_force"] = lab.fit_transform(df_ms2["police_force"])
    df_ms2["local_authority_district"] = lab.fit_transform(
        df_ms2["local_authority_district"]
    )
    df_ms2["local_authority_ons_district"] = lab.fit_transform(
        df_ms2["local_authority_ons_district"]
    )
    df_ms2["local_authority_highway"] = lab.fit_transform(
        df_ms2["local_authority_highway"]
    )
    df_ms2["junction_detail"] = lab.fit_transform(df_ms2["junction_detail"])
    df_ms2["junction_control"] = lab.fit_transform(df_ms2["junction_control"])
    df_ms2["special_conditions_at_site"] = lab.fit_transform(
        df_ms2["special_conditions_at_site"]
    )
    df_ms2["weather_conditions"] = lab.fit_transform(df_ms2["weather_conditions"])

    df_combined = accidents_cleaned.append(df_ms2, ignore_index=True)

    df_combined["spotlight"] = df_combined["road_type"].apply(
        lambda x: 1 if x == 2 or x == 6 else 0
    )
    # df_combined.to_csv("accidents_cleaned_milestone2.csv", index=False)
    export_csv(df_combined, path, "accidents_cleaned_milestone2.csv")


def export_csv(df, path, filename):
    filename = f"{path}/{filename}"
    df.to_csv(filename, index=False)


def main():
    ms_2()


if __name__ == "__main__":
    main()
