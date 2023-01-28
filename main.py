import pandas as pd
import numpy as np
import json
import streamlit as st

# load json file
f = open('Top20k.json')
json_data = json.load(f)


def load_coordinates_for_map():
    """ fetch longitude and lattitde coordinates from file"""
    latitude = []
    longitude = []
    for object in json_data:
        latitude.append(float(object['Latitude']))
        longitude.append(float(object['Longitude']))
    return {'lat': latitude, 'lon': longitude}
df = pd.DataFrame(data=load_coordinates_for_map())

def remove_duplicates(l: list):
    return list(set(l))

def extract_value_for_key(object, key):
    return object[key]

def get_unique_values_for_key_in_json(key):
    """ loop through the json and return a unique list of values for a given key"""
    values = []
    for item in json_data:
        values.append(extract_value_for_key(item, key))
    return remove_duplicates(values)

def get_keys_and_their_values_that_are_unique():
    keys = json_data[0].keys()
    dict = {}
    for key in keys:
        values = get_unique_values_for_key_in_json(key)
        if len(values) == 1:
            dict[key] = values

    return dict

table_unique_df = pd.DataFrame.from_dict(get_keys_and_their_values_that_are_unique(), orient='index', columns=['Values']).reset_index()
table_unique_df.rename(columns={'index':'Key'},inplace=True)
st.table(table_unique_df)
st.map(df)


