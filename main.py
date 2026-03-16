# Sección de importación de módulos
from Modules.UI.header import show_header
from Modules.Data.ecobici_service import EcobiciService
from Modules.Viz.viz_service import EcobiciViz
import streamlit as st
import pandas as pd

st.cache_data.clear()  

# Sección para crear la GUI
show_header("Mi primera GUI en Streamlit")

ecobici = EcobiciService()
# Cargar datos
df = ecobici.get_full_data()
st.write(df[['num_bikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled']].describe())

# Visualización con Plotly
viz = EcobiciViz()
viz.render_dashboard(df)
