import plotly.express as px
import streamlit as st

class EcobiciViz:
    def render_map(self, df):
        st.subheader("Mapa de Estaciones Ecobici")
        
        # 1. Lista desplegable para resaltar estación
        estaciones = ["Todas"] + sorted(df['name'].unique().tolist())
        seleccion = st.selectbox("Busca y selecciona una estación para resaltarla:", estaciones)

        # 2. Configuración dinámica según la selección
        if seleccion != "Todas":
            # Marcamos la seleccionada con un color diferente
            df['resaltado'] = df['name'].apply(lambda x: 'Seleccionada' if x == seleccion else 'Normal')
            color_map = {"Seleccionada": "#FF4B4B", "Normal": "#1f77b4"}
            
            # Obtener coordenadas para centrar el mapa
            punto = df[df['name'] == seleccion].iloc[0]
            lat_center, lon_center = punto['lat'], punto['lon']
            zoom_val = 15
        else:
            df['resaltado'] = 'Normal'
            color_map = {"Normal": "#1f77b4"}
            lat_center, lon_center = 19.4326, -99.1332 # Centro CDMX
            zoom_val = 12

        # 3. Creación del mapa interactivo
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data={
                "lat": False, 
                "lon": False, 
                "capacity": True,
                "num_bikes_available": True
            },
            color="resaltado",
            color_discrete_map=color_map,
            zoom=zoom_val,
            center={"lat": lat_center, "lon": lon_center},
            height=600
        )

        # Estilo visual del mapa
        fig.update_layout(mapbox_style="carto-positron") # Estilo limpio y legible
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
