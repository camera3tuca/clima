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
    page_title="Weather Pro",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Inteligente (Adapta ao Modo Escuro/Claro) ---
st.markdown("""
<style>
    /* Ajusta o fundo dos cartões para usar a cor secundária do tema atual */
    .metric-card-container {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--secondary-background-color);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        color: var(--text-color);
        height: 100%;
    }
    
    /* Remove padding excessivo do topo */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Melhora a visualização das abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Funções Auxiliares ---

def deg_to_compass(num):
    """Converte graus de vento para direção cardeal"""
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
    return {'latitude': -16.6869, 'longitude': -49.2648, 'city': 'Goiânia', 'region': 'Goiás', 'country_name': 'Brasil'}

@st.cache_data(ttl=3600)
def get_weather_data(lat, lon, api_key):
    """Busca dados da API"""
    base_url = "https://api.openweathermap.org/data/2.5"
    try:
        current = requests.get(f"{base_url}/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pt_br").json()
        forecast = requests.get(f"{base_url}/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pt_br").json()
        return current, forecast
    except:
        return None, None

def process_forecast_data(forecast_data):
    """Processa DataFrame"""
    if not forecast_data or 'list' not in forecast_data:
        return pd.DataFrame()
        
    data = []
    for item in forecast_data['list']:
        dt = pd.to_datetime(item['dt'], unit='s')
        data.append({
            'Data': dt,
            'Dia': dt.strftime('%d/%m'),
            'Temp (°C)': item['main']['temp'],
            'Min (°C)': item['main']['temp_min'],
            'Max (°C)': item['main']['temp_max'],
            'Umidade (%)': item['main']['humidity'],
            'Vento (m/s)': item['wind']['speed'],
            'Chuva (mm)': item.get('rain', {}).get('3h', 0)
        })
    return pd.DataFrame(data)

def card_metric(label, value, sub_value):
    """Cria um cartão HTML personalizado"""
    st.markdown(f"""
    <div class="metric-card-container">
        <div style="font-size: 0.9rem; margin-bottom: 5px; opacity: 0.8;">{label}</div>
        <div style="font-size: 1.8rem; font-weight: bold;">{value}</div>
        <div style="font-size: 0.8rem; margin-top: 5px; opacity: 0.8; color: #2ecc71;">{sub_value}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Interface Principal ---

# Sidebar
st.sidebar.title("⚙️ Configurações")
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")

if not OPENWEATHER_API_KEY:
    st.error("⚠️ Configure a chave OPENWEATHER_API_KEY nos secrets.")
    st.stop()

user_loc = get_user_location()
default_city = f"{user_loc.get('city')}, {user_loc.get('region')}"
city_input = st.sidebar.text_input("📍 Cidade:", value=default_city)

try:
    geolocator = Nominatim(user_agent="weather_pro_app")
    location = geolocator.geocode(city_input)
    if location:
        lat, lon = location.latitude, location.longitude
        display_name = location.address.split(',')[0]
        st.sidebar.success(f"✅ {display_name}")
    else:
        st.sidebar.warning("Usando padrão")
        lat, lon = user_loc['latitude'], user_loc['longitude']
        display_name = user_loc.get('city')
except:
    lat, lon = user_loc['latitude'], user_loc['longitude']
    display_name = user_loc.get('city')

# Corpo Principal
st.title(f"🌦️ {display_name}")

current, forecast_raw = get_weather_data(lat, lon, OPENWEATHER_API_KEY)

if current and current.get('cod') == 200:
    # Métricas Superiores (Custom Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card_metric("Temperatura", f"{current['main']['temp']:.1f}°C", f"Sensação: {current['main']['feels_like']:.0f}°C")
    with c2:
        wind_dir = deg_to_compass(current['wind']['deg'])
        card_metric("Vento", f"{current['wind']['speed']} m/s", f"Direção: {wind_dir}")
    with c3:
        card_metric("Umidade", f"{current['main']['humidity']}%", f"Pressão: {current['main']['pressure']}hPa")
    with c4:
        vis = current.get('visibility', 0) / 1000
        card_metric("Visibilidade", f"{vis:.1f} km", f"Nuvens: {current['clouds']['all']}%")

    st.markdown("---")

    # Abas
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗺️ Mapa", "📋 Dados"])

    df = process_forecast_data(forecast_raw)

    with tab1:
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("🌡️ Temperatura (24h)")
            if not df.empty:
                df_24h = df.head(8)
                fig_temp = px.line(df_24h, x='Data', y='Temp (°C)', markers=True, template="plotly_white")
                fig_temp.update_traces(line_color='#FF6B6B', line_width=3)
                fig_temp.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300)
                # Correção do aviso de log: width="stretch" (se suportado) ou nativo
                st.plotly_chart(fig_temp, use_container_width=True) 

        with col_right:
            st.subheader("🌧️ Chuva e Umidade")
            if not df.empty:
                fig_mix = go.Figure()
                fig_mix.add_trace(go.Bar(x=df.head(8)['Data'], y=df.head(8)['Chuva (mm)'], name='Chuva', marker_color='#4A90E2'))
                fig_mix.add_trace(go.Scatter(x=df.head(8)['Data'], y=df.head(8)['Umidade (%)'], name='Umidade', yaxis='y2', line=dict(color='#2ecc71')))
                
                fig_mix.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300,
                    yaxis2=dict(overlaying='y', side='right', showgrid=False),
                    template="plotly_white",
                    legend=dict(orientation="h", y=1.1)
                )
                st.plotly_chart(fig_mix, use_container_width=True)

    with tab2:
        st.subheader("📍 Geolocalização")
        # Mapa ajustado
        m = folium.Map(location=[lat, lon], zoom_start=11, tiles="CartoDB positron")
        folium.Marker(
            [lat, lon], 
            popup=f"<b>{display_name}</b>", 
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        # Ajuste de layout para o mapa não ficar comprimido
        st_folium(m, height=400, use_container_width=True)

    with tab3:
        st.subheader("Base de Dados (5 Dias)")
        # Correção do aviso: width="stretch" para dataframe (nova sintaxe Streamlit)
        try:
            st.dataframe(df, use_container_width=True) 
        except:
             # Fallback caso a versão do streamlit não aceite o novo parametro ainda
            st.dataframe(df)
            
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar CSV", csv, "weather_data.csv", "text/csv")

else:
    st.error("Não foi possível carregar os dados. Verifique a API Key.")

# Footer Minimalista
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Weather Analytics Pro • v2.1</div>", unsafe_allow_html=True)
