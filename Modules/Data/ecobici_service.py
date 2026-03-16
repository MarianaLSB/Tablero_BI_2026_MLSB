import requests
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def get_full_data():
    try:
        resp_info = requests.get('https://gbfs.mex.lyftbikes.com/gbfs/es/station_information.json')
        data_info = resp_info.json()['data']['stations']
        df_info = pd.DataFrame(data_info)
        df_info = df_info[['station_id', 'name', 'lat', 'lon', 'capacity']]

        resp_status = requests.get('https://gbfs.mex.lyftbikes.com/gbfs/es/station_status.json')
        data_status = resp_status.json()['data']['stations']
        df_status = pd.DataFrame(data_status)

        cols_status = ['station_id', 'num_bikes_available', 'num_bikes_disabled',
                       'num_docks_available', 'num_docks_disabled', 'is_renting']
        df_status = df_status[cols_status]

        df_final = pd.merge(df_info, df_status, on='station_id')

        cols_numericas = ['num_bikes_available', 'num_bikes_disabled',
                          'num_docks_available', 'num_docks_disabled']
        df_final[cols_numericas] = df_final[cols_numericas].clip(lower=0)

        return df_final

    except Exception as e:
        st.error(f"Error al conectar con la API de Ecobici: {e}")
        return pd.DataFrame()


class EcobiciService:
    def get_full_data(self):
        return get_full_data()
