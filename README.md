<img src="https://posgrados-panamericana.up.edu.mx/hs-fs/hubfs/logo%20posgrados%20con%20espacio.png?width=137&name=logo%20posgrados%20con%20espacio.png" width=150>

El objetivo de este tablero es servir como prototipo y guía para el desarrollo del proyecto final de la asignatura.

---

## 🚀 Descripción del Proyecto

El tablero permite visualizar y analizar algunos de los datos que se extrajeron de manera automática del portal EcoBici.

### Objetivos principales:
* **Centralización de datos:** Integración de fuentes de datos mediante un Webscrapper.
* **Visualización interactiva:** Uso de filtros dinámicos para explorar variables clave.
* **Apoyo a la toma de decisiones:** Generación de insights basados en los requerimientos del proyecto final.

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Framework de visualización:** Streamlit
* **Extracción de datos:** Web Scraping (BeautifulSoup / Selenium)
* **Manipulación de datos:** Pandas, NumPy
* **Visualización:** Plotly / Matplotlib

---

## 📁 Estructura del Repositorio

```
Tablero_BI_2026/
│
├── app.py                  # Archivo principal de la aplicación Streamlit
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Documentación del repositorio
│
├── data/
│   ├── raw/                # Datos crudos extraídos del portal EcoBici
│   └── processed/          # Datos limpios listos para visualizar
│
├── scrapper/
│   └── ecobici_scrapper.py # Script de extracción de datos
│
└── utils/
    └── helpers.py          # Funciones auxiliares
```

---

## ⚙️ Instrucciones de Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/edavgaun/Tablero_BI_2026.git
cd Tablero_BI_2026
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ▶️ Cómo Correr la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

> 💡 **Nota:** Asegúrate de tener los datos generados en la carpeta `data/processed/` antes de correr el tablero. Si no, ejecuta primero el scrapper:
> ```bash
> python scrapper/ecobici_scrapper.py
> ```

---

## 👩‍🎓 Contexto Académico

Este repositorio fue desarrollado como material de apoyo para la **Especialidad en Business Intelligence** de la **Universidad Panamericana Mixcoac**, como ejemplo base para el desarrollo del proyecto final de la asignatura.
