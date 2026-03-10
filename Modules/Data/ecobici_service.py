import requests
import pandas as pd
import numpy as np


class EcobiciService:

    URL_STATION_INFO   = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_information.json"
    URL_STATION_STATUS = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_status.json"

    def get_full_data(self) -> pd.DataFrame:
        # Información de estaciones
        response_stations = requests.get(self.URL_STATION_INFO)
        data_stations = response_stations.json()
        df = pd.DataFrame(data_stations['data']['stations'])
        df = df[['station_id', 'name', 'lat', 'lon', 'capacity']]

        # Estado en tiempo real
        response_station_status = requests.get(self.URL_STATION_STATUS)
        station_status = response_station_status.json()
        df_status = pd.DataFrame(station_status['data']['stations'])

        columnas = ['num_bikes_available', 'num_bikes_disabled',
                    'num_docks_available', 'num_docks_disabled']
        df_status = df_status[columnas]

        df = pd.concat([df, df_status], axis=1)

        return df
