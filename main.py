import pandas as pd
import numpy as np
import json
import streamlit as st
import plotly.graph_objects as go
from streamlit_timeline import timeline

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

def get_organizer_and_their_courses_total() -> dict:
    """ {'Veranstalter1': 50, 'Veranstalter2': 60} .. """
    dict = {}
    for item in json_data:
        if item['Veranstaltername'] in dict.keys():
            dict[item['Veranstaltername']] += 1
        else:
            dict[item['Veranstaltername']] = 1
    return dict

def get_organizer_and_their_courses_total_bar_values(n: int, is_top: bool):
    data = get_top_or_bottom_n_organizers(n, is_top)
    return list(data.keys()), list(data.values())

def get_top_or_bottom_n_organizers(n: int, is_top: bool):
    if is_top:
        return dict(sorted(get_organizer_and_their_courses_total().items(), key=lambda x: x[1], reverse=True)[0:n])
    else:
        return dict(sorted(get_organizer_and_their_courses_total().items(), key=lambda x: x[1], reverse=True)[-n-1:-1])

def organizers_and_their_courses_percentage_from_total():
    org_courses_total_dict = get_organizer_and_their_courses_total()
    total_courses = len(list(json_data))
    for key in org_courses_total_dict:
        org_courses_total_dict[key] = (org_courses_total_dict[key] / total_courses)*100
    return org_courses_total_dict


col1, col2 = st.columns([3,3])

table_unique_df = pd.DataFrame.from_dict(get_keys_and_their_values_that_are_unique(), orient='index', columns=['Values']).reset_index()
table_unique_df.rename(columns={'index':'Key'},inplace=True)
table_top_organizers_df = pd.DataFrame.from_dict(get_top_or_bottom_n_organizers(3, True), orient='index', columns=['Values']).reset_index()
table_top_organizers_df.rename(columns={'index':'Key'},inplace=True)
col1.subheader('Top 3 Veranstalter')
col1.table(table_top_organizers_df)

y_values,x_values = get_organizer_and_their_courses_total_bar_values(20,True)

fig = go.Figure(go.Bar(
            x=x_values,
            y=y_values,
            orientation='h'))
fig.update_layout(yaxis=dict(autorange="reversed"))
col1.subheader('Top 20 Veranstalter visualisiert')
col1.plotly_chart(fig, use_container_width=True)

col2.subheader('Dataset eindeutige Schlüssel')
col2.table(table_unique_df)
col2.subheader('Kurse Standorte (lat,lon)')
col2.map(df)


timearr = []
timearr2 = []
for i in json_data[0:100]:
    #st.write(i)
    #st.write(i["Kursbeginn"][0:4])
    year = i["Kursbeginn"][0:4]
    month = i["Kursbeginn"][5:7]
    day = i["Kursbeginn"][8:10]
    extra = {
        "start_date": { 
            "year":  year, 
            "month": month,
            "day": day
            },
        "text": {
            "text": i["Kurstitel"]
            } 
        }
    #rooinr = json.dumps(extra)
    timearr.append(extra)

#st.write(timearr)

fortime = {"events":timearr}
testobj = {
    "events": [
        {"start_date":{
            "year": "2020"
        }}
    ]
}
#st.write(fortime)
#makejson = json.loads(fortime)
#timlin = json.dumps(fortime)
#st.write(timlin)
timeline(fortime, height=800)

"""for j in range(0, len(timearr)-1):
    timearr2.append(timearr[j])
lasttime = timearr[len(timearr)-1]
timearr2.append(lasttime[:-1])
st.write(timearr2)"""