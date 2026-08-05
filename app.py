import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
# Esto debe ser lo primero que se ejecuta en Streamlit
st.set_page_config(
    page_title="Dashboard Musical Latam",
    page_icon="🎶",
    layout="wide", # Para usar todo el ancho de la pantalla
    initial_sidebar_state="expanded"
)

# --- 1. CARGAR LOS DATOS ---
# Usamos st.cache_data para que no recargue el CSV cada vez que interactuamos con la app
@st.cache_data
def load_data():
    # En tu caso real, esto será 'data/dataset.csv'
    # Asegúrate de que la carpeta 'data' exista junto a tu app.py
    df = pd.read_csv("data/dataset.csv") 
    
    # Convertimos la fecha al tipo de dato correcto
    df['Fecha_Mayor_Exito'] = pd.to_datetime(df['Fecha_Mayor_Exito'])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("¡Ups! No encontré el archivo 'data/dataset.csv'. Por favor, asegúrate de que la ruta sea correcta.")
    st.stop() # Detiene la ejecución si no hay datos

# --- 2. TÍTULO Y SUBTÍTULO LLAMATIVOS ---
st.title("🎵 ¡El Ritmo de Latinoamérica! 💃🕺")
st.subheader("Explorando las tendencias de los géneros musicales en los últimos 20 años 🎧✨")
st.markdown("---") # Una línea divisoria para que se vea más ordenado

# --- FILTROS EN LA BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("🎛️ Filtros de Búsqueda")

# Filtro de Género Musical
generos_disponibles = df['Genero_Musical'].unique().tolist()
generos_seleccionados = st.sidebar.multiselect(
    "Selecciona los Géneros Musicales:",
    options=generos_disponibles,
    default=generos_disponibles # Por defecto seleccionamos todos
)

# Filtro de País de Origen
paises_disponibles = df['Pais_Origen'].unique().tolist()
paises_seleccionados = st.sidebar.multiselect(
    "Selecciona los Países de Origen:",
    options=paises_disponibles,
    default=paises_disponibles
)

# Filtro booleano: ¿Ganador de Grammy?
solo_grammys = st.sidebar.checkbox("Mostrar SOLO ganadores de Grammy Latino 🏆")

# --- APLICAR LOS FILTROS AL DATAFRAME ---
df_filtrado = df[
    (df['Genero_Musical'].isin(generos_seleccionados)) &
    (df['Pais_Origen'].isin(paises_seleccionados))
]

if solo_grammys:
    df_filtrado = df_filtrado[df_filtrado['Ganador_Grammy_Latino'] == True]

# --- 3. CHECKBOX PARA VISTA PREVIA DE DATOS ---
if st.checkbox("👀 Mostrar vista previa de los datos filtrados (Primeras 10 filas)"):
    # Mostramos cuántos resultados quedaron después de filtrar
    st.write(f"Se encontraron **{len(df_filtrado)}** artistas/bandas con estos filtros.")
    st.dataframe(df_filtrado.head(10), use_container_width=True)

st.markdown("---")

# Verificamos que el dataframe no esté vacío antes de graficar
if df_filtrado.empty:
    st.warning("⚠️ Los filtros seleccionados no arrojaron ningún resultado. Por favor, intenta con otra combinación.")
else:
    # --- 4 Y 5. GRÁFICOS CON PLOTLY EXPRESS ---

    # Para organizar mejor, usamos 2 columnas en la primera fila de gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Oyentes Mensuales por Artista (Top 15)")
        # Ordenamos los datos para mostrar los que tienen más oyentes primero
        df_top_oyentes = df_filtrado.sort_values(by='Oyentes_Mensuales_Millones', ascending=False).head(15)
        
        # GRÁFICO 1: Gráfico de Barras Horizontales
        fig_barras = px.bar(
            df_top_oyentes,
            x='Oyentes_Mensuales_Millones',
            y='Artista_o_Banda',
            orientation='h', # h para horizontal
            color='Genero_Musical', # Colorea las barras según el género
            hover_data=['Pais_Origen', 'Canciones_Top_10'],
            labels={'Oyentes_Mensuales_Millones': 'Millones de Oyentes', 'Artista_o_Banda': 'Artista/Banda'}
        )
        # Ordenamos el eje Y para que el mayor quede arriba
        fig_barras.update_layout(yaxis={'categoryorder':'total ascending'}) 
        st.plotly_chart(fig_barras, use_container_width=True)

    with col2:
        st.markdown("### 🍩 Distribución por País de Origen")
        # Calculamos cuántos artistas hay por cada país en los datos filtrados
        conteo_paises = df_filtrado['Pais_Origen'].value_counts().reset_index()
        conteo_paises.columns = ['Pais_Origen', 'Cantidad']

        # GRÁFICO 2: Gráfico Circular tipo "Donut"
        fig_pastel = px.pie(
            conteo_paises,
            values='Cantidad',
            names='Pais_Origen',
            hole=0.4, # El "agujero" en el medio lo hace un donut chart
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # Escondemos el texto si es muy pequeño y mostramos el porcentaje
        fig_pastel.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pastel, use_container_width=True)

    # El histograma lo ponemos abajo para que ocupe todo el ancho
    st.markdown("### 📈 Distribución de Canciones en el Top 10")
    
    # GRÁFICO 3: Histograma
    fig_hist = px.histogram(
        df_filtrado,
        x='Canciones_Top_10',
        nbins=15, # Número de 'cajas' en el histograma
        color='Gira_Internacional_Activa', # Ver si están de gira afecta la distribución
        barmode='group', # Pone las barras una al lado de la otra
        labels={'Canciones_Top_10': 'Cantidad de Canciones en el Top 10', 'count': 'Número de Artistas'},
        color_discrete_map={True: '#00cc96', False: '#ef553b'} # Colores personalizados para True/False
    )
    # Renombrar leyenda para que sea más clara
    fig_hist.update_layout(legend_title_text='¿Gira Activa?') 
    st.plotly_chart(fig_hist, use_container_width=True)

st.caption("Hecho con ❤️, Streamlit y Pandas.")