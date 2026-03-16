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
            characters='🚲',
            font_size=14,
            icon_legend=True,
            legend={
                'loc'           : 'upper left',
                'bbox_to_anchor': (0, -0.1),
                'ncol'          : 2,
                'fontsize'      : 9,
            },
            figsize=(4, 4),
            title={
                'label'   : 'Estado de bicis y puertos',
                'loc'     : 'center',
                'fontsize': 13,
            }
        )
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    def render_map(self, df, seleccion, nivel_zoom):
        st.subheader("Mapa de Estaciones EcoBici")

        zoom_map = {1: 11, 2: 13, 3: 15, 4: 17}
        zoom_val = zoom_map[nivel_zoom]

        if seleccion != "Todas":
            punto = df[df['name'] == seleccion].iloc[0]
            df['resultado'] = df['name'].apply(lambda x: 'Seleccionada' if x == seleccion else 'Normal')
            color_map = {"Seleccionada": "#FF4B4B", "Normal": "#1f7fb4"}
            df['tamano_marker'] = df['name'].apply(lambda x: 25 if x == seleccion else 10)
            lat_center = punto['lat'] if nivel_zoom > 1 else df['lat'].mean()
            lon_center = punto['lon'] if nivel_zoom > 1 else df['lon'].mean()
        else:
            df['resultado'] = 'Normal'
            color_map = {"Normal": "#1f7fb4"}
            df['tamano_marker'] = 10
            lat_center = df['lat'].mean()
            lon_center = df['lon'].mean()

        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data={
                "lat": False,
                "lon": False,
                "num_bikes_available": True,
                "num_bikes_disabled": True,
                "num_docks_available": True,
                "num_docks_disabled": True,
                "resultado": False,
                "tamano_marker": False,
            },
            color="resultado",
            color_discrete_map=color_map,
            size="tamano_marker",
            size_max= 6,
            zoom=zoom_val,
            center={"lat": lat_center, "lon": lon_center},
            height=600,
        )

        if seleccion != "Todas":
            fig.add_trace(go.Scattermapbox(
                lat=[punto['lat']],
                lon=[punto['lon']],
                mode='markers+text',
                marker=dict(size=10, color='#FF4B4B', symbol='star'),
                text=[seleccion],
                textposition='top right',
                name='Estación seleccionada'
            ))

        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_dashboard(self, df):
        # Widgets FUERA de las columnas
        estaciones = ["Todas"] + sorted(df['name'].unique().tolist())
        seleccion = st.selectbox("Busca y selecciona una estación:", estaciones)
        nivel_zoom = st.slider("Nivel de zoom", min_value=1, max_value=4, value=1)

        # Layout de dos columnas
        col_mapa, col_waffle = st.columns([2, 1])
        with col_mapa:
            self.render_map(df, seleccion, nivel_zoom)
        with col_waffle:
            self.render_waffle(df)
