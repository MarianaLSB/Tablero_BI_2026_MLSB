import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt


class EcobiciViz:

    def render_waffle(self, df):
        bikes_available = max(1, int(df['num_bikes_available'].sum()))
        bikes_disabled  = max(1, int(df['num_bikes_disabled'].sum()))
        docks_available = max(1, int(df['num_docks_available'].sum()))
        docks_disabled  = max(1, int(df['num_docks_disabled'].sum()))

        total      = bikes_available + bikes_disabled + docks_available + docks_disabled
        categorias = ['Bicis disponibles', 'Bicis dañadas', 'Puertos disponibles', 'Puertos dañados']
        valores    = [bikes_available, bikes_disabled, docks_available, docks_disabled]
        colores    = ['#2ecc71', '#e74c3c', '#3498db', '#e67e22']

        celdas = 100
        grilla = []
        for i, v in enumerate(valores):
            grilla += [i] * round(v / total * celdas)
        while len(grilla) < celdas:
            grilla.append(len(valores) - 1)
        grilla = grilla[:celdas]

        fig, ax = plt.subplots(figsize=(4, 4))
        for idx, celda in enumerate(grilla):
            fila = idx // 10
            col  = idx % 10
            ax.add_patch(plt.Rectangle((col, 9 - fila), 0.9, 0.9,
                                        color=colores[celda], alpha=0.4))
            ax.text(col + 0.45, 9 - fila + 0.45, '🚲',
                    ha='center', va='center', fontsize=11)

        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_title('Estado de bicis y puertos', fontsize=12)

        handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colores]
        ax.legend(handles, categorias, loc='upper left',
                  bbox_to_anchor=(0, -0.05), ncol=2, fontsize=8)

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
            size_max=8,
            zoom=zoom_val,
            center={"lat": lat_center, "lon": lon_center},
            height=600,
        )

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
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_dashboard(self, df):
        estaciones = ["Todas"] + sorted(df['name'].unique().tolist())
        seleccion  = st.selectbox("Busca y selecciona una estación:", estaciones)
        nivel_zoom = st.slider("Nivel de zoom", min_value=1, max_value=4, value=1)

        col_mapa, col_waffle = st.columns([2, 1])
        with col_mapa:
            self.render_map(df, seleccion, nivel_zoom)
        with col_waffle:
            self.render_waffle(df)


    def render_top_vacias(self, df):
    st.subheader("🔴 Top 10 estaciones más vacías")
    top = (df[['name', 'num_bikes_available', 'num_docks_available']]
           .sort_values('num_bikes_available')
           .head(10))
    fig = px.bar(
        top,
        x='num_bikes_available',
        y='name',
        orientation='h',
        color='num_bikes_available',
        color_continuous_scale='RdYlGn',
        labels={'num_bikes_available': 'Bicis disponibles', 'name': 'Estación'},
        height=400,
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    def render_tabla(self, df):
        st.subheader("📋 Detalle por estación")
        busqueda = st.text_input("Buscar estación:", "")
        tabla = df[['name', 'num_bikes_available', 'num_bikes_disabled',
                    'num_docks_available', 'num_docks_disabled']].copy()
        tabla.columns = ['Estación', 'Bicis disp.', 'Bicis dañadas',
                         'Puertos disp.', 'Puertos dañados']
        if busqueda:
            tabla = tabla[tabla['Estación'].str.contains(busqueda, case=False)]
        st.dataframe(tabla, use_container_width=True)
