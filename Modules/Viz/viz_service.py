import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
from pywaffle import Waffle


class EcobiciViz:

    def render_waffle(self, df):
        bikes_available  = int(df['num_bikes_available'].sum())
        bikes_disabled   = int(df['num_bikes_disabled'].sum())
        docks_available  = int(df['num_docks_available'].sum())
        docks_disabled   = int(df['num_docks_disabled'].sum())

        fig = plt.figure(
            FigureClass=Waffle,
            rows=10,
            values={
                'Bicis disponibles' : bikes_available,
                'Bicis dañadas'     : bikes_disabled,
                'Puertos disponibles': docks_available,
                'Puertos dañados'   : docks_disabled,
            },
            colors=['#2ecc71', '#e74c3c', '#3498db', '#e67e22'],
            icons='bicycle',
            icon_size=14,
            icon_legend=True,
            legend={
                'loc'           : 'upper left',
                'bbox_to_anchor': (0, -0.1),
                'ncol'          : 2,
                'fontsize'      : 9,
            },
            figsize=(6, 6),
            title={
                'label'   : 'Estado de bicis y puertos',
                'loc'     : 'center',
                'fontsize': 13,
            }
        )
        st.pyplot(fig)
        plt.close(fig)

    def render_map(self, df):
        st.subheader("Mapa de Estaciones EcoBici")

        # 1. Lista desplegable para resaltar estación
        estaciones = ["Todas"] + sorted(df['name'].unique().tolist())
        seleccion = st.selectbox("Busca y selecciona una estación para resaltarla:", estaciones)

        # 2. Slider de zoom (4 niveles, por defecto nivel 1 = sin zoom)
        nivel_zoom = st.slider("Nivel de zoom", min_value=1, max_value=4, value=1)
        zoom_map = {1: 11, 2: 13, 3: 15, 4: 17}
        zoom_val = zoom_map[nivel_zoom]

        # 3. Centro del mapa: centroide siempre, solo se acerca si hay slider > 1 y hay selección
        if seleccion != "Todas":
            df['resultado'] = df['name'].apply(lambda x: 'Seleccionada' if x == seleccion else 'Normal')
            color_map = {"Seleccionada": "#FF4B4B", "Normal": "#1f7fb4"}
            punto = df[df['name'] == seleccion].iloc[0]
            if nivel_zoom > 1:
                lat_center = punto['lat']
                lon_center = punto['lon']
            else:
                lat_center = df['lat'].mean()
                lon_center = df['lon'].mean()
        else:
            df['resultado'] = 'Normal'
            color_map = {"Seleccionada": "#FF4B4B", "Normal": "#1f7fb4"}
            lat_center = df['lat'].mean()
            lon_center = df['lon'].mean()

        # 4. Creación del mapa interactivo con círculos más grandes
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
            color="resultado",
            color_discrete_map=color_map,
            size_max=18,
            zoom=zoom_val,
            center={"lat": lat_center, "lon": lon_center},
            height=600
        )

        # Aumentar tamaño de los círculos
        fig.update_traces(marker=dict(size=12))

        # 5. Marcador especial para la estación seleccionada
        if seleccion != "Todas":
            punto = df[df['name'] == seleccion].iloc[0]
            fig.add_trace(go.Scattermapbox(
                lat=[punto['lat']],
                lon=[punto['lon']],
                mode='markers+text',
                marker=dict(size=20, color='#FF4B4B', symbol='star'),
                text=[seleccion],
                textposition='top right',
                name='Estación seleccionada'
            ))

        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)

    def render_dashboard(self, df):
        col_mapa, col_waffle = st.columns([2, 1])
        with col_mapa:
            self.render_map(df)
        with col_waffle:
            self.render_waffle(df)
