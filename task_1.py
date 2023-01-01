#Milestone 1

#Importing required files
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import datetime
from sklearn.preprocessing import LabelEncoder
from pandas.io.parquet import to_parquet

#Creating the function ms_1 for doing milestone 1 tasks
def ms_1():
    #Reading the data
    df = pd.read_csv('2011_Accidents_UK.csv', encoding='latin-1', low_memory=False)
    
    #Helper functions
    
    #Handling missing values
    df = df.dropna(axis='index', subset=['road_type'], inplace=False)
    df['weather_conditions'].fillna(df['weather_conditions'].mode()[0], inplace=True)
    df = df.replace({"Data missing or out of range": np.nan}, inplace=False)
    df.dropna(axis='index', subset=['road_surface_conditions'], inplace=True)
    df['trunk_road_flag'].fillna(df['trunk_road_flag'].mode()[0], inplace=True)
    df['junction_control'].fillna(df['junction_control'].mode()[0], inplace=True)
    df['second_road_number'].fillna(-1, inplace=True)
    value = "first_road_class is C or Unclassified. These roads do not have official numbers so recorded as zero "
    df.replace({value: 0}, inplace=True)
    df = df.replace({"first_road_class is C or Unclassified. These roads do not have official numbers so recorded as zero": 0}, inplace=False)
    df['first_road_number'] = df['first_road_number'].astype(float)
    df['second_road_number'] = df['second_road_number'].astype(float)
    
    #Handling outliers
    z = np.abs(stats.zscore(df['number_of_vehicles']))
    filtered_entries = z < 3
    #REVISE THIS PART
    df = df[filtered_entries]
    floor = df['number_of_casualties'].quantile(0.10)
    cap = df['number_of_casualties'].quantile(0.90)
    df["number_of_casualties"] = np.where(df["number_of_casualties"] <floor, floor,df['number_of_casualties'])
    df["number_of_casualties"] = np.where(df["number_of_casualties"] >cap,cap,df['number_of_casualties'])
    
    #Discretization
    formatted_date = pd.to_datetime(df['date'])
    df['week_number'] = formatted_date.apply(lambda x: x.weekofyear)
    df['week_number'] = pd.cut(df['week_number'], bins=[0, 13, 26, 39, 52], labels=['weekGroup1', 'weekGroup2', 'weekGroup3', 'weekGroup4'])
    
    #Encoding
    is_trunk = lambda x: 0 if x =="Non-trunk" else 1
    df['trunk_road_flag']=df['trunk_road_flag']. apply(is_trunk)
    
    df['first_road_A']= df['first_road_class'].apply(lambda x: 1 if x == 'A' else 0)
    df['first_road_B']= df['first_road_class'].apply(lambda x: 1 if x == 'B' else 0)
    df['first_road_C']= df['first_road_class'].apply(lambda x: 1 if x == 'C' else 0)
    df['second_road_A']= df['second_road_class'].apply(lambda x: 1 if x == 'A' else 0)
    df['second_road_B']= df['second_road_class'].apply(lambda x: 1 if x == 'B' else 0)
    df['second_road_C']= df['second_road_class'].apply(lambda x: 1 if x == 'C' else 0)
    
    is_urban = lambda x: 1 if x =="Urban" else 0
    df['urban_or_rural_area']=df['urban_or_rural_area']. apply(is_urban)
    
    police_attended = lambda x: 1 if x =="Yes" else 0
    df['did_police_officer_attend_scene_of_accident']=df['did_police_officer_attend_scene_of_accident']. apply(police_attended)
    
    lab = LabelEncoder()
    
    df['accident_severity'] = lab.fit_transform(df['accident_severity'])
    df['carriageway_hazards'] = lab.fit_transform(df['carriageway_hazards'])
    df['light_conditions'] = lab.fit_transform(df['light_conditions'])
    df['pedestrian_crossing_human_control'] = lab.fit_transform(df['pedestrian_crossing_human_control'])
    df['pedestrian_crossing_physical_facilities'] = lab.fit_transform(df['pedestrian_crossing_physical_facilities'])
    df['road_surface_conditions'] = lab.fit_transform(df['road_surface_conditions'])
    df['road_type'] = lab.fit_transform(df['road_type'])
    df['police_force'] = lab.fit_transform(df['police_force'])
    df['local_authority_district'] = lab.fit_transform(df['local_authority_district'])
    df['local_authority_ons_district'] = lab.fit_transform(df['local_authority_ons_district'])
    df['local_authority_highway'] = lab.fit_transform(df['local_authority_highway'])
    df['junction_detail'] = lab.fit_transform(df['junction_detail'])
    df['junction_control'] = lab.fit_transform(df['junction_control'])
    df['special_conditions_at_site'] = lab.fit_transform(df['special_conditions_at_site'])
    df['weather_conditions'] = lab.fit_transform(df['weather_conditions'])
    
    #Normalization
    index_of_pos_number_of_vehicals = df.number_of_vehicles > 0
    pos_number_of_vehicals = df.number_of_vehicles.loc[index_of_pos_number_of_vehicals]
    #REVISE THIS PART
    df['number_of_vehicles'] = pos_number_of_vehicals
    
    #Adding more features
    is_weekend = lambda x: 1 if x =="Saturday" or x == "Sunday" else 0
    df['is_weekend']=df['day_of_week']. apply(is_weekend)
    
    df['time'] = pd.to_datetime(df['time'], format='%H:%M')
    df['hour'] = df['time'].dt.hour
    
    #Exporting to csv file
    df.to_csv('accidents_cleaned.csv', index=False)
    
    #Exporting to parquet file 
    df.to_parquet('accidents_cleaned.parquet', index=False)

#Calls the above script
ms_1()
