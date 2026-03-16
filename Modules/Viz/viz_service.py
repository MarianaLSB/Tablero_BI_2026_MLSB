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
    
        total  = bikes_available + bikes_disabled + docks_available + docks_disabled
        celdas = 100
    
        categorias = [
            ('Bicis disp.',     bikes_available, '#2ecc71'),
            ('Bicis dañadas',   bikes_disabled,  '#e74c3c'),
            ('Puertos disp.',   docks_available, '#3498db'),
            ('Puertos dañados', docks_disabled,  '#e67e22'),
        ]
    
        grilla = []
        for nombre, valor, color in categorias:
            grilla += [color] * round(valor / total * celdas)
        while len(grilla) < celdas:
            grilla.append(categorias[-1][2])
        grilla = grilla[:celdas]
    
        filas = ""
        for fila in range(10):
            fila_iconos = ""
            for col in range(10):
                idx = fila * 10 + col
                color = grilla[idx]
                fila_iconos += f'<span style="color:{color}; font-size:20px;">🚲</span>'
            filas += f'<div style="display:flex; gap:2px;">{fila_iconos}</div>'
    
        leyenda = ""
        for nombre, valor, color in categorias:
            leyenda += f'<span style="display:inline-block;width:12px;height:12px;background:{color};border-radius:2px;margin-right:4px;"></span>{nombre} ({valor})&nbsp;&nbsp;'
    
        st.markdown(f"""
        <div style="background:#1e1e1e; padding:15px; border-radius:10px;">
            <p style="color:white; text-align:center; font-weight:bold;">Estado de bicis y puertos</p>
            <div>{filas}</div>
            <br>
            <div style="font-size:12px; color:white;">{leyenda}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_map(self, df, seleccion, nivel_zoom):
        df = df.copy()
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
            df['tamano_marker'] = [10] * len(df)
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
                "num_docks_available": True,
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

    def render_top_vacias(self, df):
        top = (df[['name', 'num_bikes_available']]
               .sort_values('num_bikes_available')
               .head(10)
               .copy())
        st.subheader(f"Top 10 estaciones más vacías ({len(top[top['num_bikes_available']==0])} sin bicis ahorita)")
        top['display'] = top['num_bikes_available'].apply(lambda x: 0.1 if x == 0 else x)
        top['etiqueta'] = top['num_bikes_available'].apply(
            lambda x: '🔴 Vacía' if x == 0 else '🟡 Casi vacía'
        )
        fig = px.bar(
            top,
            x='display',
            y='name',
            orientation='h',
            color='etiqueta',
            color_discrete_map={'🔴 Vacía': '#e74c3c', '🟡 Casi vacía': '#f39c12'},
            labels={'display': 'Bicis disponibles', 'name': 'Estación'},
            height=400,
        )
        fig.update_layout(showlegend=True)
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

    def render_dashboard(self, df):
        estaciones = ["Todas"] + sorted(df['name'].unique().tolist())
        seleccion  = st.selectbox("Busca y selecciona una estación:", estaciones)
        nivel_zoom = st.slider("Nivel de zoom", min_value=1, max_value=4, value=1)

        col_mapa, col_waffle = st.columns([2, 1])
        with col_mapa:
            self.render_map(df, seleccion, nivel_zoom)
        with col_waffle:
            self.render_waffle(df)

        st.divider()
        self.render_top_vacias(df)
        st.divider()
        self.render_tabla(df)
