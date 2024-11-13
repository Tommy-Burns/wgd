import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import requests
import geopandas as gpd

st.set_page_config(layout="wide", page_title="My Geospatial Dashboard")

@st.cache_data
def get_data():
    url = f"https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world_population.csv"
    geo_url = f"https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson"
    try:
        df = pd.read_csv(url)
        gdf = gpd.read_file(geo_url)
        return df, gdf
    except Exception as e:
        st.error(f"An error occured: {e}")
        return None, None, None

data, geodata = get_data()

def get_geo_details(country):
    # Filter the GeoDataFrame for the selected country
    gh = geodata[geodata['name'] == country]
    
    if gh.empty:
        # If country is not found, return None
        return None, None, None
    return gh

st.markdown(
    """
    <style>
    .map-container {
        height: 400px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Set up the Streamlit app layout
st.title("World Population Dashboard")
st.write("Select a country to view its population data and geographical information.")


# Sidebar for country selection with no default selection
country = st.selectbox("Select a Country", options=[""] + list(data["Country/Territory"].unique()), key="selected_country")
country_boundary = get_geo_details(country)

# Only fetch data if a country is selected
if country:
    # Filter data based on selected country
    country_data = data[data["Country/Territory"] == country].iloc[0]

    # Layout with columns: map and chart details
    col1, col2 = st.columns([3, 2])

    with col1:
        # Top section in the right column: Population bar chart
        st.subheader("Population Over Selected Years")
        years = ["2022 Population", "2020 Population", "2015 Population", "2010 Population",
                 "2000 Population", "1990 Population", "1980 Population", "1970 Population"]
        selected_years = st.multiselect("Select Population Years", options=years, default=years[:3])

        # Prepare the data for the bar chart
        population_data = {
            "Year": [year.split()[0] for year in selected_years],
            "Population": [country_data[year] for year in selected_years]
        }
        population_df = pd.DataFrame(population_data)

        # Display the bar chart
        fig = px.bar(population_df, x="Year", y="Population", title=f"Population of {country} Over Selected Years")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Map
        # Display the map with the capital marked
        if country_boundary is not None:
            # Display the map only if the country boundary and coordinates are available

            bounds = country_boundary.total_bounds
            # Country statistics
            st.subheader("Country Statistics")
            st.write(f"**Area (km²):** {country_data['Area (km²)']} km²")
            st.write(f"**Density (per km²):** {country_data['Density (per km²)']} people/km²")
            st.write(f"**Growth Rate:** {country_data['Growth Rate']}%")
            st.write(f"**World Population Percentage:** {country_data['World Population Percentage']}%")

            # Map
            st.subheader("Country Map")
            m = folium.Map()
            folium.GeoJson(data=country_boundary).add_to(m)
            m.fit_bounds([
                [bounds[1], bounds[0]],
                [bounds[3], bounds[2]]
            ])

            st_folium(m, width=300, height=300,use_container_width=True)
                
        else:
                st.error("Selected country could not be found in geographical data.")
    
else:
    st.info("Please select a country to view its data.")
