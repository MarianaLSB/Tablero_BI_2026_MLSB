# Sección de importación de módulos
from Modules.UI.header import show_header
from Modules.DATA.ecobici_service import EcobiciService

# Sección para crear la GUI
show_header("Mi primera GUI en Streamlit")

st.write(EcobiciService())
