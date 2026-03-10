# Sección de importación de módulos
from Modules.UI.header import show_header
from Modules.Data.ecobici_service import EcobiciService
import streamlit as st
import pandas as pd

# Sección para crear la GUI
show_header("Mi primera GUI en Streamlit")

ecobici = EcobiciService()
# Cargar datos
df = ecobici.get_full_data()

# Visualzación con Plotly
viz = EcobiciViz()
viz.render_map(df)
