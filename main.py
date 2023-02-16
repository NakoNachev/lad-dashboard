import pandas as pd
import numpy as np
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_timeline import timeline
import matplotlib.pyplot as plt
import random
import matplotlib.colors as mcolors
import streamlit_nested_layout 

# set up main layout to use whole width of screen
st.set_page_config(layout="wide")

# markdown/styles 
span_alignment="""
<style>
span {
  text-align: center
}
</style>
"""
st.markdown(span_alignment, unsafe_allow_html=True)

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

def pack_data_for_timeline(upper_range: int) -> dict:
    timearr = []
    for i in json_data[0:upper_range]:
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
        timearr.append(extra)
    return {"events":timearr}

def get_city_and_their_courses_total() -> dict:
    """ returns each city with its total courses"""
    cities_and_corses = {}
    for item in json_data:
        if item['Anbieterstadt'] in cities_and_corses.keys():
            cities_and_corses[item['Anbieterstadt']] += 1
        else:
            cities_and_corses[item['Anbieterstadt']] = 1

    return cities_and_corses

def get_top_n_cities_data_for_pie_chart(first_top_cities: int) -> dict:
    """ packs the data for the pie chart. Takes the first n cities, packs the rest into 'other' category """
    cities_and_corses = dict(sorted(get_city_and_their_courses_total().items(), key=lambda x: x[1], reverse=True))
    filtered_data = {}
    filtered_data['Andere'] = 0
    counter = 0
    for key, value in cities_and_corses.items():
        if counter < first_top_cities:
            filtered_data[key]=value
        else:
            filtered_data['Andere'] = filtered_data['Andere'] + value
        counter = counter+1
    return filtered_data

def prep_plot_data():
    """ creates the figure for the pie chart """
    city_data = get_top_n_cities_data_for_pie_chart(10)
    colors = random.choices(list(mcolors.CSS4_COLORS.values()),k = len(city_data.keys()))
    fig1, ax1 = plt.subplots() # https://discuss.streamlit.io/t/how-to-draw-pie-chart-with-matplotlib-pyplot/13967/2   https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html
    ax1.pie(list(city_data.values()), colors=colors, labels=list(city_data.keys()), autopct='%1.1f%%',
        shadow=False, startangle=90)
    ax1.axis('equal')
    return fig1



    
def prep_plot_data_2():
    """ creates the figure for the pie chart 
        source can be found: https://medium.com/@kvnamipara/a-better-visualisation-of-pie-charts-by-matplotlib-935b7667d77f """
    city_data = get_top_n_cities_data_for_pie_chart(10)
    colors = random.choices(list(mcolors.CSS4_COLORS.values()),k = len(city_data.keys()))
    fig1, ax1 = plt.subplots()
    ax1.pie(list(city_data.values()), colors=colors, labels=list(city_data.keys()), autopct='%1.1f%%',
        shadow=False, startangle=90, pctdistance=0.85)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    ax1.axis('equal')
    return fig1

def plotly_pie():
    df = pd.DataFrame.from_dict(get_top_n_cities_data_for_pie_chart(10), orient='index', columns=['Werte']).reset_index()
    df.rename(columns={'index':'Schlüssel'},inplace=True)
    print(df)
    fig = px.pie(df, values='Werte', names='Schlüssel', color_discrete_sequence=px.colors.sequential.RdBu)
    return fig

def prep_organizers_chart():
    y_values,x_values = get_organizer_and_their_courses_total_bar_values(20,True)
    fig = go.Figure(go.Bar(
            x=x_values,
            y=y_values,
            orientation='h'))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig

def get_average_courses_total_per_city():
    city_and_courses_total = get_city_and_their_courses_total()
    values = list(city_and_courses_total.values())
    total = np.sum(values)
    return total / len(values)

# initiate columns
col1, col2 = st.columns([4,4])

# set up col2
table_unique_df = pd.DataFrame.from_dict(get_keys_and_their_values_that_are_unique(), orient='index', columns=['Werte']).reset_index()
table_unique_df.rename(columns={'index':'Schlüssel'},inplace=True)
table_top_organizers_df = pd.DataFrame.from_dict(get_top_or_bottom_n_organizers(3, True), orient='index', columns=['Werte']).reset_index()
table_top_organizers_df.rename(columns={'index':'Schlüssel'},inplace=True)
col2.subheader('Top 3 Veranstalter')
col2.table(table_top_organizers_df)
col2.subheader('Top 20 Veranstalter visualisiert')
col2.plotly_chart(prep_organizers_chart(), use_container_width=True)
col2.subheader('Kurse gruppiert nach Städte')

with col2:
    inner_columns = st.columns([0.5,2.5,0.5])
    inner_columns[1].plotly_chart(plotly_pie())

# set up col 1
col1.subheader('Kurse Standorte (lat,lon)')
col1.map(df)
col1.subheader('Dataset eindeutige Schlüssel')
col1.table(table_unique_df)

# timeline(pack_data_for_timeline(100), height=800)

with st.sidebar:
    st.subheader('Metriken')
    st.metric('Datensätze', '20k')
    st.metric('Anzahl Veranstalter',len(get_organizer_and_their_courses_total().keys()))
    st.metric('Anzahl Städte', len(get_city_and_their_courses_total().keys()))
    st.metric('Durchschnittliche Anzahl Kurse pro Stadt', np.round(get_average_courses_total_per_city(),2))
