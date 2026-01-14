import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import warnings

warnings.filterwarnings('ignore')

# --- Configuração da Página ---
st.set_page_config(
    page_title="Weather Pro Analytics",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado para Estilo Profissional ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- Funções Auxiliares ---

def deg_to_compass(num):
    """Converte graus de vento para direção cardeal (N, NE, etc)"""
    val = int((num/22.5)+.5)
    arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return arr[(val % 16)]

@st.cache_data(ttl=3600)
def get_user_location():
    """Obtém localização aproximada pelo IP"""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        if 'latitude' in data and 'longitude' in data:
            return data
    except:
        pass
    
    # Fallback
    return {'latitude': -16.6869, 'longitude': -49.2648, 'city': 'Goiânia', 'region': 'Goiás', 'country_name': 'Brasil'}

@st.cache_data(ttl=3600)
def get_weather_data(lat, lon, api_key):
    """Busca dados atuais e previsão em uma única chamada (se possível) ou separadas"""
    base_url = "https://api.openweathermap.org/data/2.5"
    
    try:
        # Clima atual
        current = requests.get(f"{base_url}/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pt_br").json()
        # Previsão
        forecast = requests.get(f"{base_url}/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pt_br").json()
        
        return current, forecast
    except Exception as e:
        return None, None

def process_forecast_data(forecast_data):
    """Processa dados brutos da previsão para DataFrame limpo"""
    if not forecast_data or 'list' not in forecast_data:
        return pd.DataFrame()
        
    data = []
    for item in forecast_data['list']:
        dt = pd.to_datetime(item['dt'], unit='s')
        data.append({
            'Data': dt,
            'Dia': dt.strftime('%d/%m'),
            'Temp (°C)': item['main']['temp'],
            'Sensação (°C)': item['main']['feels_like'],
            'Min (°C)': item['main']['temp_min'],
            'Max (°C)': item['main']['temp_max'],
            'Umidade (%)': item['main']['humidity'],
            'Vento (m/s)': item['wind']['speed'],
            'Direção Vento': item['wind']['deg'],
            'Descrição': item['weather'][0]['description'].title(),
            'Chuva (mm)': item.get('rain', {}).get('3h', 0)
        })
    return pd.DataFrame(data)

# --- Interface Principal ---

# Sidebar
st.sidebar.title("⚙️ Configurações")
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")

if not OPENWEATHER_API_KEY:
    st.error("⚠️ Configure a chave OPENWEATHER_API_KEY nos secrets.")
    st.stop()

# Localização
user_loc = get_user_location()
default_city = f"{user_loc.get('city')}, {user_loc.get('region')}"
city_input = st.sidebar.text_input("📍 Buscar Localização:", value=default_city)

try:
    geolocator = Nominatim(user_agent="weather_pro_app")
    location = geolocator.geocode(city_input)
    
    if location:
        lat, lon = location.latitude, location.longitude
        display_name = location.address.split(',')[0]
        st.sidebar.success(f"✅ {display_name}")
    else:
        st.sidebar.error("Local não encontrado. Usando padrão.")
        lat, lon = user_loc['latitude'], user_loc['longitude']
        display_name = user_loc.get('city')
except:
    lat, lon = user_loc['latitude'], user_loc['longitude']
    display_name = user_loc.get('city')

# --- Corpo Principal ---

st.title(f"🌦️ Weather Analytics: {display_name}")
st.markdown(f"Dashboard profissional de monitoramento climático para **{display_name}**.")

# Buscar Dados
current, forecast_raw = get_weather_data(lat, lon, OPENWEATHER_API_KEY)

if current and current.get('cod') == 200:
    # 1. Cartões de Métricas (Top Row)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Temperatura", f"{current['main']['temp']:.1f}°C", f"Min: {current['main']['temp_min']:.1f}°C")
    with col2:
        wind_dir = deg_to_compass(current['wind']['deg'])
        st.metric("Vento", f"{current['wind']['speed']} m/s", f"Direção: {wind_dir}")
    with col3:
        st.metric("Umidade", f"{current['main']['humidity']}%", f"Pressão: {current['main']['pressure']} hPa")
    with col4:
        vis = current.get('visibility', 0) / 1000
        st.metric("Visibilidade", f"{vis:.1f} km", f"Nuvens: {current['clouds']['all']}%")

    st.markdown("---")

    # 2. Abas para Análise
    tab1, tab2, tab3 = st.tabs(["🗺️ Visão Geral & Mapa", "📈 Previsão Detalhada", "📋 Dados Brutos"])

    df = process_forecast_data(forecast_raw)

    with tab1:
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("Localização Atual")
            # Mapa com Folium
            m = folium.Map(location=[lat, lon], zoom_start=10)
            folium.Marker(
                [lat, lon], 
                popup=f"<b>{display_name}</b><br>{current['weather'][0]['description'].title()}", 
                icon=folium.Icon(color="blue", icon="cloud")
            ).add_to(m)
            st_folium(m, height=350, use_container_width=True)
            
        with c2:
            st.subheader("Resumo Próximas 24h")
            if not df.empty:
                # Pegar apenas as próximas 8 entradas (24h, já que são intervalos de 3h)
                df_24h = df.head(8)
                fig_24h = px.line(df_24h, x='Data', y='Temp (°C)', markers=True, 
                                  title="Tendência de Temperatura (24h)", template="plotly_white")
                fig_24h.update_traces(line_color='#FF6B6B', line_width=3)
                st.plotly_chart(fig_24h, use_container_width=True)

    with tab2:
        st.subheader("Análise de Previsão (5 Dias)")
        
        if not df.empty:
            # Gráfico Combinado: Linha (Temp) e Barra (Chuva)
            fig = go.Figure()
            
            # Adicionar barras de chuva
            fig.add_trace(go.Bar(
                x=df['Data'], 
                y=df['Chuva (mm)'],
                name='Chuva (mm)',
                marker_color='#4A90E2',
                opacity=0.6,
                yaxis='y2'
            ))

            # Adicionar linha de temperatura
            fig.add_trace(go.Scatter(
                x=df['Data'], 
                y=df['Temp (°C)'],
                name='Temperatura (°C)',
                mode='lines+markers',
                line=dict(color='#FF6B6B', width=2)
            ))

            # Layout com dois eixos Y
            fig.update_layout(
                title="Temperatura vs Precipitação",
                yaxis=dict(title="Temperatura (°C)", side="left"),
                yaxis2=dict(title="Chuva (mm)", side="right", overlaying="y", showgrid=False),
                template="plotly_white",
                hovermode="x unified",
                legend=dict(orientation="h", y=1.1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de Vento e Umidade
            col_a, col_b = st.columns(2)
            with col_a:
                fig_hum = px.area(df, x='Data', y='Umidade (%)', title="Variação da Umidade",
                                  color_discrete_sequence=['#2ecc71'])
                st.plotly_chart(fig_hum, use_container_width=True)
            
            with col_b:
                fig_wind = px.line(df, x='Data', y='Vento (m/s)', title="Velocidade do Vento",
                                   color_discrete_sequence=['#9b59b6'])
                st.plotly_chart(fig_wind, use_container_width=True)

    with tab3:
        st.subheader("Base de Dados Completa")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Baixar CSV",
            csv,
            "weather_analytics_pro.csv",
            "text/csv",
            key='download-csv'
        )

else:
    st.error("Erro ao carregar dados. Verifique a localização ou a API Key.")
    
# Footer
st.markdown("---")
st.markdown("Desenvolvido com Streamlit, Plotly e OpenWeatherMap")
