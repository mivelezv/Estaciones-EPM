import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Estaciones de Carga EPM", layout="wide")
st.image('img/Headercm.png', use_container_width=True)



# CONTENEDOR: TÍTULO PRINCIPAL
with st.container(border=True):
    st.markdown("""
        <div style='background-color: white;
                 padding: 15px;
                 border-radius: 10px;
                 border: 2px solid #1DB954;
                 text-align: center;'>
            <h1 style='color: green;'>🔋 Dashboard de Estaciones de Carga EPM</h1>
        </div>
    """, unsafe_allow_html=True)

st.caption('Proyecto Bootcamp Talento Tech -- Análisis de Datos Nivel Explorador -- Aplicación Desarrollada por el Grupo 2 -- Integrantes: \n'
    '\n Mildrey Giovanna Velez Villegas -- mivelezv@unal.edu.co / Juan Camilo Agudelo -- juancamiloagudeloe@gmail.com / Lina María Flórez Arango -- lina.florez.arango16@gmail.com '
    '/ Sara Gutierrez -- sara.19-99@hotmail.com / Santiago Jaramillo -- santiagojaramillo1987@gmail.com'
    ) 

# CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Estaciones_gas_electricas.csv", sep=';', encoding='utf-8', on_bad_lines='skip')

    if 'Latitud' in df.columns and 'Longitud' in df.columns:
        df["Latitud"] = df["Latitud"].astype(str).str.replace(",", ".")
        df["Longitud"] = df["Longitud"].astype(str).str.replace(",", ".")
        df["Latitud"] = pd.to_numeric(df["Latitud"], errors="coerce")
        df["Longitud"] = pd.to_numeric(df["Longitud"], errors="coerce")
    return df

df = cargar_datos()


# CONTENEDOR: FILTROS LATERALES
with st.sidebar.container(border=True):

    st.markdown("""
        <div style="
            background-color: #e9f7ef;
            border: 2px solid #1DB954;
            padding: 15px;
            border-radius: 10px;
            color: #1DB954;
            text-align: center;
            font-weight: bold;
            font-size: 18px;">
            🔍 Filtros de Búsqueda
        </div>
    """, unsafe_allow_html=True)

    ciudades = st.multiselect(" Selecciona ciudad:", sorted(df['Ciudad'].dropna().unique()))
    tipos_estacion = st.multiselect(" Tipo de estación:", sorted(df['Tipo de estacion'].dropna().unique()))
    tipos_carga = st.multiselect(" Tipo de carga:", sorted(df['Tipo de carga'].dropna().unique()))



# APLICAR FILTROS
df_filtrado = df.copy()

if ciudades:
    df_filtrado = df_filtrado[df_filtrado['Ciudad'].isin(ciudades)]

if tipos_estacion:
    df_filtrado = df_filtrado[df_filtrado['Tipo de estacion'].isin(tipos_estacion)]

if tipos_carga:
    df_filtrado = df_filtrado[df_filtrado['Tipo de carga'].isin(tipos_carga)]



# # --- Mapa Interactivo ---
# # # (recomendado al inicio del script, fuera de este bloque)
st.set_page_config(layout="wide")

if "Latitud" in df_filtrado.columns and "Longitud" in df_filtrado.columns:
    df_mapa = df_filtrado.dropna(subset=["Latitud", "Longitud"])

    if not df_mapa.empty:
        # Centro del mapa (promedio de coordenadas)
        centro_lat = df_mapa["Latitud"].mean()
        centro_lon = df_mapa["Longitud"].mean()

        # --- Cálculo de span para "maximizar" la ubicación ---
        lat_min, lat_max = df_mapa["Latitud"].min(), df_mapa["Latitud"].max()
        lon_min, lon_max = df_mapa["Longitud"].min(), df_mapa["Longitud"].max()
        max_span = max(lat_max - lat_min, lon_max - lon_min)

        # Heurística de zoom según qué tan dispersos estén los puntos
        if max_span < 0.01:       # Muy cerca (unas pocas cuadras)
            zoom = 15
        elif max_span < 0.05:     # Barrio / comuna
            zoom = 13
        elif max_span < 0.1:      # Parte de ciudad
            zoom = 12
        elif max_span < 0.5:      # Ciudad completa
            zoom = 10
        elif max_span < 1:        # Área metropolitana
            zoom = 9
        else:                     # Varias ciudades / región
            zoom = 7

        fig_mapa = px.scatter_mapbox(
            df_mapa,
            lat="Latitud",
            lon="Longitud",
            hover_name="Estacion",
            hover_data={"Ciudad": True, "Tipo de estacion": True, "Direccion": True},
            color_discrete_sequence=["#1DB954"],
            zoom=13,                 # ← MÁS ZOOM (ajústalo a 14, 15 o 16)
            size=[11] * len(df_mapa),# ← BOLITA MÁS GRANDE
            size_max=25,             # ← TAMAÑO MÁXIMO
            height=600
        )   

        fig_mapa.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": centro_lat, "lon": centro_lon},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )

        with st.container(border=True):
            st.subheader('Mapa de Estaciones Filtradas')
            st.plotly_chart(fig_mapa, use_container_width=True)

    else:
        st.warning("⚠️ No hay coordenadas válidas para mostrar en el mapa.")
else:
    st.warning("⚠️ No se encontraron registros con los filtros seleccionados.")



# CONTENEDOR: TABLA DE RESULTADOS
with st.container(border=True):
    st.markdown("### Resultados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True, height=600)
    st.write(f"🔎 Registros encontrados: **{len(df_filtrado)}**")  # Taxto inferior de la tablar 


# GRÁFICAS INTERACTIVAS
#st.markdown("## Análisis Visual de Estaciones")
with st.container(border=True):
    st.markdown("""
    <div style='background-color: white;
             padding: 15px;
             border-radius: 10px;
             border: 2px solid #1DB954;
             text-align: center;'>
        <h1 style='color: green;'> Análisis Visual de Estaciones </h1>
    </div>
""", unsafe_allow_html=True)

if not df_filtrado.empty:
    # --- Gráfico 1: Estaciones por Ciudad ---
    with st.container(border=True):
        st.subheader('Distribución de Estaciones por Ciudad')
        fig_ciudad = px.bar(
            df_filtrado.groupby("Ciudad").size().reset_index(name="Cantidad"),
            x="Ciudad",
            y="Cantidad",
            color="Ciudad",
            #title="Distribución de Estaciones por Ciudad"    -- TITULO CHIQUITO DEPENDE LO QUE SE DEFINA CON EL EQUIPO
    )
    with st.container(border=True):
        st.plotly_chart(fig_ciudad, use_container_width=True)

    # --- Gráfico 2: Estaciones por Tipo de Carga ---
with st.container(border=True):
    st.subheader('Proporción por tipo de carga')
    fig_carga = px.pie(
        df_filtrado,
        names="Tipo de carga",
        #title="Proporción por Tipo de Carga",           -- TITULO CHIQUITO DEPENDE LO QUE SE DEFINA CON EL EQUIPO
        hole=0.4
    )
with st.container(border=True):
    st.plotly_chart(fig_carga, use_container_width=True)



st.caption('Cobertura y capacidad de estaciones de EPM - Proyecto equipo 2')