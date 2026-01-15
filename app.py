import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from geopy.geocoders import Nominatim
import warnings
warnings.filterwarnings('ignore')

# Função para obter localização por IP
@st.cache_data(ttl=3600)
def get_user_location():
    """Obtém localização do usuário através do IP"""
    try:
        # Tenta com API ipapi.co (mais confiável e gratuita)
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        
        if 'latitude' in data and 'longitude' in data:
            return {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'city': data.get('city', 'Desconhecido'),
                'region': data.get('region', ''),
                'country': data.get('country_name', ''),
                'success': True
            }
    except Exception as e:
        print(f"Erro ipapi.co: {e}")
    
    # Fallback para ipinfo.io
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        data = response.json()
        
        if 'loc' in data:
            lat, lon = data['loc'].split(',')
            return {
                'latitude': float(lat),
                'longitude': float(lon),
                'city': data.get('city', 'Desconhecido'),
                'region': data.get('region', ''),
                'country': data.get('country', ''),
                'success': True
            }
    except Exception as e:
        print(f"Erro ipinfo.io: {e}")
    
    # Fallback para localização padrão
    return {
        'latitude': -15.8942,
        'longitude': -48.9293,
        'city': 'Goiânia',
        'region': 'Goiás',
        'country': 'Brasil',
        'success': False
    }

# Configuração da página
st.set_page_config(
    page_title="Weather Analytics",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌦️ Weather Analytics Dashboard")
st.markdown("Análise completa de temperatura e precipitação com histórico comparativo")

# API Configuration
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
if not OPENWEATHER_API_KEY:
    st.error("⚠️ Configure a chave OPENWEATHER_API_KEY nos secrets do Streamlit")
    st.stop()

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")

# Obter localização automática
user_location = get_user_location()

# Seleção de local
st.sidebar.subheader("📍 Localização")

if user_location['success']:
    default_location = f"{user_location['city']}, {user_location['region']}, {user_location['country']}"
    st.sidebar.success(f"✅ Localização detectada: {default_location}")
else:
    default_location = "Goiânia, Goiás, Brasil"
    st.sidebar.info("ℹ️ Usando localização padrão (Goiânia)")

location_input = st.sidebar.text_input("Buscar outra cidade:", value=default_location)

try:
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(location_input)
    
    if location:
        latitude = location.latitude
        longitude = location.longitude
        city_name = location.address.split(',')[0]
        st.sidebar.success(f"✅ {city_name} selecionado")
    else:
        st.sidebar.error("Localização não encontrada")
        latitude, longitude, city_name = user_location['latitude'], user_location['longitude'], user_location['city']
except:
    st.sidebar.warning("Usando localização anterior")
    latitude, longitude, city_name = user_location['latitude'], user_location['longitude'], user_location['city']

# Período de análise
st.sidebar.subheader("📅 Período")
days_back = st.sidebar.slider("Dias para análise histórica:", 1, 30, 7)

# Tipo de gráfico
st.sidebar.subheader("📊 Visualização")
chart_type = st.sidebar.selectbox("Tipo de gráfico:", 
    ["Temperatura", "Precipitação", "Comparativo", "Análise Semanal"])

# Funções de API
@st.cache_data(ttl=3600)
def get_current_weather(lat, lon):
    """Busca clima atual"""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Verifica se a resposta contém erro
        if 'cod' in data and data['cod'] != '200' and data['cod'] != 200:
            st.error(f"❌ Erro da API: {data.get('message', 'Erro desconhecido')}")
            return None
        
        # Verifica se contém dados necessários
        if 'main' not in data or 'weather' not in data:
            st.error("❌ Resposta inválida da API")
            return None
            
        return data
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erro HTTP: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao buscar clima: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_forecast_weather(lat, lon):
    """Busca previsão de 5 dias"""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Verifica se a resposta contém erro
        if 'cod' in data and data['cod'] != '200' and data['cod'] != 200:
            st.error(f"❌ Erro da API: {data.get('message', 'Erro desconhecido')}")
            return None
        
        # Verifica se contém dados necessários
        if 'list' not in data:
            st.error("❌ Resposta inválida da API")
            return None
            
        return data
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erro HTTP: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao buscar previsão: {str(e)}")
        return None

def create_forecast_dataframe(forecast_data):
    """Converte dados de previsão em DataFrame"""
    if not forecast_data or 'list' not in forecast_data:
        return None
    
    data = []
    for item in forecast_data['list']:
        data.append({
            'datetime': pd.to_datetime(item['dt'], unit='s'),
            'temp': item['main']['temp'],
            'temp_max': item['main']['temp_max'],
            'temp_min': item['main']['temp_min'],
            'feels_like': item['main']['feels_like'],
            'humidity': item['main']['humidity'],
            'pressure': item['main']['pressure'],
            'clouds': item['clouds']['all'],
            'wind_speed': item['wind']['speed'],
            'description': item['weather'][0]['description'],
            'rain': item.get('rain', {}).get('3h', 0)
        })
    
    df = pd.DataFrame(data)
    df['date'] = df['datetime'].dt.date
    return df

# Página principal
col1, col2, col3 = st.columns(3)

# Busca dados atuais
current = get_current_weather(latitude, longitude)
forecast = get_forecast_weather(latitude, longitude)
df_forecast = create_forecast_dataframe(forecast)

# Validação dos dados
if current is None:
    st.error("❌ Não foi possível carregar os dados do clima. Verifique:")
    st.info("""
    - A chave OPENWEATHER_API_KEY está corretamente configurada?
    - A localização está correta?
    - Você tem plano ativo na OpenWeatherMap?
    """)
    st.stop()

if current:
    with col1:
        st.metric("🌡️ Temperatura Atual", f"{current['main']['temp']:.1f}°C", 
                  f"Sensação: {current['main']['feels_like']:.1f}°C")
    
    with col2:
        st.metric("💧 Umidade", f"{current['main']['humidity']}%")
    
    with col3:
        st.metric("💨 Vento", f"{current['wind']['speed']:.1f} m/s")

# Dados gerais
if current:
    st.markdown(f"### 📍 {city_name}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Clima Atual:**
        - Descrição: {current['weather'][0]['description'].capitalize()}
        - Máxima: {current['main']['temp_max']:.1f}°C
        - Mínima: {current['main']['temp_min']:.1f}°C
        - Pressão: {current['main']['pressure']} hPa
        """)
    
    with col2:
        sunrise = datetime.fromtimestamp(current['sys']['sunrise'])
        sunset = datetime.fromtimestamp(current['sys']['sunset'])
        st.info(f"""
        **Sol e Lua:**
        - Nascer: {sunrise.strftime('%H:%M')}
        - Pôr: {sunset.strftime('%H:%M')}
        - Visibilidade: {current.get('visibility', 0)/1000:.1f} km
        - Cobertura: {current['clouds']['all']}%
        """)

# Gráficos
st.markdown("---")
st.markdown("## 📊 Análises Gráficas")

if df_forecast is not None:
    if chart_type == "Temperatura":
        st.subheader("📈 Evolução de Temperatura (5 dias)")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(df_forecast['datetime'], df_forecast['temp'], 'o-', 
                label='Temperatura', color='#FF6B6B', linewidth=2, markersize=6)
        ax.fill_between(df_forecast['datetime'], df_forecast['temp_min'], 
                         df_forecast['temp_max'], alpha=0.2, color='#FF6B6B')
        ax.set_xlabel('Data/Hora', fontsize=12)
        ax.set_ylabel('Temperatura (°C)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Estatísticas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temp Máxima", f"{df_forecast['temp_max'].max():.1f}°C")
        col2.metric("Temp Mínima", f"{df_forecast['temp_min'].min():.1f}°C")
        col3.metric("Temp Média", f"{df_forecast['temp'].mean():.1f}°C")
        col4.metric("Variação", f"{df_forecast['temp_max'].max() - df_forecast['temp_min'].min():.1f}°C")
    
    elif chart_type == "Precipitação":
        st.subheader("🌧️ Previsão de Chuva (5 dias)")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.bar(df_forecast['datetime'], df_forecast['rain'], 
               color='#4A90E2', alpha=0.7, width=0.08)
        ax.set_xlabel('Data/Hora', fontsize=12)
        ax.set_ylabel('Chuva (mm/3h)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        col1.metric("Chuva Máxima", f"{df_forecast['rain'].max():.1f} mm")
        col2.metric("Chuva Total", f"{df_forecast['rain'].sum():.1f} mm")
        col3.metric("Dias com Chuva", len(df_forecast[df_forecast['rain'] > 0]))
    
    elif chart_type == "Comparativo":
        st.subheader("📊 Gráfico Comparativo: Temperatura vs Chuva")
        
        fig, ax1 = plt.subplots(figsize=(14, 6))
        
        ax1.plot(df_forecast['datetime'], df_forecast['temp'], 'o-', 
                color='#FF6B6B', label='Temperatura', linewidth=2, markersize=6)
        ax1.set_ylabel('Temperatura (°C)', fontsize=12, color='#FF6B6B')
        ax1.tick_params(axis='y', labelcolor='#FF6B6B')
        ax1.grid(True, alpha=0.3)
        
        ax2 = ax1.twinx()
        ax2.bar(df_forecast['datetime'], df_forecast['rain'], 
               alpha=0.3, color='#4A90E2', label='Precipitação', width=0.08)
        ax2.set_ylabel('Chuva (mm/3h)', fontsize=12, color='#4A90E2')
        ax2.tick_params(axis='y', labelcolor='#4A90E2')
        
        ax1.set_xlabel('Data/Hora', fontsize=12)
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    elif chart_type == "Análise Semanal":
        st.subheader("📅 Análise Semanal")
        
        # Agrupa por dia
        df_daily = df_forecast.groupby('date').agg({
            'temp': 'mean',
            'temp_max': 'max',
            'temp_min': 'min',
            'rain': 'sum',
            'humidity': 'mean',
            'wind_speed': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌡️ Temperatura Diária")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(range(len(df_daily)), df_daily['temp'], alpha=0.7, color='#FF6B6B', label='Média')
            ax.plot(range(len(df_daily)), df_daily['temp_max'], 'ro-', label='Máxima', linewidth=2)
            ax.plot(range(len(df_daily)), df_daily['temp_min'], 'bs-', label='Mínima', linewidth=2)
            ax.set_xticks(range(len(df_daily)))
            ax.set_xticklabels([d.strftime('%d/%m') for d in df_daily['date']], rotation=45)
            ax.set_ylabel('Temperatura (°C)', fontsize=11)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.markdown("### 🌧️ Chuva Acumulada")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(range(len(df_daily)), df_daily['rain'], alpha=0.7, color='#4A90E2')
            ax.set_xticks(range(len(df_daily)))
            ax.set_xticklabels([d.strftime('%d/%m') for d in df_daily['date']], rotation=45)
            ax.set_ylabel('Chuva (mm)', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig)
        
        # Tabela semanal
        st.markdown("### 📋 Resumo Semanal")
        df_display = df_daily.copy()
        df_display['date'] = df_display['date'].astype(str)
        df_display.columns = ['Data', 'Temp Média (°C)', 'Temp Máx (°C)', 
                              'Temp Mín (°C)', 'Chuva (mm)', 'Umidade (%)', 'Vento (m/s)']
        st.dataframe(df_display.round(1), use_container_width=True)

# Dados brutos
st.markdown("---")
st.subheader("📊 Dados Brutos da Previsão")

if df_forecast is not None:
    df_display = df_forecast[['datetime', 'temp', 'temp_max', 'temp_min', 
                               'humidity', 'wind_speed', 'rain', 'description']].copy()
    df_display.columns = ['Data/Hora', 'Temp (°C)', 'Máx (°C)', 'Mín (°C)', 
                          'Umidade (%)', 'Vento (m/s)', 'Chuva (mm)', 'Descrição']
    
    st.dataframe(df_display.round(1), use_container_width=True)
    
    # Download
    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button("📥 Baixar dados em CSV", csv, "weather_data.csv", "text/csv")

st.markdown("---")
st.markdown("🌍 Weather Analytics Dashboard | Atualizado em: " + datetime.now().strftime('%d/%m/%Y %H:%M'))
