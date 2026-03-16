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
        st.info("El color representa el % de ocupación (Azul = Lleno, Rojo = Vacío).")

        # Calcular disponibilidad %
        df['total_cap'] = df['num_bikes_available'] + df['num_docks_available']
        df['disponibilidad_pct'] = (df['num_bikes_available'] / df['total_cap']).fillna(0) * 100

        # 1. Lista desplegable para resaltar estación
        estaciones = ["Todas"] + sorted(df['name'].unique().tolist())
        seleccion = st.selectbox("Busca y selecciona una estación para resaltarla:", estaciones)

        # 2. Slider de zoom
        nivel_zoom = st.slider("Nivel de zoom", min_value=1, max_value=4, value=1)
        zoom_map = {1: 11, 2: 13, 3: 15, 4: 17}
        zoom_val = zoom_map[nivel_zoom]

        # 3. Centro del mapa y tamaño de markers
        if seleccion != "Todas":
            punto = df[df['name'] == seleccion].iloc[0]
            df['tamano_marker'] = df['name'].apply(lambda x: 25 if x == seleccion else 10)
            lat_center = punto['lat'] if nivel_zoom > 1 else df['lat'].mean()
            lon_center = punto['lon'] if nivel_zoom > 1 else df['lon'].mean()
        else:
            df['tamano_marker'] = 10
            lat_center = df['lat'].mean()
            lon_center = df['lon'].mean()

        # 4. Mapa con color por disponibilidad
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
                "disponibilidad_pct": ":.1f",
                "tamano_marker": False,
            },
            color="disponibilidad_pct",
            color_continuous_scale="RdYlBu",
            size="tamano_marker",
            size_max=18,
            zoom=zoom_val,
            center={"lat": lat_center, "lon": lon_center},
            height=600,
            labels={"disponibilidad_pct": "% Bicis"}
        )

        # 5. Marcador estrella para estación seleccionada
        if seleccion != "Todas":
            fig.add_trace(go.Scattermapbox(
                lat=[punto['lat']],
                lon=[punto['lon']],
                mode='markers+text',
                marker=dict(size=20, color='#FF4B4B', symbol='star'),
                text=[seleccion],
                textposition='top right',
                name='Estación seleccionada'
            ))

        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(title="% Llenado")
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_dashboard(self, df):
        col_mapa, col_waffle = st.columns([2, 1])
        with col_mapa:
            self.render_map(df)
        with col_waffle:
            self.render_waffle(df)
